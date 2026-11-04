import DraftHarbourNativeCore
import Foundation
import XCTest

private actor SuggestionTestProvider: AIProvider {
  nonisolated let id = "test-local"
  nonisolated let displayName = "Test Local"
  var requests: [AIRequest] = []
  func generate(_ request: AIRequest) async throws -> AIResponse {
    requests.append(request)
    return AIResponse(text: "Reviewed replacement.", provider: id)
  }
}

final class AISuggestionServiceTests: XCTestCase {
  func testLongChapterBrainstormUsesBoundedContextAndRequestedAction() async throws {
    var envelope = DhprojCodec.newProject(title: "Suggestions")
    envelope.sections[0].content = String(repeating: "The harbour bell rang across the quay. ", count: 900) + "Final clue."
    let provider = SuggestionTestProvider()
    let preview = try await AISuggestionService.generate(envelope: envelope, section: envelope.sections[0], selection: nil, action: .brainstorm, instruction: "", provider: provider, model: nil)
    let requests = await provider.requests
    XCTAssertEqual(requests.count, 1)
    XCTAssertTrue(requests[0].prompt.contains("exactly three"))
    XCTAssertTrue(requests[0].context?.contains("Final clue.") == true)
    XCTAssertLessThan(requests[0].context?.count ?? 99999, 3000)
    XCTAssertFalse(preview.replacesPassage)
    XCTAssertEqual(envelope.sections[0].content, preview.source)
  }

  func testCustomInstructionIsNotDroppedByPipelineTemplate() async throws {
    let envelope = DhprojCodec.newProject(title: "Suggestions")
    var section = envelope.sections[0]; section.content = "The bell rang."
    let provider = SuggestionTestProvider()
    _ = try await AISuggestionService.generate(envelope: envelope, section: section, selection: nil, action: .custom, instruction: "Suggest one unusual motivation.", provider: provider, model: nil)
    let requests = await provider.requests
    XCTAssertTrue(requests[0].prompt.contains("AUTHOR INSTRUCTION:\nSuggest one unusual motivation."))
    XCTAssertFalse(requests[0].prompt.hasPrefix("Continue"))
  }

  func testSelectedPassageApprovalPreservesSurroundingsAndRejectsStaleSource() async throws {
    let envelope = DhprojCodec.newProject(title: "Suggestions")
    var section = envelope.sections[0]; section.content = "Prefix. The old bell rang. Suffix."
    let range = (section.content! as NSString).range(of: "The old bell rang.")
    let preview = try await AISuggestionService.generate(envelope: envelope, section: section, selection: range, action: .revise, instruction: "", provider: SuggestionTestProvider(), model: nil)
    let result = try AISuggestionService.replacement(preview, current: section.content!)
    XCTAssertEqual(result, "Prefix. Reviewed replacement. Suffix.")
    XCTAssertThrowsError(try AISuggestionService.replacement(preview, current: section.content! + " Changed."))
    XCTAssertEqual(section.content, "Prefix. The old bell rang. Suffix.")
  }

  func testLongPassagesArePartitionedWithoutOmittingCharacters() {
    let source = String(repeating: "A sentence with words and an emoji 🐦. ", count: 400)
    let parts = AISuggestionService.passageParts(source)
    XCTAssertGreaterThan(parts.count, 1)
    XCTAssertEqual(parts.joined(), source)
    XCTAssertTrue(parts.allSatisfy { $0.count <= 2000 })
  }

  func testContextLimitErrorIsActionableAndDoesNotExposeRuntimeDetails() {
    let payload = Data(#"{"error":{"type":"exceed_context_size_error","message":"private-runtime-token"}}"#.utf8)
    let failure = LocalRuntimeFailure.httpFailure(status: 400, body: payload).localizedDescription
    XCTAssertTrue(failure.contains("context window"))
    XCTAssertFalse(failure.contains("private-runtime-token"))
  }
}
