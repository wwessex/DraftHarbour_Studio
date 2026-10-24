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
}
