import DraftHarbourNativeCore
import XCTest

private actor ManuscriptChatTestProvider: AIProvider {
  nonisolated let id = "test-local"
  nonisolated let displayName = "Test Local"
  var requests: [AIRequest] = []
  func generate(_ request: AIRequest) async throws -> AIResponse {
    requests.append(request)
    let text = request.sectionTitle == "Return"
      ? #"{"reply":"Repeated word","edits":[{"before":"The the brass bell","after":"The brass bell","rationale":"Remove repetition"}]}"#
      : request.sectionTitle == nil ? "Overall manuscript answer." : #"{"reply":"Opening observed","edits":[]}"#
    return AIResponse(text: text, provider: id)
  }
}

final class ManuscriptChatTests: XCTestCase {
  private func manuscript() -> DhprojEnvelope {
    var envelope = DhprojCodec.newProject(title: "Chat")
    envelope.sections[0].title = "Opening"
    envelope.sections[0].content = String(repeating: "A", count: 7000) + "Late clue."
    envelope.sections.append(Section(id: "return", novelId: envelope.project.id, order: 1, title: "Return", content: "The the brass bell rang."))
    return envelope
  }

  func testReadsAllChaptersAndBuildsApprovalOnlyProposal() async throws {
    let envelope = manuscript()
    let engine = ManuscriptChatTestProvider()
    let result = try await ManuscriptChatService.respond(prompt: "Remove repetition in Return", context: AIProjectContextService.index(for: envelope), provider: engine, model: nil, allowsEdits: true)
    let requests = await engine.requests
    XCTAssertEqual(requests.compactMap(\.sectionTitle), ["Opening", "Opening", "Opening", "Return"])
    XCTAssertTrue(requests.contains { $0.context?.contains("Late clue.") == true })
    XCTAssertEqual(result.editProposals.count, 1)
    let store = ProjectStore(envelope: envelope)
    let thread = store.ensureAIChatThread(title: "Edit")
    let message = try store.appendAIChatMessage(threadID: thread.id, role: .assistant, content: result.reply, editProposals: result.editProposals)
    XCTAssertEqual(store.envelope.sections[1].content, "The the brass bell rang.")
    let proposal = try XCTUnwrap(result.editProposals.first)
    XCTAssertEqual(try store.acceptAIEditProposal(threadID: thread.id, messageID: message.id, proposalID: proposal.id, providerId: engine.id, prompt: "Remove repetition"), .accepted)
    XCTAssertEqual(store.envelope.sections[1].content, "The brass bell rang.")
    XCTAssertEqual(store.envelope.snapshots.first?.doc, "The the brass bell rang.")
  }

  func testRejectsApprovalAfterUnrelatedManuscriptEdit() async throws {
    let envelope = manuscript()
    let result = try await ManuscriptChatService.respond(prompt: "Remove repetition", context: AIProjectContextService.index(for: envelope), provider: ManuscriptChatTestProvider(), model: nil, allowsEdits: true)
    let store = ProjectStore(envelope: envelope)
    let thread = store.ensureAIChatThread(title: "Edit")
    let message = try store.appendAIChatMessage(threadID: thread.id, role: .assistant, content: result.reply, editProposals: result.editProposals)
    store.selectSection("return")
    store.updateActiveSectionContent("The the brass bell rang loudly.")
    let proposal = try XCTUnwrap(result.editProposals.first)
    XCTAssertEqual(try store.acceptAIEditProposal(threadID: thread.id, messageID: message.id, proposalID: proposal.id, providerId: "test", prompt: "Edit"), .stale)
    XCTAssertEqual(store.activeSection?.content, "The the brass bell rang loudly.")
  }

  func testDiscussionCannotReturnEdits() async throws {
    let result = try await ManuscriptChatService.respond(prompt: "Discuss", context: AIProjectContextService.index(for: manuscript()), provider: ManuscriptChatTestProvider(), model: nil, allowsEdits: false)
    XCTAssertTrue(result.editProposals.isEmpty)
  }
}
