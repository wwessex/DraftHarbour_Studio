import Foundation

public struct LocalModelInstallPlan: Sendable {
  public var model: String
  public var packageBytes: UInt64
  public var requiredBytes: UInt64
  public var availableBytes: UInt64
  public var physicalMemory: UInt64
}

/// Installs only a catalog-pinned directory. No archives, executable paths or
/// catalog overrides come from imported projects or the shared renderer.
public enum LocalModelInstaller {
  public static let minimumMemory: UInt64 = 8 * 1024 * 1024 * 1024
  private static let reserve: UInt64 = 256 * 1024 * 1024
  public static func previousURL(for destination: URL) -> URL {
    destination.deletingLastPathComponent().appendingPathComponent("previous-bundle", isDirectory: true)
  }
  public static func plan(source: URL, destination: URL = NativeLocalModelRuntime.packageURL,
                          catalog: LocalRuntimeCatalog = .development) throws -> LocalModelInstallPlan {
    let manifest = try LocalRuntimePackage.verify(source, catalog: catalog)
    let parent = destination.deletingLastPathComponent()
    let sourceParts = source.standardizedFileURL.resolvingSymlinksInPath().pathComponents
    let parentParts = parent.standardizedFileURL.resolvingSymlinksInPath().pathComponents
    guard !sourceParts.starts(with: parentParts), !parentParts.starts(with: sourceParts) else {
      throw LocalRuntimeFailure.unavailable("Choose a package outside the app's local model storage.")
    }
    try FileManager.default.createDirectory(at: parent, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
    let capacity = try parent.resourceValues(forKeys: [.volumeAvailableCapacityForImportantUsageKey])
    guard let available = capacity.volumeAvailableCapacityForImportantUsage, available >= 0 else {
      throw LocalRuntimeFailure.unavailable("Unable to check available model storage.")
    }
    let bytes = manifest.files.values.reduce(UInt64(0)) { $0 + $1.bytes } + UInt64(try Data(contentsOf: source.appendingPathComponent("manifest.json")).count)
    return try resources(model: manifest.model_id, bytes: bytes, available: UInt64(available), memory: ProcessInfo.processInfo.physicalMemory)
  }
  static func resources(model: String, bytes: UInt64, available: UInt64, memory: UInt64) throws -> LocalModelInstallPlan {
    guard memory >= minimumMemory else { throw LocalRuntimeFailure.unavailable("This experimental model requires at least 8 GiB of RAM. It has been tested on a 16 GB Mac.") }
    let (required, overflow) = bytes.addingReportingOverflow(reserve)
    guard !overflow, available >= required else { throw LocalRuntimeFailure.unavailable("There is not enough free space to stage and verify this model. The installed model is unchanged.") }
    return LocalModelInstallPlan(model: model, packageBytes: bytes, requiredBytes: required, availableBytes: available, physicalMemory: memory)
  }
  public static func install(source: URL, destination: URL = NativeLocalModelRuntime.packageURL,
                             catalog: LocalRuntimeCatalog = .development) throws -> String {
    _ = try plan(source: source, destination: destination, catalog: catalog)
    return try replace(source: source, destination: destination, catalog: catalog)
  }
  // The activation seam lets regression tests exercise an OS rename failure.
  static func replace(source: URL, destination: URL, catalog: LocalRuntimeCatalog,
                      activate: (URL, URL) throws -> Void = { try FileManager.default.moveItem(at: $0, to: $1) }) throws -> String {
    let fm = FileManager.default
    let manifest = try LocalRuntimePackage.verify(source, catalog: catalog)
    let parent = destination.deletingLastPathComponent()
    let previous = previousURL(for: destination)
    let hadActive = fm.fileExists(atPath: destination.path)
    let hadPrevious = fm.fileExists(atPath: previous.path)
    if hadActive { _ = try LocalRuntimePackage.verify(destination, catalog: catalog) }
    if hadPrevious { _ = try LocalRuntimePackage.verify(previous, catalog: catalog) }
    let work = parent.appendingPathComponent(".install-\(UUID().uuidString)", isDirectory: true)
    let staged = work.appendingPathComponent("bundle", isDirectory: true)
    let retired = work.appendingPathComponent("retired", isDirectory: true)
    try fm.createDirectory(at: staged, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
    var preserveRecovery = false
    defer { if !preserveRecovery { try? fm.removeItem(at: work) } }
    for name in Array(manifest.files.keys) + ["manifest.json"] {
      let file = try LocalRuntimePackage.file(name, in: source)
      let target = staged.appendingPathComponent(name)
      try fm.createDirectory(at: target.deletingLastPathComponent(), withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
      try fm.copyItem(at: file, to: target)
    }
    _ = try LocalRuntimePackage.verify(staged, catalog: catalog)
    do {
      if hadPrevious { try fm.moveItem(at: previous, to: retired) }
      if hadActive { try fm.moveItem(at: destination, to: previous) }
      try activate(staged, destination)
    } catch {
      if !fm.fileExists(atPath: destination.path), hadActive, fm.fileExists(atPath: previous.path) {
        try? fm.moveItem(at: previous, to: destination)
      }
      if !fm.fileExists(atPath: previous.path), fm.fileExists(atPath: retired.path) { try? fm.moveItem(at: retired, to: previous) }
      // Never discard a previous package if an OS failure prevented recovery.
      preserveRecovery = fm.fileExists(atPath: retired.path)
      throw LocalRuntimeFailure.unavailable("Installation failed. Existing model files were preserved; try restoring the previous package.")
    }
    return manifest.model_id
  }
  public static func restorePrevious(destination: URL = NativeLocalModelRuntime.packageURL,
                                     catalog: LocalRuntimeCatalog = .development) throws -> String {
    let fm = FileManager.default, previous = previousURL(for: destination)
    let manifest = try LocalRuntimePackage.verify(previous, catalog: catalog)
    let hadActive = fm.fileExists(atPath: destination.path)
    if hadActive { _ = try LocalRuntimePackage.verify(destination, catalog: catalog) }
    let held = destination.deletingLastPathComponent().appendingPathComponent(".rollback-\(UUID().uuidString)")
    do {
      if hadActive { try fm.moveItem(at: destination, to: held) }
      try fm.moveItem(at: previous, to: destination)
      if hadActive { try fm.moveItem(at: held, to: previous) }
    } catch {
      if !fm.fileExists(atPath: destination.path), fm.fileExists(atPath: held.path) { try? fm.moveItem(at: held, to: destination) }
      throw LocalRuntimeFailure.unavailable("Restore failed. Model files were retained for recovery.")
    }
    return manifest.model_id
  }
}
