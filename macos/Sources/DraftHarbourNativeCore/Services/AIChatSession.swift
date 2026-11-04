import Foundation
import Observation

/// A document owns this session; temporary sidebar/workspace views do not own requests.
@MainActor @Observable
public final class AIChatSession {
  public typealias Responder = @MainActor (String, DhprojEnvelope, AIProviderConfig, Bool, String, @escaping @Sendable (String) async -> Void) async throws -> AIChatGenerationResult
  public var selectedThreadID: String?
  public var selectedProviderID: String?
  public var prompt = ""
  public private(set) var isSending = false
  public var requestEdits = false
  public private(set) var sendStatus = ""
  public var errorMessage: String?
  @ObservationIgnored private var generationTask: Task<Void, Never>?
  @ObservationIgnored private let responder: Responder

  public init(responder: @escaping Responder = { prompt, envelope, config, edits, history, progress in
    try await AIChatService.respond(to: prompt, envelope: envelope, providerConfig: config, allowsEdits: edits, history: history, progress: progress)
  }) { self.responder = responder }

  public func start(store: ProjectStore, provider: AIProviderConfig) {
    let question = prompt.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !isSending, !question.isEmpty else { return }
    isSending = true
    sendStatus = "Connecting to local model…"
    let edits = requestEdits
    let projectID = store.envelope.project.id
    generationTask = Task { await sendPrompt(question: question, projectID: projectID, store: store, selectedProvider: provider, allowsEdits: edits) }
  }

  public func cancel() {
    generationTask?.cancel()
    if isSending { sendStatus = "Stopping…" }
  }

  public func waitForCompletion() async { await generationTask?.value }

  private func sendPrompt(question: String, projectID: String, store: ProjectStore, selectedProvider: AIProviderConfig, allowsEdits: Bool) async {
    let trimmed = question
    errorMessage = nil
    defer { isSending = false; generationTask = nil; if Task.isCancelled { sendStatus = "Request cancelled." } }

    do {
      try Task.checkCancellation()
      guard store.envelope.project.id == projectID else { return }
      _ = try NativeAIProviderFactory().provider(from: selectedProvider)
      let thread = store.ensureAIChatThread(id: selectedThreadID, title: trimmed)
      selectedThreadID = thread.id
      if !store.envelope.aiProviders.contains(where: { $0.id == selectedProvider.id }) {
        store.upsertAIProvider(selectedProvider)
      }
      _ = try store.appendAIChatMessage(threadID: thread.id, role: .user, content: trimmed)
      prompt = ""

      let shouldAddCharacters = AIChatService.shouldAddCharactersToStoryBible(trimmed)
      let shouldAddWorldEntries = AIChatService.shouldAddWorldEntriesToStoryBible(trimmed)
      if shouldAddCharacters || shouldAddWorldEntries {
        var replyParts: [String] = []
        var context = AIProjectContextService.index(for: store.envelope)

        if shouldAddCharacters {
          let candidates = context.manuscriptCharacterCandidates(limit: 80)
          let addedCharacters = store.addAICharacterCandidatesToStoryBible(candidates)
          replyParts.append(AIChatService.storyBibleAddResponse(
            addedCharacters: addedCharacters,
            candidates: candidates,
            checkedSectionCount: context.sections.count,
            projectType: context.projectType
          ))
          context = AIProjectContextService.index(for: store.envelope)
        }

        if shouldAddWorldEntries {
          let candidates = context.manuscriptWorldCandidates(limit: 80)
          let addedWorldEntries = store.addAIWorldCandidatesToStoryBible(candidates)
          replyParts.append(AIChatService.storyBibleWorldAddResponse(
            addedWorldEntries: addedWorldEntries,
            candidates: candidates,
            checkedSectionCount: context.sections.count,
            projectType: context.projectType
          ))
        }

        _ = try store.appendAIChatMessage(
          threadID: thread.id,
          role: .assistant,
          content: replyParts.joined(separator: "\n\n"),
          providerId: "local-story-bible-update",
          model: "story-bible-candidate-scan"
        )
        return
      }

      let history = (store.envelope.aiChatThreads.first(where: { $0.id == thread.id })?.messages.dropLast().suffix(6) ?? []).map { "\($0.role.rawValue): \($0.content)" }.joined(separator: "\n\n")
      let result = try await responder(trimmed, store.envelope, selectedProvider, allowsEdits, history) { message in
        await MainActor.run { self.sendStatus = message }
      }
      try Task.checkCancellation()
      guard store.envelope.project.id == projectID else { return }
      _ = try store.appendAIChatMessage(
        threadID: thread.id,
        role: .assistant,
        content: result.reply,
        providerId: result.providerId,
        model: result.model,
        editProposals: result.editProposals
      )
    } catch {
      if !Task.isCancelled { errorMessage = error.localizedDescription }
    }
  }

}
