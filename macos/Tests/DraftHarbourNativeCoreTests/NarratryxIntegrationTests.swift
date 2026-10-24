import DraftHarbourNativeCore
import Foundation
import XCTest

final class NarratryxIntegrationTests: XCTestCase {
  func testProfileMatchesSharedContractWithoutCredentialsOrImplicitEndpoint() throws {
    let root = URL(fileURLWithPath: #filePath)
      .deletingLastPathComponent().deletingLastPathComponent()
      .deletingLastPathComponent().deletingLastPathComponent()
    let data = try Data(contentsOf: root.appendingPathComponent("fixtures/narratryx-profile.json"))
    let contract = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
    let config = NarratryxProfile.configuration()
    XCTAssertEqual(config.label, contract["label"] as? String)
    XCTAssertEqual(config.model, contract["model"] as? String)
    XCTAssertEqual(NarratryxProfile.baseModel, contract["baseModel"] as? String)
    XCTAssertEqual(config.provider, .customLLM)
    XCTAssertEqual(config.endpoint, "")
    XCTAssertNil(config.keychainAccount)
    XCTAssertTrue(NarratryxProfile.recognizes("narratryx-next-reviewed-version"))
  }

  func testNativeProviderUsesExactEndpointModelAndSecret() async throws {
    let configuration = URLSessionConfiguration.ephemeral
    configuration.protocolClasses = [NarratryxURLProtocol.self]
    let session = URLSession(configuration: configuration)
    defer { session.invalidateAndCancel(); NarratryxURLProtocol.handler = nil }
    NarratryxURLProtocol.handler = { request in
      XCTAssertEqual(request.url?.absoluteString, "https://models.example.test/v1/chat/completions")
      XCTAssertEqual(request.value(forHTTPHeaderField: "Authorization"), "Bearer private-test-key")
      let body = try JSONSerialization.jsonObject(with: requestBody(request)) as! [String: Any]
      XCTAssertEqual(body["model"] as? String, NarratryxProfile.model)
      let messages = try XCTUnwrap(body["messages"] as? [[String: String]])
      XCTAssertEqual(messages.count, 2)
      XCTAssertTrue(messages[1]["content"]!.contains("Original passage"))
      return (200, Data("{\"choices\":[{\"message\":{\"role\":\"assistant\",\"content\":\"A proposed continuation.\"}}]}".utf8))
    }
    let provider = OpenAICompatibleProvider(id: "experiment", displayName: NarratryxProfile.label,
      endpoint: URL(string: "https://models.example.test/v1/chat/completions")!, apiKey: "private-test-key", defaultModel: NarratryxProfile.model, session: session)
    let response = try await provider.generate(AIRequest(prompt: "Continue briefly", context: "Original passage", projectType: .book))
    XCTAssertEqual(response.text, "A proposed continuation.")
    XCTAssertEqual(response.model, NarratryxProfile.model)
  }

  func testOversizedContextExplainsFailureWithoutChangingTheProject() async throws {
    let configuration = URLSessionConfiguration.ephemeral
    configuration.protocolClasses = [NarratryxURLProtocol.self]
    let session = URLSession(configuration: configuration)
    defer { session.invalidateAndCancel(); NarratryxURLProtocol.handler = nil }
    NarratryxURLProtocol.handler = { _ in
      (413, Data("{\"error\":{\"message\":\"Use a shorter passage. Nothing was truncated.\"}}".utf8))
    }
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Safe trial"))
    store.updateActiveSectionContent("Original passage")
    let before = store.envelope
    let provider = OpenAICompatibleProvider(id: "experiment", displayName: NarratryxProfile.label,
      endpoint: URL(string: "https://models.example.test/v1/chat/completions")!, apiKey: "test-key", defaultModel: NarratryxProfile.model, session: session)
    do {
      _ = try await provider.generate(AIRequest(prompt: "Revise", context: "Original passage", projectType: .book))
      XCTFail("Oversized requests must fail explicitly")
    } catch {
      XCTAssertTrue(error.localizedDescription.contains("shorter passage"))
    }
    XCTAssertEqual(store.envelope, before)
  }
}

private func requestBody(_ request: URLRequest) throws -> Data {
  if let body = request.httpBody { return body }
  guard let stream = request.httpBodyStream else { return Data() }
  stream.open()
  defer { stream.close() }
  var data = Data()
  var buffer = [UInt8](repeating: 0, count: 1024)
  while stream.hasBytesAvailable {
    let count = stream.read(&buffer, maxLength: buffer.count)
    if count < 0 { throw stream.streamError ?? URLError(.cannotDecodeContentData) }
    if count == 0 { break }
    data.append(buffer, count: count)
  }
  return data
}

private final class NarratryxURLProtocol: URLProtocol {
  nonisolated(unsafe) static var handler: ((URLRequest) throws -> (Int, Data))?
  override class func canInit(with request: URLRequest) -> Bool { true }
  override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
  override func startLoading() {
    do {
      guard let handler = Self.handler else { throw URLError(.badServerResponse) }
      let (status, data) = try handler(request)
      let response = HTTPURLResponse(url: request.url!, statusCode: status, httpVersion: nil, headerFields: ["Content-Type": "application/json"])!
      client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
      client?.urlProtocol(self, didLoad: data)
      client?.urlProtocolDidFinishLoading(self)
    } catch {
      client?.urlProtocol(self, didFailWithError: error)
    }
  }
  override func stopLoading() {}
}
