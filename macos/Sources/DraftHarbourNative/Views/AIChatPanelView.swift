import DraftHarbourNativeCore
import SwiftUI

private struct AIProposalDisplayRow: Identifiable {
  var threadID: String
  var messageID: String
  var proposal: AIEditProposal

  var id: String { proposal.id }
}

struct AIChatPanelView: View {
  @Bindable var store: ProjectStore
  @Bindable var session: AIChatSession
  var focusEditProposal: (AIEditProposal) -> Void

  @AppStorage("DraftHarbour.aiSetup.mode") private var aiMode = "existing"

  private var providerOptions: [AIProviderConfig] {
    var providers = store.envelope.aiProviders.filter { $0.enabled && NativeAIProviderFactory.isLocalProvider($0) }
    if aiMode == "local", !providers.contains(where: { $0.endpoint == NativeLocalModelRuntime.endpoint }) {
      providers.insert(.managedLocalDefault(), at: 0)
    }
    if !providers.contains(where: { $0.provider == .appleFoundation }) {
      providers.append(.appleFoundationDefault())
    }
    return providers
  }

  private var selectedProvider: AIProviderConfig {
    if let selectedProviderID = session.selectedProviderID,
       let provider = providerOptions.first(where: { $0.id == selectedProviderID }) {
      return provider
    }
    return providerOptions.first ?? .appleFoundationDefault()
  }

  private var selectedThread: AIChatThread? {
    if session.selectedThreadID == "" { return nil }
    if let selectedThreadID = session.selectedThreadID,
       let thread = store.envelope.aiChatThreads.first(where: { $0.id == selectedThreadID }) {
      return thread
    }
    return store.envelope.aiChatThreads.first
  }

  private var proposalRows: [AIProposalDisplayRow] {
    guard let selectedThread else { return [] }
    return selectedThread.messages.flatMap { message in
      message.editProposals.map {
        AIProposalDisplayRow(threadID: selectedThread.id, messageID: message.id, proposal: $0)
      }
    }
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 14) {
      header
      threadSelector
      ScrollViewReader { reader in
        ScrollView {
          VStack(alignment: .leading, spacing: 14) {
            transcript
            if !proposalRows.isEmpty { proposals }
            Color.clear.frame(height: 1).id("chat-bottom")
          }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear { reader.scrollTo("chat-bottom", anchor: .bottom) }
        .onChange(of: selectedThread?.messages.count) { _, _ in
          reader.scrollTo("chat-bottom", anchor: .bottom)
        }
        .onChange(of: selectedThread?.id) { _, _ in
          reader.scrollTo("chat-bottom", anchor: .bottom)
        }
      }
      composer
        .fixedSize(horizontal: false, vertical: true)
        .layoutPriority(1)
      if let errorMessage = session.errorMessage {
        Label(errorMessage, systemImage: "exclamationmark.triangle")
          .foregroundStyle(.red)
      }
    }
    .onAppear {
      session.selectedThreadID = session.selectedThreadID ?? store.envelope.aiChatThreads.first?.id
      session.selectedProviderID = session.selectedProviderID ?? providerOptions.first?.id
    }
  }

  private var header: some View {
    GroupBox("Provider") {
      VStack(alignment: .leading, spacing: 10) {
        Picker("Provider", selection: Binding(get: {
          selectedProvider.id
        }, set: { value in
          session.selectedProviderID = value
        })) {
          ForEach(providerOptions) { provider in
            Text(provider.label).tag(provider.id)
          }
        }
        HStack(spacing: 10) {
          Label(providerStatusText(selectedProvider), systemImage: selectedProvider.provider == .appleFoundation ? "apple.logo" : "cpu")
            .foregroundStyle(providerStatusStyle(selectedProvider))
          Spacer()
          Text("Full project context")
            .font(.caption)
            .foregroundStyle(.secondary)
        }
        Text("AI Chat uses local models only. Project context stays on this device. Edits are proposals until accepted.")
          .font(.caption)
          .foregroundStyle(.secondary)
      }
      .padding(.vertical, 4)
    }
  }

  private var threadSelector: some View {
    HStack {
      Picker("Thread", selection: Binding(get: {
        selectedThread?.id ?? ""
      }, set: { value in
        session.selectedThreadID = value.isEmpty ? nil : value
      })) {
        if store.envelope.aiChatThreads.isEmpty {
          Text("New Chat").tag("")
        }
        ForEach(store.envelope.aiChatThreads) { thread in
          Text(thread.title).tag(thread.id)
        }
      }
      .frame(maxWidth: 360)

      Button {
        session.selectedThreadID = ""
        session.prompt = ""
      } label: {
        Label("New Chat", systemImage: "plus.message")
      }
      .help("Start a new local AI conversation")
    }
  }

  private var transcript: some View {
    GroupBox("Chat") {
      VStack(alignment: .leading, spacing: 12) {
        if let selectedThread, !selectedThread.messages.isEmpty {
          ForEach(selectedThread.messages) { message in
            VStack(alignment: .leading, spacing: 4) {
              HStack {
                Text(message.role == .user ? "You" : "Assistant")
                  .font(.headline)
                Spacer()
                if let providerId = message.providerId {
                  Text(providerId)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                }
              }
              Text(message.content)
                .fixedSize(horizontal: false, vertical: true)
                .textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading)
              if !message.editProposals.isEmpty {
                Text("\(message.editProposals.count) proposed edit\(message.editProposals.count == 1 ? "" : "s")")
                  .font(.caption)
                  .foregroundStyle(.secondary)
              }
            }
            .padding(.vertical, 6)
            Divider()
          }
        } else {
          ContentUnavailableView("No Chat Yet", systemImage: "message.badge", description: Text("Ask about the manuscript or request edits across the full local project."))
            .frame(maxWidth: .infinity, minHeight: 160)
        }
      }
      .padding(.vertical, 4)
    }
  }

  private var composer: some View {
    GroupBox("Ask") {
      VStack(alignment: .leading, spacing: 10) {
        Toggle("Request edit proposals", isOn: $session.requestEdits).disabled(session.isSending)
        Text("All \(store.envelope.sections.count) chapters/scenes · edits require approval").font(.caption).foregroundStyle(.secondary)
        if session.isSending { Text(session.sendStatus).font(.caption).foregroundStyle(.secondary) }
        TextField("Ask about continuity, characters, plot, or request specific edits", text: $session.prompt, axis: .vertical)
          .lineLimit(2...4)
          .textFieldStyle(.roundedBorder)
        HStack {
          Button {
            session.start(store: store, provider: selectedProvider)
          } label: {
            Label(session.isSending ? "Thinking..." : "Send", systemImage: "paperplane")
          }
          .help("Send your message to the selected local model")
          .disabled(session.isSending || session.prompt.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

          if session.isSending { Button("Stop") { session.cancel() }.help("Stop generating this reply") }
          if selectedProviderUnavailable {
            Text(providerStatusText(selectedProvider))
              .font(.caption)
              .foregroundStyle(.secondary)
          }
        }
      }
      .padding(.vertical, 4)
    }
  }

  private var proposals: some View {
    GroupBox("Proposed Edits") {
      VStack(alignment: .leading, spacing: 10) {
        let pendingCount = proposalRows.filter { $0.proposal.status == .pending }.count
        if proposalRows.isEmpty {
          Text("No proposed edits in this chat.")
            .foregroundStyle(.secondary)
        } else {
          HStack {
            Text("\(pendingCount) pending")
              .foregroundStyle(.secondary)
            Spacer()
            Button("Accept All") {
              guard let selectedThread else { return }
              _ = store.acceptAllPendingAIEditProposals(threadID: selectedThread.id, providerId: selectedProvider.id, prompt: latestUserPrompt(in: selectedThread))
            }
            .disabled(pendingCount == 0)
          }

          ForEach(proposalRows) { row in
            proposalRow(row)
            Divider()
          }
        }
      }
      .padding(.vertical, 4)
    }
  }

  private func proposalRow(_ row: AIProposalDisplayRow) -> some View {
    VStack(alignment: .leading, spacing: 8) {
      HStack {
        Text(sectionTitle(row.proposal.sectionId))
          .font(.headline)
        Text(row.proposal.status.rawValue.capitalized)
          .font(.caption)
          .foregroundStyle(statusStyle(row.proposal.status))
        Spacer()
        Button {
          focusEditProposal(row.proposal)
        } label: {
          Label("Focus", systemImage: "scope")
        }
      }
      Text(row.proposal.rationale)
        .foregroundStyle(.secondary)
      Grid(alignment: .leading, horizontalSpacing: 12, verticalSpacing: 6) {
        GridRow {
          Text("Original")
            .foregroundStyle(.secondary)
          Text(row.proposal.originalText)
            .textSelection(.enabled)
        }
        GridRow {
          Text("Replacement")
            .foregroundStyle(.secondary)
          Text(row.proposal.replacementText)
            .textSelection(.enabled)
        }
      }
      HStack {
        Button("Accept") {
          do {
            _ = try store.acceptAIEditProposal(
              threadID: row.threadID,
              messageID: row.messageID,
              proposalID: row.proposal.id,
              providerId: selectedProvider.id,
              prompt: selectedThread.map { latestUserPrompt(in: $0) } ?? ""
            )
          } catch {
            session.errorMessage = error.localizedDescription
          }
        }
        .disabled(row.proposal.status != .pending)

        Button("Reject") {
          do {
            _ = try store.rejectAIEditProposal(threadID: row.threadID, messageID: row.messageID, proposalID: row.proposal.id)
          } catch {
            session.errorMessage = error.localizedDescription
          }
        }
        .disabled(row.proposal.status != .pending)
      }
    }
  }

  private var selectedProviderUnavailable: Bool {
    selectedProvider.provider == .appleFoundation && AppleFoundationModelsProvider.availabilityStatus() != .available
  }

  private func providerStatusText(_ provider: AIProviderConfig) -> String {
    if provider.provider == .appleFoundation {
      return AppleFoundationModelsProvider.availabilityStatus().label
    }
    if provider.endpoint == NativeLocalModelRuntime.endpoint { return "On-device managed model" }
    return NativeAIProviderFactory.isLocalProvider(provider) ? "Local endpoint" : "Configured endpoint"
  }

  private func providerStatusStyle(_ provider: AIProviderConfig) -> Color {
    if provider.provider == .appleFoundation {
      return AppleFoundationModelsProvider.availabilityStatus() == .available ? .green : .secondary
    }
    return NativeAIProviderFactory.isLocalProvider(provider) ? .green : .secondary
  }

  private func statusStyle(_ status: AIEditProposalStatus) -> Color {
    switch status {
    case .pending:
      return .orange
    case .accepted:
      return .green
    case .rejected:
      return .secondary
    case .stale:
      return .red
    }
  }

  private func sectionTitle(_ id: String) -> String {
    store.envelope.sections.first(where: { $0.id == id })?.title ?? "Missing Section"
  }

  private func latestUserPrompt(in thread: AIChatThread) -> String {
    thread.messages.last(where: { $0.role == .user })?.content ?? ""
  }
}
