import DraftHarbourNativeCore
import XCTest

private actor ChatReplyGate {
  var pending: CheckedContinuation<AIChatGenerationResult, Never>?
  func reply() async -> AIChatGenerationResult {
    await withCheckedContinuation { pending = $0 }
  }
  func isWaiting() -> Bool { pending != nil }
  func finish() { pending?.resume(returning: AIChatGenerationResult(reply: "The answer survived the workspace change.", providerId: "test-local")); pending = nil }
}

final class AIChatSessionTests: XCTestCase {
  @MainActor
  func testDocumentSessionSurvivesPresenterReplacementAndRejectsDuplicateSend() async throws {
    let gate = ChatReplyGate()
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Session"))
    let session = AIChatSession { _, _, _, _, _, progress in
      await progress("Reading chapter 1…")
      return await gate.reply()
    }
    session.prompt = "Tell me about the plot."
    session.start(store: store, provider: .appleFoundationDefault())
    for _ in 0..<100 where !(await gate.isWaiting()) { await Task.yield() }
    XCTAssertTrue(session.isSending)
    XCTAssertEqual(session.sendStatus, "Reading chapter 1…")
    // Workspace/sidebar presenters can be discarded; the document retains the same session.
    var presenter: AIChatSession? = session
    presenter = nil
    XCTAssertNil(presenter)
    let nextPresenter = session
    session.prompt = "Do not start a second request."
    nextPresenter.start(store: store, provider: .appleFoundationDefault())
    await gate.finish()
    await nextPresenter.waitForCompletion()
    XCTAssertFalse(nextPresenter.isSending)
    XCTAssertNil(nextPresenter.errorMessage)
    XCTAssertEqual(store.envelope.aiChatThreads[0].messages.map(\.role), [.user, .assistant])
    XCTAssertEqual(store.envelope.aiChatThreads[0].messages.last?.content, "The answer survived the workspace change.")
  }

  @MainActor
  func testExplicitStopRejectsLateReplyAndAllowsAnotherMessage() async throws {
    let gate = ChatReplyGate()
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Stop"))
    let session = AIChatSession { _, _, _, _, _, _ in await gate.reply() }
    session.prompt = "First request"
    session.start(store: store, provider: .appleFoundationDefault())
    for _ in 0..<100 where !(await gate.isWaiting()) { await Task.yield() }
    session.cancel()
    await gate.finish()
    await session.waitForCompletion()
    XCTAssertFalse(session.isSending)
    XCTAssertEqual(store.envelope.aiChatThreads[0].messages.count, 1)
    XCTAssertEqual(session.sendStatus, "Request cancelled.")
    session.prompt = "Second request"
    session.start(store: store, provider: .appleFoundationDefault())
    for _ in 0..<100 where !(await gate.isWaiting()) { await Task.yield() }
    await gate.finish()
    await session.waitForCompletion()
    XCTAssertEqual(store.envelope.aiChatThreads[0].messages.count, 3)
  }
  @MainActor
  func testLateReplyCannotBeAddedToAReplacementProject() async throws {
    let gate = ChatReplyGate()
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Original"))
    let session = AIChatSession { _, _, _, _, _, _ in await gate.reply() }
    session.prompt = "Review the original project"
    session.start(store: store, provider: .appleFoundationDefault())
    for _ in 0..<100 where !(await gate.isWaiting()) { await Task.yield() }
    store.envelope = DhprojCodec.newProject(title: "Replacement")
    await gate.finish()
    await session.waitForCompletion()
    XCTAssertTrue(store.envelope.aiChatThreads.isEmpty)
    XCTAssertFalse(session.isSending)
  }

}
