import Foundation
import XCTest
@testable import DraftHarbourNativeCore

@MainActor
final class LocalModelRuntimeTests: XCTestCase {
  private func fixture() throws -> (URL, LocalRuntimeCatalog) {
    let root = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
    addTeardownBlock { try? FileManager.default.removeItem(at: root) }
    try Data("model".utf8).write(to: root.appendingPathComponent("model.gguf"))
    try Data("runtime".utf8).write(to: root.appendingPathComponent("server"))
    var files: [String: Any] = [:]
    for name in ["model.gguf", "server"] {
      let path = root.appendingPathComponent(name)
      files[name] = ["bytes": try Data(contentsOf: path).count, "sha256": try LocalRuntimePackage.sha256(path)]
    }
    let payload: [String: Any] = ["schema_version": 1, "engine": "llama.cpp", "platform": LocalRuntimePackage.platform,
      "model_id": NativeLocalModelRuntime.modelID, "context_limit": 4096, "max_output_tokens": 512,
      "model": "model.gguf", "executable": "server", "files": files]
    try JSONSerialization.data(withJSONObject: payload).write(to: root.appendingPathComponent("manifest.json"))
    return (root, LocalRuntimeCatalog(manifestSHA256: try LocalRuntimePackage.sha256(root.appendingPathComponent("manifest.json")), platform: LocalRuntimePackage.platform))
  }
  func testVerifiedPackageRejectsTamperedModelAndExternalTrustHash() throws {
    let (root, catalog) = try fixture()
    XCTAssertEqual(try LocalRuntimePackage.verify(root, catalog: catalog).model_id, NativeLocalModelRuntime.modelID)
    XCTAssertThrowsError(try LocalRuntimePackage.verify(root, catalog: LocalRuntimeCatalog(manifestSHA256: "wrong", platform: catalog.platform)))
    try Data("changed".utf8).write(to: root.appendingPathComponent("model.gguf"))
    XCTAssertThrowsError(try LocalRuntimePackage.verify(root, catalog: catalog))
  }
  func testPlatformTraversalAndUnlistedLibrariesAreRejected() throws {
    let (root, catalog) = try fixture()
    XCTAssertThrowsError(try LocalRuntimePackage.verify(root, catalog: catalog, platform: "different-platform"))
    for name in ["../server", "/server", "runtime/../server", "C:/server", "runtime\\server"] {
      XCTAssertThrowsError(try LocalRuntimePackage.file(name, in: root))
    }
    try Data("extra".utf8).write(to: root.appendingPathComponent("injected.dylib"))
    XCTAssertThrowsError(try LocalRuntimePackage.verify(root, catalog: catalog))
  }
  func testSymlinkFilesAreRejected() throws {
    let (root, catalog) = try fixture()
    try FileManager.default.removeItem(at: root.appendingPathComponent("model.gguf"))
    try FileManager.default.createSymbolicLink(at: root.appendingPathComponent("model.gguf"), withDestinationURL: root.appendingPathComponent("server"))
    XCTAssertThrowsError(try LocalRuntimePackage.verify(root, catalog: catalog))
  }
  func testInvalidExecutableCannotBecomeAReadyRuntime() async throws {
    let (root, catalog) = try fixture()
    let runtime = NativeLocalModelRuntime(root: root, catalog: catalog)
    do {
      _ = try await runtime.generate(AIRequest(prompt: "Continue.", projectType: .book))
      XCTFail("Invalid executable must never become ready")
    } catch { /* Explicit failure, no remote provider is involved. */ }
    runtime.stopNow()
  }
  func testCataloguePinMatchesDevelopmentEvidence() throws {
    let repository = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    let data = try Data(contentsOf: repository.appendingPathComponent("llm/Narratryx/configs/portable-craft-v1.dev-catalog.json"))
    let catalog = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
    XCTAssertEqual(catalog["manifest_sha256"] as? String, LocalRuntimeCatalog.development.manifestSHA256)
    XCTAssertEqual(catalog["platform"] as? String, LocalRuntimeCatalog.development.platform)
    XCTAssertEqual(catalog["model_id"] as? String, NativeLocalModelRuntime.modelID)
  }
  private func installDestination() throws -> URL {
    let (storage, _) = try fixture()
    let parent = storage.appendingPathComponent("installed", isDirectory: true)
    try FileManager.default.createDirectory(at: parent, withIntermediateDirectories: true)
    return parent.appendingPathComponent("bundle", isDirectory: true)
  }
  func testInstallerResourceLimits() throws {
    XCTAssertNoThrow(try LocalModelInstaller.resources(model: "test", bytes: 100, available: 1_000_000_000, memory: LocalModelInstaller.minimumMemory))
    XCTAssertThrowsError(try LocalModelInstaller.resources(model: "test", bytes: 100, available: 10, memory: LocalModelInstaller.minimumMemory))
    XCTAssertThrowsError(try LocalModelInstaller.resources(model: "test", bytes: 100, available: UInt64.max, memory: LocalModelInstaller.minimumMemory - 1))
  }
  func testInstallReinstallAndRestoreVerifiedPackage() throws {
    let (source, catalog) = try fixture(); let destination = try installDestination()
    for _ in 0..<2 { _ = try LocalModelInstaller.replace(source: source, destination: destination, catalog: catalog) }
    XCTAssertNoThrow(try LocalRuntimePackage.verify(destination, catalog: catalog))
    XCTAssertNoThrow(try LocalRuntimePackage.verify(LocalModelInstaller.previousURL(for: destination), catalog: catalog))
    _ = try LocalModelInstaller.restorePrevious(destination: destination, catalog: catalog)
    XCTAssertNoThrow(try LocalRuntimePackage.verify(destination, catalog: catalog))
  }
  func testFailedPromotionPreservesWorkingPackage() throws {
    let (source, catalog) = try fixture(); let destination = try installDestination()
    _ = try LocalModelInstaller.replace(source: source, destination: destination, catalog: catalog)
    XCTAssertThrowsError(try LocalModelInstaller.replace(source: source, destination: destination, catalog: catalog,
      activate: { _, _ in throw LocalRuntimeFailure.unavailable("Simulated rename failure") }))
    XCTAssertNoThrow(try LocalRuntimePackage.verify(destination, catalog: catalog))
    XCTAssertNoThrow(try LocalRuntimePackage.verify(source, catalog: catalog))
  }
  func testUnrecognizedPreviousFilesAreNeverDeleted() throws {
    let (source, catalog) = try fixture(); let destination = try installDestination()
    _ = try LocalModelInstaller.replace(source: source, destination: destination, catalog: catalog)
    let previous = LocalModelInstaller.previousURL(for: destination)
    try FileManager.default.createDirectory(at: previous, withIntermediateDirectories: true)
    let keep = previous.appendingPathComponent("keep.txt")
    try Data("unrecognized data".utf8).write(to: keep)
    XCTAssertThrowsError(try LocalModelInstaller.replace(source: source, destination: destination, catalog: catalog))
    XCTAssertEqual(try String(contentsOf: keep, encoding: .utf8), "unrecognized data")
    XCTAssertNoThrow(try LocalRuntimePackage.verify(destination, catalog: catalog))
  }
  func testTamperedSourceCannotReplaceInstalledModel() throws {
    let (source, catalog) = try fixture(); let destination = try installDestination()
    _ = try LocalModelInstaller.replace(source: source, destination: destination, catalog: catalog)
    try Data("tampered".utf8).write(to: source.appendingPathComponent("model.gguf"))
    XCTAssertThrowsError(try LocalModelInstaller.replace(source: source, destination: destination, catalog: catalog))
    XCTAssertNoThrow(try LocalRuntimePackage.verify(destination, catalog: catalog))
  }
  func testRestoreCanRecoverMissingActiveDirectory() throws {
    let (source, catalog) = try fixture(); let destination = try installDestination()
    try FileManager.default.moveItem(at: source, to: LocalModelInstaller.previousURL(for: destination))
    _ = try LocalModelInstaller.restorePrevious(destination: destination, catalog: catalog)
    XCTAssertNoThrow(try LocalRuntimePackage.verify(destination, catalog: catalog))
  }
  func testLocalSetupCannotSendOtherNativeToolsToRemoteProviders() throws {
    let key = "DraftHarbour.aiSetup.mode", defaults = UserDefaults.standard
    let previous = defaults.string(forKey: key)
    defer { if let previous { defaults.set(previous, forKey: key) } else { defaults.removeObject(forKey: key) } }
    defaults.set("local", forKey: key)
    for type in [AIProviderType.customLLM, .openAICompatible, .localOpenAI] {
      let config = AIProviderConfig(provider: type, label: "Remote", endpoint: "https://example.test/v1/chat/completions", model: "test")
      XCTAssertThrowsError(try NativeAIProviderFactory().provider(from: config)) { error in
        XCTAssertTrue(error.localizedDescription.contains("On this computer"))
      }
    }
  }
}
