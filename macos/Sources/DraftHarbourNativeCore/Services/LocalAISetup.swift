import Foundation

/// Device setup only: never imports credentials, edits projects or chooses an online provider.
public enum LocalAISetup {
  public enum PackageState: Equatable, Sendable {
    case unchecked
    case missing
    case verified(String)
    case rejected(String)
    case unsupported

    public var canEnable: Bool {
      if case .verified = self { return true }
      return false
    }
    public var message: String {
      switch self {
      case .unchecked: return "Installed package has not been checked."
      case .missing: return "Narratryx is not installed. Select an already obtained verified package folder to install it."
      case .verified: return "Narratryx Craft v1 is installed and verified. It starts only when you request AI assistance."
      case .rejected(let reason): return "The installed package could not be verified: \(reason)"
      case .unsupported: return "This package supports Apple Silicon Macs only. No verified package is available for this Mac."
      }
    }
  }

  public static let requirements = "Narratryx Craft v1 is experimental. The verified package is about 2.71 GB and is obtained separately; it is not included with the app and no public download is available here. Select the complete folder containing manifest.json, not a model file or archive. No server setup, API key or training is needed."
  public static let resources = "Installation needs free space for another copy of the package plus a 256 MiB reserve, while retaining an existing verified copy for recovery. The selected folder is kept. At least 8 GiB of physical memory is required as a rejection guard; this is not a performance guarantee. Tested on one 16 GB development Mac, not every supported Mac."
  public static let recovery = "You can select a verified package again or try Restore previous package. Unrecognized or changed files are preserved and may prevent replacement or restore; do not delete recovery folders. You can continue writing without AI."

  public static func needsFirstRun(storedMode: String?, hasEnabledProviders: Bool) -> Bool {
    storedMode == nil && !hasEnabledProviders
  }

  /// Hashing is performed by the caller off the UI thread. No runtime is started.
  public static func inspect(root: URL = NativeLocalModelRuntime.packageURL,
                             catalog: LocalRuntimeCatalog = .development,
                             platform: String = LocalRuntimePackage.platform,
                             memory: UInt64 = ProcessInfo.processInfo.physicalMemory) -> PackageState {
    guard catalog.platform == platform else { return .unsupported }
    guard FileManager.default.fileExists(atPath: root.path) else { return .missing }
    do {
      let manifest = try LocalRuntimePackage.verify(root, catalog: catalog, platform: platform)
      guard memory >= LocalModelInstaller.minimumMemory else {
        return .rejected("This Mac has less than the required 8 GiB of physical memory.")
      }
      return .verified(manifest.model_id)
    } catch { return .rejected(error.localizedDescription) }
  }
}
