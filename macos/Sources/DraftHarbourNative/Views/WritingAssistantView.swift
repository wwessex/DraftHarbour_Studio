import DraftHarbourNativeCore
import SwiftUI

/// The same passage workflow in the manuscript workspace and advanced AI panel.
struct WritingAssistantView: View {
  @Bindable var store: ProjectStore
  var editorSelection: () -> NSRange
  var configuredProvider: (() throws -> AIProviderConfig)?
  var configure: (() -> Void)?
  @State private var expanded = false
  @State private var direction = ""
  @State private var providerID = ""
  @State private var task: Task<Void, Never>?
  @State private var generating = false
  @State private var error: String?
  @State private var result = ""
  @State private var draft: (plan: WritingPlan, sectionID: String, providerID: String)?
  @State private var undo: (sectionID: String, before: String, after: String)?

  private var providers: [AIProviderConfig] { store.envelope.aiProviders.filter(\.enabled) }
  private var selectedProviderID: String { providerID.isEmpty ? providers.first?.id ?? "" : providerID }

  var body: some View {
    VStack(alignment: .leading, spacing: 8) {
      HStack(spacing: 10) {
        Label("AI writing", systemImage: "sparkles").font(.headline)
        ForEach(WritingAction.allCases, id: \.rawValue) { action in
          Button(action.title) {
            expanded = true
            if action != .write || !direction.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
              task = Task { await generate(action) }
            }
          }
          .disabled(generating || store.activeSection == nil)
        }
        Spacer(minLength: 0)
        if expanded {
          Button("Close") { task?.cancel(); expanded = false; draft = nil; result = "" }
        }
      }
      if !expanded, configuredProvider == nil, let chosen = providers.first(where: { $0.id == selectedProviderID }) {
        Text("Model: \(chosen.label)").font(.caption).foregroundStyle(.secondary)
      }
      if expanded {
        ScrollView {
          VStack(alignment: .leading, spacing: 8) {
            if configuredProvider == nil {
              if !providers.isEmpty {
                Picker("AI model", selection: Binding(get: { selectedProviderID }, set: { providerID = $0 })) {
                  ForEach(providers) { provider in Text(provider.label).tag(provider.id) }
                }
              } else {
                Text("Connect a model once to start writing with AI.").font(.caption)
                if let configure { Button("Connect AI model", action: configure) }
              }
            }
            TextField("Instructions (required for Write)", text: $direction, axis: .vertical)
              .textFieldStyle(.roundedBorder).lineLimit(2...4)
            Text("Rewrite selected text or the final paragraph. Continue adds after the ending. Review before applying.")
              .font(.caption).foregroundStyle(.secondary)
            if generating {
              HStack { ProgressView().controlSize(.small); Text("Generating…"); Button("Stop") { task?.cancel() } }
            }
            if let error { Text(error).foregroundStyle(.red) }
            if let draft {
              Text(result).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading)
              HStack {
                Button(draft.plan.action == .rewrite ? "Replace Passage" : "Append to Chapter", action: apply)
                  .disabled(generating)
                Button("Discard") { self.draft = nil; result = "" }
              }
            }
            if undo != nil { Button("Undo AI Change", action: undoChange) }
          }
        }.frame(maxHeight: 220)
      }
    }
    .padding(10)
    .background(.quaternary.opacity(0.35))
    .onChange(of: store.activeSectionID) { _, _ in
      task?.cancel()
      draft = nil
      result = ""
      direction = ""
      undo = nil
      error = nil
    }
    .onDisappear { task?.cancel() }
  }

  @MainActor
  private func generate(_ action: WritingAction) async {
    guard let section = store.activeSection else { return }
    generating = true
    error = nil
    draft = nil
    result = ""
    defer { generating = false; task = nil }
    do {
      let plan = try WritingActions.prepare(action, source: section.content ?? "", selection: editorSelection(), direction: direction)
      let config: AIProviderConfig
      if let configuredProvider { config = try configuredProvider() }
      else if let selected = providers.first(where: { $0.id == selectedProviderID }) { config = selected }
      else { throw DraftHarbourError.providerNotConfigured("Connect an AI model first.") }
      let provider = try NativeAIProviderFactory().provider(from: config)
      let response = try await provider.generate(AIRequest(prompt: plan.prompt,
        context: AIWorkflowServices.buildStoryContext(envelope: store.envelope, section: section),
        projectType: store.projectType, sectionTitle: section.title, model: config.model))
      guard !Task.isCancelled else { return }
      guard !response.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        throw DraftHarbourError.providerNotConfigured("The model returned no passage to review.")
      }
      result = response.text
      draft = (plan, section.id, response.provider)
    } catch {
      if !Task.isCancelled { self.error = error.localizedDescription }
    }
  }

  private func apply() {
    guard let draft else { return }
    do {
      guard store.activeSection?.id == draft.sectionID else { throw DraftHarbourError.invalidSelection }
      let before = store.activeSection?.content ?? ""
      let after = try WritingActions.applying(draft.plan, current: before, output: result)
      try store.createSnapshot(label: "Before AI \(draft.plan.action.title)")
      store.updateActiveSectionContent(after)
      store.recordAIRevision(sectionID: draft.sectionID, providerId: draft.providerID, prompt: draft.plan.prompt, before: before, after: after)
      undo = (draft.sectionID, before, after)
      self.draft = nil
      result = ""
    } catch { self.error = error.localizedDescription }
  }

  private func undoChange() {
    guard let undo else { return }
    guard store.activeSection?.id == undo.sectionID, store.activeSection?.content == undo.after else {
      error = "The chapter changed. Use a snapshot or the revision log to recover earlier text."
      return
    }
    store.updateActiveSectionContent(undo.before)
    self.undo = nil
  }
}
