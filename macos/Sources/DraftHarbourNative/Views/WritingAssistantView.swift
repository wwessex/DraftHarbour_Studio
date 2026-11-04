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
  @State private var sceneFacts = ""
  @State private var providerID = ""
  @State private var task: Task<Void, Never>?
  @State private var generating = false
  @State private var error: String?
  @State private var result = ""
  @State private var copyeditChanges: [CopyeditChange] = []
  @State private var draft: (plan: WritingPlan, sectionID: String, providerID: String)?
  @State private var undo: (sectionID: String, before: String, after: String)?
  @AppStorage("DraftHarbour.aiSetup.mode") private var aiMode = "existing"
  @State private var showSetup = false
  @State private var packageState: LocalAISetup.PackageState = .unchecked
  @State private var localStatus = ""
  @State private var checkingLocal = false
  @State private var selectedAction: WritingAction = .write
  @State private var rewriteTarget: (source: String, range: NSRange)?
  @FocusState private var instructionsFocused: Bool

  private var unchangedCopyedit: Bool {
    guard let draft, draft.plan.action == .copyedit else { return false }
    return result.utf16.elementsEqual((draft.plan.source as NSString).substring(with: draft.plan.range).utf16)
  }
  private var providers: [AIProviderConfig] { store.envelope.aiProviders.filter(\.enabled) }
  private var selectedProviderID: String { providerID.isEmpty ? providers.first?.id ?? "" : providerID }
  private var originalSelectedPassage: String? {
    guard let target = rewriteTarget, let range = Range(target.range, in: target.source) else { return nil }
    return String(target.source[range])
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 8) {
      HStack(spacing: 10) {
        Label("AI writing", systemImage: "sparkles").font(.headline)
        ForEach(WritingAction.allCases, id: \.rawValue) { action in
          Button(action.title) {
            if action == .write {
              captureSelection(); selectedAction = .write; draft = nil; result = ""; error = nil; expanded = true; instructionsFocused = true
            } else { beginAction(action) }
          }
          .help(action.title + " using the current AI model; review before applying")
          .disabled(generating || showSetup || store.activeSection == nil)
        }
        Spacer(minLength: 0)
        if configuredProvider == nil {
          Button("AI setup") { task?.cancel(); showSetup.toggle(); if showSetup { checkLocalPackage() } }.help("Choose and check the AI model")
        }
        if expanded {
          Button("Close") { task?.cancel(); expanded = false; draft = nil; result = ""; sceneFacts = "" }.help("Close the writing preview")
        }
      }
      if showSetup, configuredProvider == nil {
        localSetupPanel
      }
      if !expanded, configuredProvider == nil, aiMode == "existing", let chosen = providers.first(where: { $0.id == selectedProviderID }) {
        Text("Model: \(chosen.label)").font(.caption).foregroundStyle(.secondary)
      }
      if configuredProvider == nil, aiMode == "local" {
        Text("On this computer · verifies and starts when you request a draft").font(.caption).foregroundStyle(.secondary)
      }
      if configuredProvider == nil, aiMode == "later" {
        Text("AI is off. Keep writing, or open AI setup whenever you are ready.").font(.caption).foregroundStyle(.secondary)
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
              .textFieldStyle(.roundedBorder).lineLimit(2...4).focused($instructionsFocused)
            TextField("Scene facts (optional): form=human, timeline=before", text: $sceneFacts).textFieldStyle(.roundedBorder).disabled(generating)
            if selectedAction.replacesPassage {
              Text(rewriteTarget == nil ? "Target: final paragraph (no text selected)." : "Target: selected text only.").font(.caption)
              if let originalSelectedPassage { Text(originalSelectedPassage).font(.callout).textSelection(.enabled) }
            }
            Text("Uses relevant Story Bible canon when available. Rewrite selected text or the final paragraph. Continue adds after the ending. Review before applying.")
              .font(.caption).foregroundStyle(.secondary)
            if generating {
              HStack { ProgressView().controlSize(.small); Text("Generating…"); Button("Stop") { task?.cancel() } }
            }
            if let error { Text(error).foregroundStyle(.red) }
            if let draft {
              if draft.plan.action == .copyedit {
                if unchangedCopyedit {
                  Text("No corrections proposed. The text is unchanged. Use Rewrite for style, pacing or stronger wording.")
                } else {
                  Text("\(copyeditChanges.count) correction(s) proposed. Review the exact changes below.")
                  ForEach(copyeditChanges.indices, id: \.self) { index in
                    VStack(alignment: .leading) {
                      Text("Original: ") + Text(quoted(copyeditChanges[index].before)).strikethrough()
                      Text("Corrected: ") + Text(copyeditChanges[index].after.isEmpty ? "(deleted)" : quoted(copyeditChanges[index].after)).underline().bold()
                    }.textSelection(.enabled)
                  }
                  Text("Corrected passage").font(.caption)
                }
              }
              if !unchangedCopyedit { Text(result).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }
              HStack {
                Button(draft.plan.action.replacesPassage ? "Replace Passage" : "Append to Chapter", action: apply)
                  .disabled(generating || unchangedCopyedit)
                Button("Discard") { self.draft = nil; result = "" }
              }
            }
            if undo != nil { Button("Undo AI Change", action: undoChange) }
          }
        }.frame(maxHeight: 220)
        HStack {
          Button("Generate draft") { beginAction(selectedAction, useCapturedTarget: true) }
            .buttonStyle(.borderedProminent)
            .disabled(generating || showSetup || checkingLocal || (selectedAction == .write && direction.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty))
          Text("Action: \(selectedAction.title)").font(.caption).foregroundStyle(.secondary)
        }
      }
    }
    .padding(10)
    .background(.quaternary.opacity(0.35))
    .onChange(of: store.activeSectionID) { _, _ in
      task?.cancel()
      draft = nil
      result = ""
      direction = ""
      sceneFacts = ""
      undo = nil
      error = nil
      rewriteTarget = nil
      selectedAction = .write
    }
    .onAppear {
      guard configuredProvider == nil else { return }
      if LocalAISetup.needsFirstRun(storedMode: UserDefaults.standard.string(forKey: "DraftHarbour.aiSetup.mode"), hasEnabledProviders: !providers.isEmpty) {
        aiMode = "later"; showSetup = true; checkLocalPackage()
      }
    }
    .onChange(of: aiMode) { _, _ in
      task?.cancel(); draft = nil; result = ""; expanded = false
    }
    .onDisappear { task?.cancel() }
  }

  private var localSetupPanel: some View {
    VStack(alignment: .leading, spacing: 8) {
      ScrollView {
        VStack(alignment: .leading, spacing: 8) {
          Text("Local AI setup").font(.headline)
          Text("Writing works without AI. Setup never changes your manuscript or enables an online provider.").font(.caption)
          Text(LocalAISetup.requirements).font(.caption)
          Text(LocalAISetup.resources).font(.caption).foregroundStyle(.secondary)
          Text(packageState.message).font(.caption).accessibilityIdentifier("localAI.packageStatus")
          HStack {
            Button("Install local package…", action: installPackage).disabled(checkingLocal || generating)
            Button("Check installed package", action: checkLocalPackage).disabled(checkingLocal || generating)
            Button("Restore previous package…", action: restorePackage).disabled(checkingLocal || generating)
          }
          if !localStatus.isEmpty { Text(localStatus).font(.caption).textSelection(.enabled) }
          if checkingLocal { ProgressView("Checking local package…").controlSize(.small) }
          HStack {
            Button("Use Narratryx on this computer") {
              task?.cancel(); draft = nil; result = ""; expanded = false
              aiMode = "local"; showSetup = false
            }.disabled(checkingLocal || !packageState.canEnable || generating)
            Button("Online AI — coming soon") {}.disabled(true)
          }
          Text(aiMode == "local" ? "Local mode selected. No online fallback is used; requests verify the package again." : "Installing or restoring a package does not enable AI. Choose Use Narratryx on this computer after verification.").font(.caption)
          Text(LocalAISetup.recovery).font(.caption).foregroundStyle(.secondary)
          if let configure {
            Button("Use an existing connection…") { task?.cancel(); NativeLocalModelRuntime.shared.stopNow(); aiMode = "existing"; configure() }.disabled(checkingLocal)
          }
        }.frame(maxWidth: .infinity, alignment: .leading)
      }.frame(maxHeight: 300)
      Button("Continue writing without AI") {
        task?.cancel(); NativeLocalModelRuntime.shared.stopNow()
        draft = nil; result = ""; expanded = false; aiMode = "later"; showSetup = false
      }
    }
  }

  @MainActor
  private func refreshPackageState() async {
    packageState = await Task.detached { LocalAISetup.inspect() }.value
  }

  @MainActor
  private func checkLocalPackage() {
    guard !checkingLocal else { return }
    checkingLocal = true; localStatus = ""
    Task { @MainActor in
      await refreshPackageState()
      checkingLocal = false
    }
  }

  @MainActor
  private func installPackage() {
    let picker = NSOpenPanel()
    picker.title = "Choose an already obtained verified Narratryx package"
    picker.message = "Select the complete package folder containing manifest.json. The model is not bundled with the app; this does not download it."
    picker.canChooseFiles = false; picker.canChooseDirectories = true; picker.allowsMultipleSelection = false
    guard picker.runModal() == .OK, let source = picker.url else { return }
    checkingLocal = true; localStatus = "Verifying package and checking storage…"
    Task { @MainActor in
      defer { checkingLocal = false }
      do {
        let plan = try await Task.detached { try LocalModelInstaller.plan(source: source) }.value
        let alert = NSAlert()
        alert.messageText = "Install verified local AI package?"
        alert.informativeText = "Model: \(plan.model)\nCopy: \(ByteCountFormatter.string(fromByteCount: Int64(plan.packageBytes), countStyle: .file)); free: \(ByteCountFormatter.string(fromByteCount: Int64(plan.availableBytes), countStyle: .file)).\nRequired free space: \(ByteCountFormatter.string(fromByteCount: Int64(plan.requiredBytes), countStyle: .file)) (copy plus reserve).\nRAM: \(plan.physicalMemory / 1_073_741_824) GiB (8 GiB rejection floor; tested on one 16 GB Mac, not a performance guarantee).\n\nInstall this copy and retain an existing verified package for recovery? The source folder is kept. AI is not enabled by installation. Keep the app open during installation. No training or key entry is needed."
        alert.addButton(withTitle: "Install"); alert.addButton(withTitle: "Cancel")
        guard alert.runModal() == .alertFirstButtonReturn else { localStatus = "Installation cancelled. The installed package is unchanged."; return }
        localStatus = "Copying and verifying the local package…"
        let model = try await NativeLocalModelRuntime.shared.install(from: source)
        draft = nil; result = ""
        await refreshPackageState()
        localStatus = "Installed \(model). Choose Use Narratryx on this computer to enable it, or continue writing without AI."
      } catch {
        await refreshPackageState()
        localStatus = "Installation failed: \(error.localizedDescription) " + LocalAISetup.recovery
      }
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
        draft = nil; result = ""
        await refreshPackageState()
        localStatus = "Restored \(model). Installation does not change your AI mode."
      } catch {
        await refreshPackageState()
        localStatus = "Restore unavailable: \(error.localizedDescription) " + LocalAISetup.recovery
      }
    }
  }

  @MainActor
  private func captureSelection(clearIfEmpty: Bool = false) {
    guard let source = store.activeSection?.content else { return }
    let range = editorSelection()
    if range.length > 0 { rewriteTarget = (source, range) }
    else if clearIfEmpty { rewriteTarget = nil }
  }

  @MainActor
  private func beginAction(_ action: WritingAction, useCapturedTarget: Bool = false) {
    guard !generating, task == nil else { return }
    guard let section = store.activeSection else { return }
    do {
      if !useCapturedTarget { captureSelection(clearIfEmpty: true) }
      let source = section.content ?? ""
      if action.replacesPassage, let target = rewriteTarget, target.source != source {
        throw LocalRuntimeFailure.unavailable("The chapter changed. Select the passage again before rewriting.")
      }
      // Freeze the plan before expanding controls or scheduling an async task.
      let plan = try WritingActions.prepare(action, source: source,
        selection: action.replacesPassage ? rewriteTarget?.range : nil, direction: direction)
      selectedAction = action; expanded = true
      task = Task { await generate(plan, sectionID: section.id) }
    } catch { expanded = true; self.error = error.localizedDescription }
  }

  @MainActor
  private func generate(_ plan: WritingPlan, sectionID: String) async {
    guard let section = store.activeSection, section.id == sectionID, (section.content ?? "") == plan.source else {
      error = "The chapter changed. Generate again before applying a suggestion."; task = nil; return
    }
    generating = true
    error = nil
    draft = nil
    result = ""
    defer { generating = false; task = nil }
    do {
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
        context: plan.action.replacesPassage ? AIWorkflowServices.storyBibleReferences(envelope: store.envelope, query: plan.prompt, scene: try BibleAccess.sceneFacts(sceneFacts)) : AIWorkflowServices.buildStoryContext(envelope: store.envelope, section: section, scene: try BibleAccess.sceneFacts(sceneFacts)),
        projectType: store.projectType, sectionTitle: section.title, model: config.model))
      guard !Task.isCancelled else { return }
      guard !response.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        throw DraftHarbourError.providerNotConfigured("The model returned no passage to review.")
      }
      if plan.action == .copyedit {
        let reviewed = try WritingActions.copyeditReview(plan, json: response.text)
        result = reviewed.text; copyeditChanges = reviewed.changes
      } else { result = response.text; copyeditChanges = [] }
      draft = (plan, section.id, response.provider)
    } catch {
      if !Task.isCancelled { self.error = error.localizedDescription }
    }
  }

  private func quoted(_ text: String) -> String {
    guard let data = try? JSONEncoder().encode(text), let value = String(data: data, encoding: .utf8) else { return text }
    return value
  }

  private func apply() {
    guard let draft, !unchangedCopyedit else { return }
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
