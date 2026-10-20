import AppKit
import DraftHarbourNativeCore
import SwiftUI

struct EditorWorkspaceView: View {
  @Bindable var store: ProjectStore
  @Binding var selectedRange: NSRange
  @Binding var showingFindReplace: Bool
  var addComment: () -> Void = {}
  var createSnapshot: () -> Void = {}
  var reviseSelection: () -> Void = {}
  var translateSelection: () -> Void = {}
  var shareSelection: () -> Void = {}
  var copyMarkdown: () -> Void = {}
  var configureAI: () -> Void = {}
  @AppStorage("DraftHarbour.editor.fontSize") private var fontSize = 15.0
  @AppStorage("DraftHarbour.editor.fontFamily") private var fontFamily = "System"
  @AppStorage("DraftHarbour.editor.lineHeight") private var lineHeight = 1.5
  @AppStorage("DraftHarbour.editor.pageView") private var pageView = false
  @AppStorage("DraftHarbour.editor.typewriterMode") private var typewriterMode = false
  @State private var operationError: String?
  @State private var screenplayMode = false

  var body: some View {
    VStack(spacing: 0) {
      if showingFindReplace {
        FindReplaceBar(store: store, isPresented: $showingFindReplace, selectedRange: $selectedRange)
        Divider()
      }
      if let section = store.activeSection {
        header(section: section)
        WritingAssistantView(store: store, editorSelection: { selectedRange }, configure: configureAI)
          .id(section.id)
        Divider()
        HStack(spacing: 0) {
          if pageView {
            Spacer(minLength: 24)
          }
          DraftEditorView(
            text: Binding(get: {
              store.activeSection?.content ?? ""
            }, set: { value in
              store.updateActiveSectionContent(value)
            }),
            selectedRange: $selectedRange,
            screenplayMode: screenplayMode || store.projectType == .screenplay,
            typewriterMode: typewriterMode,
            fontSize: fontSize,
            fontFamily: fontFamily,
            lineHeight: lineHeight,
            addComment: addComment,
            createSnapshot: createSnapshot,
            reviseSelection: reviseSelection,
            translateSelection: translateSelection,
            shareSelection: shareSelection,
            copyMarkdown: copyMarkdown
          )
          .frame(maxWidth: pageView ? 820 : .infinity)
          if pageView {
            Spacer(minLength: 24)
          }
        }
        .background(pageView ? AnyShapeStyle(.quaternary) : AnyShapeStyle(.clear))
      } else {
        ContentUnavailableView("No Section Selected", systemImage: "doc.text.magnifyingglass")
      }
    }
    .alert("Chapter Operation", isPresented: Binding(get: { operationError != nil }, set: { if !$0 { operationError = nil } })) {
      Button("OK", role: .cancel) {}
    } message: { Text(operationError ?? "") }
    .onAppear {
      screenplayMode = store.projectType == .screenplay
    }
  }

  private func header(section: DraftHarbourNativeCore.Section) -> some View {
    HStack(spacing: 12) {
      TextField("Section Title", text: Binding(get: {
        section.title
      }, set: { title in
        store.updateActiveSectionTitle(title)
      }))
      .textFieldStyle(.plain)
      .font(.system(size: 22, weight: .semibold))

      Text("\(MarkdownTools.wordCount(section.content ?? "")) words")
        .font(.caption)
        .foregroundStyle(.secondary)

      Spacer()
      Button("Split at Cursor") {
        do { _ = try store.splitActiveSection(atUTF16: selectedRange.location); selectedRange = NSRange(location: 0, length: 0) }
        catch { operationError = "Choose a cursor inside the chapter, outside a comment anchor. " + error.localizedDescription }
      }
      Button("Merge Next") {
        do { try store.mergeActiveSectionWithNext() }
        catch { operationError = error.localizedDescription }
      }.disabled(store.envelope.sections.last?.id == section.id)

      formattingButton("bold", command: .bold)
      formattingButton("italic", command: .italic)
      formattingButton("underline", command: .underline)
      formattingButton("quote.bubble", command: .blockquote)

      Picker("Status", selection: Binding(get: {
        section.status
      }, set: { status in
        store.updateActiveSectionStatus(status)
      })) {
        ForEach(ChapterStatus.allCases, id: \.self) { status in
          Text(status.rawValue.capitalized).tag(status)
        }
      }
      .frame(width: 130)

      Toggle("Page", isOn: $pageView)
        .toggleStyle(.button)
        .help("Toggle page view")

      Toggle("Typewriter", isOn: $typewriterMode)
        .toggleStyle(.button)
        .help("Toggle typewriter mode")

      if store.projectType == .screenplay {
        Toggle("Screenplay", isOn: $screenplayMode)
          .toggleStyle(.button)
          .help("Use screenplay editor styling")
      }
    }
    .padding(16)
  }

  private func formattingButton(_ image: String, command: MarkdownTextCommand) -> some View {
    Button {
      store.applyMarkdownCommand(command, range: selectedRange)
    } label: {
      Image(systemName: image)
    }
    .buttonStyle(.borderless)
  }
}
