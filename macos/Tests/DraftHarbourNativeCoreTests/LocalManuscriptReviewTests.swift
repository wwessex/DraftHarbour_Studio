import DraftHarbourNativeCore
import XCTest

private actor ReviewTestProvider: AIProvider {
  nonisolated let id = "test-local"
  nonisolated let displayName = "Test Local"
  var requests: [AIRequest] = []
  func generate(_ request: AIRequest) async throws -> AIResponse {
    requests.append(request)
    return AIResponse(text: "Specific feedback and suggestions.", provider: id)
  }
}

final class LocalManuscriptReviewTests: XCTestCase {
  func testLoopbackClassificationRejectsLookalikeRemoteHosts() {
    for endpoint in ["http://localhost:8080/v1", "http://127.0.0.1:8080", "http://[::1]:8080"] {
      XCTAssertTrue(NativeAIProviderFactory.isLocalProvider(AIProviderConfig(provider: .customLLM, label: "Local", endpoint: endpoint, model: "test")))
    }
    for endpoint in ["https://localhost.evil.test/v1", "https://example.com/127.0.0.1", "file://localhost/model"] {
      XCTAssertFalse(NativeAIProviderFactory.isLocalProvider(AIProviderConfig(provider: .customLLM, label: "Remote", endpoint: endpoint, model: "test")))
    }
  }

  func testReviewCoversAllPartsAndLaterSections() async throws {
    var envelope = DhprojCodec.newProject(title: "Review")
    let text = String(repeating: "A", count: 9000)
    envelope.sections[0].content = text
    envelope.sections.append(Section(novelId: envelope.project.id, order: 1, title: "Ending", content: "The ending."))
    envelope.sections.append(Section(novelId: envelope.project.id, order: 2, title: "Empty", content: ""))
    XCTAssertEqual(LocalManuscriptReview.chunks(text).joined(), text)
    let provider = ReviewTestProvider()
    let result = try await LocalManuscriptReview.run(envelope: envelope, provider: provider) { _, _ in }
    XCTAssertEqual(result.findings.count, 4)
    XCTAssertEqual(result.emptyCount, 1)
    XCTAssertTrue(result.findings.last?.title.contains("Ending") == true)
    let requests = await provider.requests
    XCTAssertEqual(requests.count, 5)
  }

  func testChatRejectsRemoteProviderBeforeRequest() async throws {
    do {
      _ = try await AIChatService.respond(to: "Hello", envelope: DhprojCodec.newProject(title: "Chat"), providerConfig: AIProviderConfig(provider: .openAICompatible, label: "Online", endpoint: "https://example.com/v1/chat/completions", model: "test"))
      XCTFail("Remote provider must not be used by chat")
    } catch {
      XCTAssertTrue(error.localizedDescription.contains("local model"))
    }
  }
}
