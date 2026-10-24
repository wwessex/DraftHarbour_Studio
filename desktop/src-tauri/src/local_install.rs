//! Verified, staged directory installation. No network, archive extraction or training.
use crate::local_runtime::{self, Manifest};
use std::{fs, path::Path};
const RESERVE: u64 = 256 * 1024 * 1024;
pub const MIN_MEMORY: u64 = 8 * 1024 * 1024 * 1024;
pub struct InstallPlan {
    pub model: String,
    pub bytes: u64,
    pub available: u64,
    pub required: u64,
    pub memory: u64,
}

pub fn resources(
    model: String,
    bytes: u64,
    available: u64,
    memory: u64,
) -> Result<InstallPlan, String> {
    if memory < MIN_MEMORY {
        return Err("This experimental model requires at least 8 GiB of RAM. It has been tested on a 16 GB Mac.".into());
    }
    let required = bytes
        .checked_add(RESERVE)
        .ok_or("Invalid model package size.")?;
    if available < required {
        return Err(
            "Not enough free space to stage this model. The installed package is unchanged.".into(),
        );
    }
    Ok(InstallPlan {
        model,
        bytes,
        available,
        required,
        memory,
    })
}
fn parent(destination: &Path) -> Result<&Path, String> {
    destination
        .parent()
        .ok_or("Invalid local storage directory.".into())
}
fn verify(root: &Path) -> Result<Manifest, String> {
    local_runtime::verify(
        root,
        local_runtime::CATALOG_HASH,
        local_runtime::CATALOG_PLATFORM,
    )
}
pub fn plan(source: &Path, destination: &Path) -> Result<InstallPlan, String> {
    let manifest = verify(source)?;
    let parent = parent(destination)?;
    fs::create_dir_all(parent).map_err(|_| "Unable to create local model storage.")?;
    let source = source
        .canonicalize()
        .map_err(|_| "Model source is missing.")?;
    let canonical_parent = parent
        .canonicalize()
        .map_err(|_| "Local storage is missing.")?;
    if source.starts_with(&canonical_parent) || canonical_parent.starts_with(&source) {
        return Err("Choose a package outside the app's local model storage.".into());
    }
    let bytes = manifest
        .files
        .values()
        .try_fold(0u64, |total, item| total.checked_add(item.bytes))
        .ok_or("Invalid package size.")?
        .checked_add(
            fs::metadata(source.join("manifest.json"))
                .map_err(|_| "Missing model manifest.")?
                .len(),
        )
        .ok_or("Invalid package size.")?;
    let (available, memory) = system_resources(parent)?;
    resources(manifest.model_id, bytes, available, memory)
}
pub fn install(source: &Path, destination: &Path) -> Result<String, String> {
    plan(source, destination)?;
    replace(
        source,
        destination,
        local_runtime::CATALOG_HASH,
        local_runtime::CATALOG_PLATFORM,
        |from, to| fs::rename(from, to),
    )
}
fn replace(
    source: &Path,
    destination: &Path,
    hash: &str,
    platform: &str,
    activate: impl FnOnce(&Path, &Path) -> std::io::Result<()>,
) -> Result<String, String> {
    let manifest = local_runtime::verify(source, hash, platform)?;
    let parent = parent(destination)?;
    let previous = parent.join("previous-bundle");
    let had_active = destination.exists();
    let had_previous = previous.exists();
    if had_active {
        local_runtime::verify(destination, hash, platform)?;
    }
    if had_previous {
        local_runtime::verify(&previous, hash, platform)?;
    }
    let work = tempfile::Builder::new()
        .prefix(".install-")
        .tempdir_in(parent)
        .map_err(|_| "Unable to stage local model.")?;
    let staged = work.path().join("bundle");
    let retired = work.path().join("retired");
    fs::create_dir(&staged).map_err(|_| "Unable to stage local model.")?;
    for name in manifest
        .files
        .keys()
        .map(String::as_str)
        .chain(std::iter::once("manifest.json"))
    {
        let from = local_runtime::safe_file(source, name)?;
        let target = staged.join(name);
        fs::create_dir_all(target.parent().ok_or("Unsafe package file.")?)
            .map_err(|_| "Unable to stage local model.")?;
        fs::copy(from, target)
            .map_err(|_| "Unable to copy local model. Installed files are unchanged.")?;
    }
    local_runtime::verify(&staged, hash, platform)?;
    let result = (|| -> std::io::Result<()> {
        if had_previous {
            fs::rename(&previous, &retired)?;
        }
        if had_active {
            fs::rename(destination, &previous)?;
        }
        activate(&staged, destination)
    })();
    if result.is_err() {
        if !destination.exists() && had_active && previous.exists() {
            let _ = fs::rename(&previous, destination);
        }
        if !previous.exists() && retired.exists() {
            let _ = fs::rename(&retired, &previous);
        }
        if retired.exists() {
            let _ = work.keep();
        }
        return Err("Installation failed. Existing model files were retained; try restoring the previous package.".into());
    }
    Ok(manifest.model_id)
}
pub fn previous_model(destination: &Path) -> Result<String, String> {
    Ok(verify(&parent(destination)?.join("previous-bundle"))?.model_id)
}
pub fn restore(destination: &Path) -> Result<String, String> {
    restore_verified(
        destination,
        local_runtime::CATALOG_HASH,
        local_runtime::CATALOG_PLATFORM,
    )
}
fn restore_verified(destination: &Path, hash: &str, platform: &str) -> Result<String, String> {
    let parent = parent(destination)?;
    let previous = parent.join("previous-bundle");
    let manifest = local_runtime::verify(&previous, hash, platform)?;
    let had_active = destination.exists();
    if had_active {
        local_runtime::verify(destination, hash, platform)?;
    }
    let work = tempfile::Builder::new()
        .prefix(".rollback-")
        .tempdir_in(parent)
        .map_err(|_| "Unable to stage model restore.")?;
    let held = work.path().join("bundle");
    let result = (|| -> std::io::Result<()> {
        if had_active {
            fs::rename(destination, &held)?;
        }
        fs::rename(&previous, destination)?;
        if had_active {
            fs::rename(&held, &previous)?;
        }
        Ok(())
    })();
    if result.is_err() {
        if !destination.exists() && held.exists() {
            let _ = fs::rename(&held, destination);
        }
        if held.exists() {
            let _ = work.keep();
        }
        return Err("Restore failed. Model files were retained for recovery.".into());
    }
    Ok(manifest.model_id)
}

#[cfg(unix)]
fn system_resources(path: &Path) -> Result<(u64, u64), String> {
    use std::{ffi::CString, os::unix::ffi::OsStrExt};
    let path = CString::new(path.as_os_str().as_bytes()).map_err(|_| "Invalid storage path.")?;
    let mut stats = std::mem::MaybeUninit::<libc::statvfs>::uninit();
    // statvfs writes the supplied structure only on a successful return.
    if unsafe { libc::statvfs(path.as_ptr(), stats.as_mut_ptr()) } != 0 {
        return Err("Unable to check available model storage.".into());
    }
    let stats = unsafe { stats.assume_init() };
    let available = (stats.f_bavail as u64)
        .checked_mul(stats.f_frsize as u64)
        .ok_or("Invalid storage capacity.")?;
    #[cfg(target_os = "macos")]
    let memory = {
        let mut value = 0u64;
        let mut size = std::mem::size_of::<u64>();
        if unsafe {
            libc::sysctlbyname(
                c"hw.memsize".as_ptr(),
                (&mut value as *mut u64).cast(),
                &mut size,
                std::ptr::null_mut(),
                0,
            )
        } != 0
        {
            return Err("Unable to check physical memory.".into());
        }
        value
    };
    #[cfg(not(target_os = "macos"))]
    let memory = {
        let pages = unsafe { libc::sysconf(libc::_SC_PHYS_PAGES) };
        let size = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
        if pages <= 0 || size <= 0 {
            return Err("Unable to check physical memory.".into());
        }
        (pages as u64)
            .checked_mul(size as u64)
            .ok_or("Invalid memory capacity.")?
    };
    Ok((available, memory))
}
#[cfg(windows)]
fn system_resources(path: &Path) -> Result<(u64, u64), String> {
    use std::os::windows::ffi::OsStrExt;
    // Win32 MEMORYSTATUSEX layout and Kernel32 APIs, as documented by Microsoft.
    #[repr(C)]
    struct MemoryStatus {
        length: u32,
        load: u32,
        total_phys: u64,
        available_phys: u64,
        total_page: u64,
        available_page: u64,
        total_virtual: u64,
        available_virtual: u64,
        available_extended: u64,
    }
    #[link(name = "kernel32")]
    extern "system" {
        fn GlobalMemoryStatusEx(status: *mut MemoryStatus) -> i32;
        fn GetDiskFreeSpaceExW(
            directory: *const u16,
            available: *mut u64,
            total: *mut u64,
            free: *mut u64,
        ) -> i32;
    }
    let mut memory = MemoryStatus {
        length: std::mem::size_of::<MemoryStatus>() as u32,
        load: 0,
        total_phys: 0,
        available_phys: 0,
        total_page: 0,
        available_page: 0,
        total_virtual: 0,
        available_virtual: 0,
        available_extended: 0,
    };
    let path: Vec<u16> = path
        .as_os_str()
        .encode_wide()
        .chain(std::iter::once(0))
        .collect();
    let mut available = 0;
    if unsafe { GlobalMemoryStatusEx(&mut memory) } == 0
        || unsafe {
            GetDiskFreeSpaceExW(
                path.as_ptr(),
                &mut available,
                std::ptr::null_mut(),
                std::ptr::null_mut(),
            )
        } == 0
    {
        return Err("Unable to check model storage or physical memory.".into());
    }
    Ok((available, memory.total_phys))
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> (tempfile::TempDir, std::path::PathBuf, String, String) {
        let root = tempfile::tempdir().unwrap();
        let source = root.path().join("source");
        fs::create_dir(&source).unwrap();
        fs::write(source.join("model.gguf"), b"verified model").unwrap();
        fs::write(source.join("server"), b"verified executable").unwrap();
        let platform = local_runtime::platform();
        let mut files = serde_json::Map::new();
        for name in ["model.gguf", "server"] {
            let path = source.join(name);
            files.insert(name.into(), serde_json::json!({"bytes":path.metadata().unwrap().len(),"sha256":local_runtime::hash(&path).unwrap()}));
        }
        fs::write(source.join("manifest.json"), serde_json::to_vec(&serde_json::json!({"schema_version":1,"engine":"llama.cpp","platform":platform,"model_id":"test-model","context_limit":4096,"max_output_tokens":512,"model":"model.gguf","executable":"server","files":files})).unwrap()).unwrap();
        let hash = local_runtime::hash(&source.join("manifest.json")).unwrap();
        fs::create_dir(root.path().join("installed")).unwrap();
        (root, source, hash, platform)
    }
    #[test]
    fn install_reinstall_and_restore_verified_copy() {
        let (root, source, hash, platform) = fixture();
        let dest = root.path().join("installed/bundle");
        for _ in 0..2 {
            replace(&source, &dest, &hash, &platform, |from, to| {
                fs::rename(from, to)
            })
            .unwrap();
        }
        assert!(local_runtime::verify(&dest, &hash, &platform).is_ok());
        assert!(local_runtime::verify(
            &dest.parent().unwrap().join("previous-bundle"),
            &hash,
            &platform
        )
        .is_ok());
        restore_verified(&dest, &hash, &platform).unwrap();
        assert!(local_runtime::verify(&dest, &hash, &platform).is_ok());
    }
    #[test]
    fn activation_failure_preserves_working_package() {
        let (root, source, hash, platform) = fixture();
        let dest = root.path().join("installed/bundle");
        replace(&source, &dest, &hash, &platform, |from, to| {
            fs::rename(from, to)
        })
        .unwrap();
        assert!(replace(&source, &dest, &hash, &platform, |_, _| Err(
            std::io::Error::other("simulated promotion failure")
        ))
        .is_err());
        assert!(local_runtime::verify(&dest, &hash, &platform).is_ok());
        assert!(local_runtime::verify(&source, &hash, &platform).is_ok());
    }
    #[test]
    fn tampering_never_replaces_active_or_unknown_previous_files() {
        let (root, source, hash, platform) = fixture();
        let dest = root.path().join("installed/bundle");
        replace(&source, &dest, &hash, &platform, |from, to| {
            fs::rename(from, to)
        })
        .unwrap();
        let previous = dest.parent().unwrap().join("previous-bundle");
        fs::create_dir(&previous).unwrap();
        fs::write(previous.join("keep.txt"), b"unrecognized data").unwrap();
        assert!(
            replace(&source, &dest, &hash, &platform, |from, to| fs::rename(
                from, to
            ))
            .is_err()
        );
        assert_eq!(
            fs::read(previous.join("keep.txt")).unwrap(),
            b"unrecognized data"
        );
        fs::write(source.join("model.gguf"), b"changed").unwrap();
        assert!(
            replace(&source, &dest, &hash, &platform, |from, to| fs::rename(
                from, to
            ))
            .is_err()
        );
        assert!(local_runtime::verify(&dest, &hash, &platform).is_ok());
    }
    #[test]
    fn missing_active_can_recover_from_verified_previous() {
        let (root, source, hash, platform) = fixture();
        let dest = root.path().join("installed/bundle");
        let previous = dest.parent().unwrap().join("previous-bundle");
        fs::rename(source, &previous).unwrap();
        restore_verified(&dest, &hash, &platform).unwrap();
        assert!(local_runtime::verify(&dest, &hash, &platform).is_ok());
    }
    #[test]
    fn resource_shortfalls_are_rejected_without_guessing_capacity() {
        assert!(resources("test".into(), 100, RESERVE + 100, MIN_MEMORY).is_ok());
        assert!(resources("test".into(), 100, RESERVE, MIN_MEMORY).is_err());
        assert!(resources("test".into(), 100, u64::MAX, MIN_MEMORY - 1).is_err());
        let root = tempfile::tempdir().unwrap();
        let (space, memory) = system_resources(root.path()).unwrap();
        assert!(space > 0 && memory > 0);
    }
}

#[cfg(test)]
mod real_smoke {
    use super::*;
    #[test]
    #[ignore = "Explicit real-model install test; never downloads weights"]
    fn real_installation_smoke() {
        let source = std::path::PathBuf::from(
            std::env::var("DRAFTHARBOUR_TEST_BUNDLE")
                .expect("Set verified existing development package"),
        );
        let temporary = tempfile::tempdir().unwrap();
        let destination = temporary.path().join("model-store/bundle");
        let runtime = local_runtime::LocalRuntime::default();
        for _ in 0..2 {
            runtime.install(&source, &destination).unwrap();
        }
        runtime.restore(&destination).unwrap();
        let response = runtime
            .generate(
                &destination,
                "Continue in two sentences: A gull called across the quay.",
            )
            .unwrap();
        assert!(!response.text.trim().is_empty());
        runtime.stop();
        assert!(verify(&destination).is_ok());
        assert!(verify(&destination.parent().unwrap().join("previous-bundle")).is_ok());
    }
}
