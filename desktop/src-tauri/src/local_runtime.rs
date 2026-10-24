//! Private, app-owned inference. No downloads, training, arbitrary URLs or credentials in IPC.
use rand::RngCore;
use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{
    collections::{HashMap, HashSet},
    fs::{self, File},
    io::{Read, Write},
    net::TcpListener,
    path::{Component, Path, PathBuf},
    process::{Child, Command, Stdio},
    sync::{
        atomic::{AtomicBool, Ordering},
        Mutex,
    },
    thread,
    time::{Duration, Instant},
};
use tempfile::TempDir;

const CATALOG_HASH: &str = "bec8fcc53a370b0a19de9cef4a8f4234add5a31feb54dcad56a8b34b260eb4e3";
const CATALOG_PLATFORM: &str = "darwin-arm64";
pub const MODEL: &str = "narratryx-craft-v1-q4-k-m";

#[derive(Deserialize)]
struct FileRecord {
    bytes: u64,
    sha256: String,
}
#[derive(Deserialize)]
pub struct Manifest {
    schema_version: u32,
    engine: String,
    platform: String,
    pub model_id: String,
    context_limit: usize,
    max_output_tokens: usize,
    model: String,
    executable: String,
    files: HashMap<String, FileRecord>,
}

fn platform() -> String {
    let os = if cfg!(target_os = "macos") {
        "darwin"
    } else {
        std::env::consts::OS
    };
    let arch = if cfg!(target_arch = "aarch64") {
        "arm64"
    } else {
        std::env::consts::ARCH
    };
    format!("{os}-{arch}")
}
fn hash(path: &Path) -> Result<String, String> {
    let mut file = File::open(path).map_err(|_| "Local model package file is missing.")?;
    let mut digest = Sha256::new();
    let mut buffer = vec![0; 8 * 1024 * 1024];
    loop {
        let count = file
            .read(&mut buffer)
            .map_err(|_| "Unable to read local model package.")?;
        if count == 0 {
            break;
        }
        digest.update(&buffer[..count]);
    }
    Ok(format!("{:x}", digest.finalize()))
}
fn safe_file(root: &Path, name: &str) -> Result<PathBuf, String> {
    if name.is_empty()
        || name.contains(['\\', ':'])
        || name
            .split('/')
            .any(|s| s.is_empty() || s == "." || s == "..")
    {
        return Err("Unsafe local model package path.".into());
    }
    let mut path = root.to_owned();
    for part in Path::new(name).components() {
        if let Component::Normal(part) = part {
            path.push(part);
        } else {
            return Err("Unsafe local model package path.".into());
        }
        if fs::symlink_metadata(&path)
            .map_err(|_| "Local package file is missing.")?
            .file_type()
            .is_symlink()
        {
            return Err("Linked local package files are not allowed.".into());
        }
    }
    if !path.is_file() {
        return Err("Local model package file is missing.".into());
    }
    Ok(path)
}
fn inventory(root: &Path, directory: &Path, result: &mut HashSet<PathBuf>) -> Result<(), String> {
    for entry in fs::read_dir(directory).map_err(|_| "Unable to inspect local model package.")? {
        let entry = entry.map_err(|_| "Unable to inspect local model package.")?;
        let kind = entry
            .file_type()
            .map_err(|_| "Unable to inspect local model package.")?;
        if kind.is_symlink() {
            return Err("Linked local package files are not allowed.".into());
        }
        if kind.is_dir() {
            inventory(root, &entry.path(), result)?;
        } else if kind.is_file() {
            result.insert(
                entry
                    .path()
                    .strip_prefix(root)
                    .map_err(|_| "Unsafe package path.")?
                    .to_owned(),
            );
        } else {
            return Err("Unsupported local package file.".into());
        }
    }
    Ok(())
}
pub fn verify(
    root: &Path,
    expected_hash: &str,
    expected_platform: &str,
) -> Result<Manifest, String> {
    if expected_platform != platform() {
        return Err("No verified local model package is available for this computer yet.".into());
    }
    let file = safe_file(root, "manifest.json")?;
    if file
        .metadata()
        .map_err(|_| "Missing model manifest.")?
        .len()
        > 1_048_576
        || hash(&file)? != expected_hash
    {
        return Err("Local model manifest verification failed.".into());
    }
    let manifest: Manifest =
        serde_json::from_reader(File::open(file).map_err(|_| "Missing model manifest.")?)
            .map_err(|_| "Invalid local model manifest.")?;
    if manifest.schema_version != 1
        || manifest.engine != "llama.cpp"
        || manifest.platform != expected_platform
        || manifest.model_id.is_empty()
        || manifest.model_id.len() > 128
        || !manifest
            .model_id
            .bytes()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b"._-".contains(&b))
        || !(512..=4096).contains(&manifest.context_limit)
        || !(1..=512).contains(&manifest.max_output_tokens)
        || !manifest.files.contains_key(&manifest.model)
        || !manifest.files.contains_key(&manifest.executable)
    {
        return Err("Unsupported local model package.".into());
    }
    for (name, record) in &manifest.files {
        let path = safe_file(root, name)?;
        if path.metadata().map_err(|_| "Missing model file.")?.len() != record.bytes
            || hash(&path)? != record.sha256
        {
            return Err("Local model file verification failed.".into());
        }
    }
    let mut actual = HashSet::new();
    inventory(root, root, &mut actual)?;
    let mut expected: HashSet<PathBuf> = manifest.files.keys().map(PathBuf::from).collect();
    expected.insert(PathBuf::from("manifest.json"));
    if actual != expected {
        return Err("The local package contains unverified files.".into());
    }
    Ok(manifest)
}
struct Session {
    child: Child,
    _private: TempDir,
    url: String,
    token: String,
}
impl Drop for Session {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}
#[derive(Default)]
pub struct LocalRuntime {
    session: Mutex<Option<Session>>,
    cancelled: AtomicBool,
    busy: AtomicBool,
}
struct BusyGuard<'a>(&'a AtomicBool);
impl Drop for BusyGuard<'_> {
    fn drop(&mut self) {
        self.0.store(false, Ordering::SeqCst);
    }
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct RuntimeReply {
    text: String,
    model: String,
    latency_ms: u128,
}
impl LocalRuntime {
    pub fn inspect(&self, root: &Path) -> Result<String, String> {
        Ok(verify(root, CATALOG_HASH, CATALOG_PLATFORM)?.model_id)
    }
    pub fn stop(&self) {
        self.cancelled.store(true, Ordering::SeqCst);
        if let Ok(mut session) = self.session.lock() {
            session.take();
        }
    }
    fn start(&self, root: &Path, client: &Client) -> Result<(String, String), String> {
        let mut owned = self
            .session
            .lock()
            .map_err(|_| "Local runtime state unavailable.")?;
        if let Some(session) = owned.as_mut() {
            if session
                .child
                .try_wait()
                .map_err(|_| "Unable to check local runtime.")?
                .is_none()
            {
                return Ok((session.url.clone(), session.token.clone()));
            }
        }
        owned.take();
        let manifest = verify(root, CATALOG_HASH, CATALOG_PLATFORM)?;
        if self.cancelled.load(Ordering::SeqCst) {
            return Err("Local AI cancelled.".into());
        }
        let private = tempfile::Builder::new()
            .prefix("draftharbour-local-")
            .tempdir()
            .map_err(|_| "Unable to create private local runtime storage.")?;
        let mut random = [0u8; 32];
        rand::rngs::OsRng
            .try_fill_bytes(&mut random)
            .map_err(|_| "Unable to create private local authentication.")?;
        let token: String = random.iter().map(|b| format!("{b:02x}")).collect();
        let key = private.path().join("access-token");
        let mut options = fs::OpenOptions::new();
        options.create_new(true).write(true);
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            options.mode(0o600);
        }
        options
            .open(&key)
            .and_then(|mut file| writeln!(file, "{token}"))
            .map_err(|_| "Unable to create private local authentication.")?;
        let listener =
            TcpListener::bind("127.0.0.1:0").map_err(|_| "Unable to reserve a local port.")?;
        let port = listener
            .local_addr()
            .map_err(|_| "Unable to reserve a local port.")?
            .port();
        drop(listener);
        let mut command = Command::new(root.join(&manifest.executable));
        command
            .current_dir(root)
            .arg("-m")
            .arg(root.join(&manifest.model))
            .args([
                "--host",
                "127.0.0.1",
                "--port",
                &port.to_string(),
                "--api-key-file",
            ])
            .arg(key)
            .args([
                "--alias",
                &manifest.model_id,
                "--ctx-size",
                &manifest.context_limit.to_string(),
                "--parallel",
                "1",
                "--no-context-shift",
                "--no-webui",
            ])
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::null());
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            command.creation_flags(0x08000000);
        }
        let child = command
            .spawn()
            .map_err(|_| "The verified local runtime could not start.")?;
        let mut session = Session {
            child,
            _private: private,
            token,
            url: format!("http://127.0.0.1:{port}"),
        };
        let started = Instant::now();
        while started.elapsed() < Duration::from_secs(120) {
            if self.cancelled.load(Ordering::SeqCst) {
                return Err("Local AI cancelled.".into());
            }
            if session
                .child
                .try_wait()
                .map_err(|_| "Unable to check local runtime.")?
                .is_some()
            {
                return Err("Local AI exited during startup.".into());
            }
            if let Ok(response) = client
                .get(format!("{}/v1/models", session.url))
                .bearer_auth(&session.token)
                .timeout(Duration::from_secs(2))
                .send()
            {
                if response.status().is_success() {
                    if let Ok(value) = response.json::<Value>() {
                        if value["data"].as_array().is_some_and(|rows| {
                            rows.iter().any(|row| row["id"] == manifest.model_id)
                        }) {
                            let result = (session.url.clone(), session.token.clone());
                            *owned = Some(session);
                            return Ok(result);
                        }
                    }
                }
            }
            thread::sleep(Duration::from_millis(100));
        }
        Err("Local AI startup timed out.".into())
    }
    pub fn generate(&self, root: &Path, prompt: &str) -> Result<RuntimeReply, String> {
        if prompt.trim().is_empty() || prompt.len() > 65_536 {
            return Err("Use a shorter, nonempty passage for Local AI.".into());
        }
        if self.busy.swap(true, Ordering::SeqCst) {
            return Err("Local AI is already generating a draft.".into());
        }
        let _guard = BusyGuard(&self.busy);
        self.cancelled.store(false, Ordering::SeqCst);
        // Tauri enables rustls without its own default crypto provider. Supply an isolated
        // configuration rather than modifying the app-wide provider. Only fixed HTTP
        // loopback URLs are used; redirects and proxies remain disabled.
        let tls = rustls::ClientConfig::builder_with_provider(std::sync::Arc::new(
            rustls::crypto::ring::default_provider(),
        ))
        .with_safe_default_protocol_versions()
        .map_err(|_| "Local connection configuration failed.")?
        .with_root_certificates(rustls::RootCertStore::empty())
        .with_no_client_auth();
        let client = Client::builder()
            .tls_backend_preconfigured(tls)
            .no_proxy()
            .redirect(reqwest::redirect::Policy::none())
            .timeout(Duration::from_secs(125))
            .build()
            .map_err(|_| "Unable to create private local connection.")?;
        let started = Instant::now();
        let (url, token) = self.start(root, &client)?;
        let result = (|| {
            if self.cancelled.load(Ordering::SeqCst) {
                return Err("Local AI cancelled.".into());
            }
            let response = client.post(format!("{url}/v1/chat/completions")).bearer_auth(token).json(&json!({
                "model":MODEL,"messages":[{"role":"user","content":prompt}],"max_tokens":512,
                "stream":false,"temperature":0,"seed":42,"cache_prompt":false,"chat_template_kwargs":{"enable_thinking":false}
            })).send().map_err(|_| "Local AI stopped or could not complete this request.")?;
            if !response.status().is_success() {
                return Err("Local AI could not complete this request. Try a shorter passage or restart Local AI.".into());
            }
            let value: Value = response
                .json()
                .map_err(|_| "Local AI returned an invalid response.")?;
            if self.cancelled.load(Ordering::SeqCst) {
                return Err("Local AI cancelled.".into());
            }
            let text = value["choices"][0]["message"]["content"]
                .as_str()
                .filter(|s| !s.trim().is_empty())
                .ok_or("Local AI returned no draft.")?
                .to_string();
            Ok(RuntimeReply {
                text,
                model: MODEL.into(),
                latency_ms: started.elapsed().as_millis(),
            })
        })();
        if result.is_err() {
            self.stop();
        }
        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> (TempDir, String) {
        let temp = tempfile::tempdir().unwrap();
        fs::write(temp.path().join("model.gguf"), b"model").unwrap();
        fs::write(temp.path().join("server"), b"runtime").unwrap();
        let mut files = serde_json::Map::new();
        for name in ["model.gguf", "server"] {
            let path = temp.path().join(name);
            files.insert(
                name.into(),
                json!({"bytes":path.metadata().unwrap().len(),"sha256":hash(&path).unwrap()}),
            );
        }
        fs::write(temp.path().join("manifest.json"), serde_json::to_vec(&json!({"schema_version":1,"engine":"llama.cpp","platform":platform(),"model_id":"test-model","context_limit":4096,"max_output_tokens":512,"model":"model.gguf","executable":"server","files":files})).unwrap()).unwrap();
        let sha = hash(&temp.path().join("manifest.json")).unwrap();
        (temp, sha)
    }
    #[test]
    fn trusted_hash_and_changed_file_rejected() {
        let (temp, sha) = fixture();
        assert!(verify(temp.path(), &sha, &platform()).is_ok());
        assert!(verify(temp.path(), "untrusted", &platform()).is_err());
        fs::write(temp.path().join("model.gguf"), b"changed").unwrap();
        assert!(verify(temp.path(), &sha, &platform()).is_err());
    }
    #[test]
    fn extra_files_platform_and_traversal_rejected() {
        let (temp, sha) = fixture();
        assert!(verify(temp.path(), &sha, "other-platform").is_err());
        for name in [
            "../model.gguf",
            "/model.gguf",
            "runtime/../model.gguf",
            "C:/model.gguf",
            "runtime\\file",
        ] {
            assert!(safe_file(temp.path(), name).is_err());
        }
        fs::write(temp.path().join("injected.dll"), b"extra").unwrap();
        assert!(verify(temp.path(), &sha, &platform()).is_err());
    }
    #[test]
    fn no_request_starts_without_supported_verified_package() {
        let (temp, _) = fixture();
        let runtime = LocalRuntime::default();
        assert!(runtime.generate(temp.path(), "Continue briefly.").is_err());
        assert!(runtime.session.lock().unwrap().is_none());
        assert!(runtime.generate(temp.path(), &"x".repeat(65_537)).is_err());
        runtime.stop();
    }
    #[cfg(unix)]
    #[test]
    fn stop_drops_only_owned_process_and_private_directory() {
        let runtime = LocalRuntime::default();
        let private = tempfile::tempdir().unwrap();
        let path = private.path().to_owned();
        let child = Command::new("/bin/sleep").arg("30").spawn().unwrap();
        *runtime.session.lock().unwrap() = Some(Session {
            child,
            _private: private,
            url: String::new(),
            token: "test-token".into(),
        });
        runtime.stop();
        assert!(runtime.session.lock().unwrap().is_none());
        assert!(!path.exists());
    }
    #[test]
    #[ignore = "Explicit real-model development smoke; no model is downloaded by tests"]
    fn real_package_smoke() {
        let root = PathBuf::from(
            std::env::var("DRAFTHARBOUR_TEST_BUNDLE")
                .expect("Set the existing verified development bundle path"),
        );
        let runtime = LocalRuntime::default();
        assert_eq!(runtime.inspect(&root).unwrap(), MODEL);
        let result = runtime
            .generate(
                &root,
                "Continue in two sentences: A gull called across the quay.",
            )
            .unwrap();
        assert!(!result.text.trim().is_empty());
        assert_eq!(result.model, MODEL);
        runtime.stop();
        assert!(runtime.session.lock().unwrap().is_none());
    }
}
