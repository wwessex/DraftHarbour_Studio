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
  @AppStorage("DraftHarbour.aiSetup.mode") private var aiMode = "existing"
  @State private var showSetup = false
  @State private var localStatus = "Local model package has not been checked."
  @State private var checkingLocal = false

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
          .disabled(generating || showSetup || store.activeSection == nil)
        }
        Spacer(minLength: 0)
        if configuredProvider == nil {
          Button("AI setup") { task?.cancel(); showSetup.toggle() }
        }
        if expanded {
          Button("Close") { task?.cancel(); expanded = false; draft = nil; result = "" }
        }
      }
      if showSetup, configuredProvider == nil {
        VStack(alignment: .leading, spacing: 8) {
          Text("Choose how AI runs. Your writing stays on this computer unless you explicitly use an online connection.").font(.caption)
          HStack {
            Button("On this computer") {
              task?.cancel(); aiMode = "local"; checkingLocal = true
              Task {
                do {
                  let model = try await NativeLocalModelRuntime.shared.inspect()
                  localStatus = "Verified \(model). Starts when you request a draft."
                } catch { localStatus = "Local AI unavailable: \(error.localizedDescription) No text was sent online." }
                checkingLocal = false
              }
            }.disabled(checkingLocal)
            Button("Online AI — coming soon") {}.disabled(true)
            Button("Decide later") { task?.cancel(); NativeLocalModelRuntime.shared.stopNow(); aiMode = "later" }
              .disabled(checkingLocal)
          }
          HStack {
            Button("Install local package…", action: installPackage).disabled(checkingLocal || generating)
            Button("Restore previous package…", action: restorePackage).disabled(checkingLocal || generating)
          }
          Text(localStatus).font(.caption)
          if checkingLocal { ProgressView().controlSize(.small) }
          if aiMode == "later" { Text("AI is off. You can keep writing and return to setup at any time.").font(.caption) }
          Text("Install only a reviewed local package. Online sign-in is still in development. No training or user-entered key is required by the managed local runtime.").font(.caption).foregroundStyle(.secondary)
          if let configure {
            Button("Use an existing connection…") { task?.cancel(); NativeLocalModelRuntime.shared.stopNow(); aiMode = "existing"; configure() }.disabled(checkingLocal)
          }
        }
      }
      if !expanded, configuredProvider == nil, aiMode == "existing", let chosen = providers.first(where: { $0.id == selectedProviderID }) {
        Text("Model: \(chosen.label)").font(.caption).foregroundStyle(.secondary)
      }
      if configuredProvider == nil, aiMode == "local" {
        Text("On this computer · verifies and starts when you request a draft").font(.caption).foregroundStyle(.secondary)
      }
      if expanded {
        ScrollView {
          VStack(alignment: .leading, spacing: 8) {
            if configuredProvider == nil, aiMode == "existing" {
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
  private func installPackage() {
    let picker = NSOpenPanel()
    picker.title = "Choose a verified local model folder"
    picker.canChooseFiles = false; picker.canChooseDirectories = true; picker.allowsMultipleSelection = false
    guard picker.runModal() == .OK, let source = picker.url else { return }
    checkingLocal = true; localStatus = "Verifying package and checking storage…"
    Task { @MainActor in
      defer { checkingLocal = false }
      do {
        let plan = try await Task.detached { try LocalModelInstaller.plan(source: source) }.value
        let alert = NSAlert()
        alert.messageText = "Install verified local AI package?"
        alert.informativeText = "Model: \(plan.model)\nCopy: \(ByteCountFormatter.string(fromByteCount: Int64(plan.packageBytes), countStyle: .file)); free: \(ByteCountFormatter.string(fromByteCount: Int64(plan.availableBytes), countStyle: .file)).\nRAM: \(plan.physicalMemory / 1_073_741_824) GiB (8 GiB floor; tested on a 16 GB Mac).\n\nReplace the active package and retain one verified previous package? Keep the app open during installation. No training or key entry is needed."
        alert.addButton(withTitle: "Install"); alert.addButton(withTitle: "Cancel")
        guard alert.runModal() == .alertFirstButtonReturn else { localStatus = "Installation cancelled. The installed package is unchanged."; return }
        localStatus = "Copying and verifying the local package…"
        let model = try await NativeLocalModelRuntime.shared.install(from: source)
        draft = nil; result = ""
        localStatus = "Installed \(model). Choose On this computer to use it."
      } catch { localStatus = "Installation unavailable: \(error.localizedDescription)" }
    }
  }

  @MainActor
  private func restorePackage() {
    checkingLocal = true; localStatus = "Checking the previous package…"
    Task { @MainActor in
      defer { checkingLocal = false }
      do {
        let model = try await Task.detached { try LocalRuntimePackage.verify(LocalModelInstaller.previousURL(for: NativeLocalModelRuntime.packageURL)).model_id }.value
        let alert = NSAlert()
        alert.messageText = "Restore previous local model?"
        alert.informativeText = "Restore \(model)? The active verified package will be retained as the previous package."
        alert.addButton(withTitle: "Restore"); alert.addButton(withTitle: "Cancel")
        guard alert.runModal() == .alertFirstButtonReturn else { localStatus = "Restore cancelled. The installed package is unchanged."; return }
        _ = try await NativeLocalModelRuntime.shared.restorePrevious()
        draft = nil; result = ""; localStatus = "Restored \(model). Choose On this computer to use it."
      } catch { localStatus = "Restore unavailable: \(error.localizedDescription)" }
    }
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
      else if aiMode == "local" {
        config = AIProviderConfig(id: "managed-local", provider: .customLLM, label: "On this computer (experimental)",
          endpoint: NativeLocalModelRuntime.endpoint, model: NativeLocalModelRuntime.modelID)
      }
      else if aiMode == "later" { throw LocalRuntimeFailure.unavailable("AI is off. Choose AI setup when you are ready.") }
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
