import DraftHarbourNativeCore
import SwiftUI

struct AISuggestionsSidebarView: View {
  @Bindable var store: ProjectStore
  var selection: NSRange
  @AppStorage("DraftHarbour.aiSetup.mode") private var aiMode = "existing"
  @State private var instruction = ""
  @State private var preview: AISuggestionPreview?
  @State private var error: String?
  @State private var status = ""
  @State private var task: Task<Void, Never>?

  var body: some View {
    VStack(alignment: .leading, spacing: 14) {
      Text("Suggestions use the last 2,000 characters of the current chapter for ideas. Revise, Strengthen and Shorten target your selection, or the last paragraph, in bounded parts.")
        .font(.caption).foregroundStyle(.secondary)
      GroupBox("Quick Actions") {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 120), spacing: 8)], spacing: 8) {
          ForEach(AISuggestionAction.allCases.filter { $0 != .custom }, id: \.rawValue) { action in
            Button(action.title) { start(action) }.frame(maxWidth: .infinity)
          }
        }.disabled(task != nil || store.activeSection == nil)
      }
      TextField("Ask for ideas or feedback", text: $instruction, axis: .vertical)
        .lineLimit(3...6).textFieldStyle(.roundedBorder)
      HStack {
        Button("Run Prompt") { start(.custom) }
          .disabled(task != nil || instruction.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || store.activeSection == nil)
        if task != nil { Button("Stop") { task?.cancel(); status = "Suggestion cancelled." } }
      }
      if !status.isEmpty { Text(status).font(.callout).foregroundStyle(.secondary) }
      if let error { Text(error).foregroundStyle(.red).textSelection(.enabled) }
      if let preview {
        GroupBox("Suggestion Preview") {
          VStack(alignment: .leading, spacing: 10) {
            Text(store.envelope.sections.first(where: { $0.id == preview.sectionID })?.title ?? "Original chapter").font(.headline)
            if preview.replacesPassage {
              DisclosureGroup("Original reviewed passage") { Text((preview.source as NSString).substring(with: preview.range)).textSelection(.enabled) }
            }
            Text(preview.text).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading)
            Text("Your draft is unchanged until you approve. A recovery snapshot is saved first.").font(.caption).foregroundStyle(.secondary)
            Button(preview.replacesPassage ? "Replace Reviewed Passage" : "Append to Chapter") { apply(preview) }
            Button("Discard") { self.preview = nil }
          }
        }
      }
    }
    .onDisappear { task?.cancel() }
  }

  private func start(_ action: AISuggestionAction) {
    guard task == nil, let section = store.activeSection else { return }
    let envelope = store.envelope
    let selectedRange = selection
    let authorInstruction = action == .custom ? instruction : ""
    preview = nil; error = nil; status = "Connecting to local model…"
    task = Task { @MainActor in
      defer { task = nil }
      do {
        let config: AIProviderConfig
        if aiMode == "local" { config = .managedLocalDefault() }
        else if let configured = envelope.aiProviders.first(where: \.enabled) { config = configured }
        else { throw LocalRuntimeFailure.unavailable("Choose AI setup or configure an AI provider first.") }
        let provider = try NativeAIProviderFactory().provider(from: config)
        preview = try await AISuggestionService.generate(envelope: envelope, section: section, selection: selectedRange, action: action, instruction: authorInstruction, provider: provider, model: config.model) { message in
          await MainActor.run { status = message }
        }
        status = "Ready for your review."
      } catch {
        if !Task.isCancelled { self.error = error.localizedDescription; status = "" }
      }
    }
  }

  private func apply(_ preview: AISuggestionPreview) {
    guard let section = store.envelope.sections.first(where: { $0.id == preview.sectionID }) else { error = "The original chapter no longer exists."; return }
    do {
      let after = try AISuggestionService.replacement(preview, current: section.content ?? "")
      store.selectSection(section.id)
      _ = try store.createSnapshot(label: "Before AI Suggestion")
      store.updateActiveSectionContent(after)
      store.recordAIRevision(sectionID: section.id, providerId: preview.providerID, prompt: preview.prompt, before: preview.source, after: after)
      self.preview = nil; error = nil; status = "Approved suggestion applied."
    } catch { self.error = error.localizedDescription }
  }
}
