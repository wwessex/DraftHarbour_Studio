import DraftHarbourNativeCore
import Foundation
import XCTest

private final class UnreachableAIProtocol: URLProtocol, @unchecked Sendable {
  override class func canInit(with request: URLRequest) -> Bool { true }
  override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
  override func startLoading() { client?.urlProtocol(self, didFailWithError: URLError(.cannotConnectToHost)) }
  override func stopLoading() {}
}

final class AIConnectionTests: XCTestCase {
  func testStoppedLocalServiceProvidesRecoveryGuidance() async throws {
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [UnreachableAIProtocol.self]
    let session = URLSession(configuration: config)
    defer { session.invalidateAndCancel() }
    let provider = OpenAICompatibleProvider(id: "local", displayName: "Local", endpoint: URL(string: "http://127.0.0.1:8890/v1/chat/completions")!, apiKey: nil, defaultModel: "narratryx-craft-v1", session: session)
    do {
      _ = try await provider.generate(AIRequest(prompt: "Hello", projectType: .book))
      XCTFail("Stopped service must fail")
    } catch {
      XCTAssertTrue(error.localizedDescription.contains("Start your local model service"))
    }
  }
}
