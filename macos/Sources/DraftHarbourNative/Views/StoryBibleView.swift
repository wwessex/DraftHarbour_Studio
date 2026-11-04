import AppKit
import DraftHarbourNativeCore
import SwiftUI
import UniformTypeIdentifiers

struct StoryBibleView: View {
  @Bindable var store: ProjectStore
  @State private var selected: BibleEntry?
  @State private var draft = BibleEntryState()
  @State private var fields = ""
  @State private var query = ""
  @State private var category = "all"
  @State private var showArchived = false
  @State private var dirty = false
  @State private var message = ""

  private var entries: [BibleEntry] { store.envelope.bibleEntries }
  private var visible: [BibleEntry] {
    entries.filter { entry in
      let s = entry.state
      return s.archived == showArchived && (category == "all" || s.category == category) &&
        (query.isEmpty || ([s.title, s.body] + s.aliases + s.tags + Array(s.fields.values)).joined(separator: " ").localizedCaseInsensitiveContains(query))
    }
  }
  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      Text("Story facts, ideas and research. Only approved canon is used by AI.").foregroundStyle(.secondary)
      HStack {
        TextField("Search titles, aliases, tags and text", text: $query)
        Picker("Type", selection: $category) {
          Text("All types").tag("all")
          ForEach(BibleEntryState.categories, id: \.self) { Text(label($0)).tag($0) }
        }.frame(width: 190)
        Toggle("Archived", isOn: $showArchived)
        Button("New entry") {
          var entry = BibleEntry(novelId: store.envelope.project.id)
          if category != "all" { entry.state.category = category }
          if ["research", "source"].contains(entry.state.category) { entry.state.status = "research" }
          entry.state.fields = BibleEntryState.templates[entry.state.category] ?? [:]
          select(entry)
          dirty = true
        }.disabled(dirty)
      }
      HStack {
        Button("Import JSON") { importJSON() }.disabled(dirty)
        Button("Export JSON") { export(markdown: false) }
        Button("Export Markdown") { export(markdown: true) }
        Text(message).foregroundStyle(.secondary)
      }
      HStack(alignment: .top, spacing: 16) {
        ScrollView {
          VStack(alignment: .leading, spacing: 8) {
            if visible.isEmpty { Text("No entries found.").foregroundStyle(.secondary) }
            ForEach(visible) { entry in
              Button { select(entry) } label: {
                VStack(alignment: .leading) {
                  Text(entry.state.title).bold()
                  Text("\(label(entry.state.category)) · \(entry.state.status)").font(.caption)
                }.frame(maxWidth: .infinity, alignment: .leading).padding(8)
              }.disabled(dirty)
            }
          }
        }.frame(width: 200)
        Divider()
        if selected != nil {
          ScrollView { editor }
        } else {
          Text("Select an entry or create a new one. Everything can be edited offline.").foregroundStyle(.secondary)
        }
      }.frame(minHeight: 420)
    }.onChange(of: store.envelope.project.id) { _, _ in selected = nil; dirty = false }
  }
  private var editor: some View {
    VStack(alignment: .leading, spacing: 12) {
      TextField("Title", text: $draft.title)
      HStack {
        Picker("Type", selection: $draft.category) {
          ForEach(BibleEntryState.categories, id: \.self) { Text(label($0)).tag($0) }
        }
        Picker("Canon status", selection: $draft.status) {
          ForEach(BibleEntryState.statuses, id: \.self) { Text($0.replacingOccurrences(of: "_", with: " ")).tag($0) }
        }
      }
      TextField("Aliases (comma separated)", text: listBinding(\.aliases))
      TextField("Tags (comma separated)", text: listBinding(\.tags))
      Text("Notes").font(.headline)
      TextEditor(text: $draft.body).frame(minHeight: 130)
      Text("Custom fields — one Name: value per line").font(.headline)
      TextEditor(text: $fields).frame(minHeight: 65)
      aiAccessControls
      TextField("Provenance / evidence", text: $draft.provenance)
      HStack {
        TextField("Valid from (e.g. Chapter 2)", text: $draft.validFrom)
        TextField("Valid until (e.g. Chapter 17)", text: $draft.validTo)
      }
      DisclosureGroup("Linked entries (\(draft.linkedEntryIds.count))") {
        ForEach(entries.filter { $0.id != selected?.id && !$0.state.archived }) { entry in
          Toggle(entry.state.title, isOn: Binding(get: { draft.linkedEntryIds.contains(entry.id) }, set: { value in
            if value { draft.linkedEntryIds.append(entry.id) } else { draft.linkedEntryIds.removeAll { $0 == entry.id } }
          }))
        }
      }
      DisclosureGroup("Backlinks") {
        ForEach(entries.filter { !$0.state.archived && $0.state.linkedEntryIds.contains(selected?.id ?? "") }) { entry in
          Button(entry.state.title) { select(entry) }.disabled(dirty)
        }
      }
      mentions
      HStack {
        Button("Save entry") { save() }.disabled(!dirty || draft.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
        if dirty {
          Button("Discard edits") {
            if let entry = entries.first(where: { $0.id == selected?.id }) { select(entry) }
            else { selected = nil; dirty = false }
          }
          Text("Unsaved edits").foregroundStyle(.secondary)
        } else if let selected, entries.contains(where: { $0.id == selected.id }) {
          Button(draft.archived ? "Unarchive entry" : "Archive entry") {
            var next = draft
            next.archived.toggle()
            commit(next, reason: next.archived ? "Archived" : "Unarchived")
          }
        }
      }
      DisclosureGroup("Version history (\(selected?.revisions.count ?? 0))") {
        ForEach((selected?.revisions ?? []).reversed()) { revision in
          VStack(alignment: .leading) {
            Text("\(Date(timeIntervalSince1970: Double(revision.createdAt) / 1000).formatted()) · \(revision.reason) · \(revision.state.title) (\(revision.state.status))")
            Text(revision.state.body).textSelection(.enabled)
            Button("Restore this version") { commit(revision.state, reason: "Restored revision") }.disabled(dirty)
          }.padding(.vertical, 6)
        }
      }
    }.onChange(of: draft) { _, new in if new != selected?.state { dirty = true } }
      .onChange(of: fields) { old, new in
        if new != fieldText(selected?.state.fields ?? [:]) { dirty = true }
        // Only user changes mark newly named fields hidden; selection loads the saved field text.
        if new != fieldText(selected?.state.fields ?? [:]) {
          let oldNames = Set(fieldNames(old))
          var access = draft.aiAccess ?? BibleAIAccess()
          access.hiddenFields = Array(Set((access.hiddenFields ?? []) + fieldNames(new).filter { !oldNames.contains($0) }.map { "field:" + $0 }))
          draft.aiAccess = access
        }
      }
  }
  private func fieldNames(_ text: String) -> [String] {
    text.components(separatedBy: "\n").compactMap { line in
      guard let colon = line.firstIndex(of: ":") else { return nil }
      let name = String(line[..<colon]).trimmingCharacters(in: .whitespaces)
      return name.isEmpty ? nil : name
    }
  }
  private var aiAccessControls: some View {
    DisclosureGroup("AI reference access") {
      Text("Controls structured references. Facts in manuscript text or other cards remain visible there. New or renamed custom fields start hidden until enabled.").font(.caption)
      Toggle("Allow AI to reference this entry", isOn: Binding(get: { draft.aiAccess?.hidden != true }, set: { value in
        var access = draft.aiAccess ?? BibleAIAccess(); access.hidden = !value; draft.aiAccess = access
      }))
      ForEach(["body", "aliases", "validity"] + Array(Set(fieldNames(fields))).sorted().map { "field:" + $0 }, id: \.self) { key in
        VStack(alignment: .leading) {
          Toggle("Allow " + key.replacingOccurrences(of: "field:", with: ""), isOn: Binding(get: { draft.aiAccess?.hiddenFields?.contains(key) != true }, set: { value in
            var access = draft.aiAccess ?? BibleAIAccess()
            access.hiddenFields = (access.hiddenFields ?? []).filter { $0 != key } + (value ? [] : [key]); draft.aiAccess = access
          }))
          TextField("Only use when (e.g. form=human)", text: Binding(get: { draft.aiAccess?.conditions?[key] ?? "" }, set: { value in
            var access = draft.aiAccess ?? BibleAIAccess(); var conditions = access.conditions ?? [:]; conditions[key] = value; access.conditions = conditions; draft.aiAccess = access
          }))
        }
      }
      Text("Conditions require matching Scene facts in the writing assistant. Missing facts exclude the field; validity notes are never interpreted automatically.").font(.caption)
    }
  }
  private var mentions: some View {
    let matches = EntityOccurrenceServices.find(names: [draft.title] + draft.aliases, sections: store.envelope.sections)
    return DisclosureGroup("Manuscript mentions (\(matches.count))") {
      ForEach(matches) { match in
        Button { store.selectSection(match.sectionID) } label: {
          VStack(alignment: .leading) { Text(match.title).bold(); Text(match.excerpt) }
        }
      }
    }
  }
  private func label(_ value: String) -> String {
    ["plotArc": "Plot Arc", "theme": "Theme / Motif", "research": "Research Note"][value] ?? value.capitalized
  }
  private func listBinding(_ key: WritableKeyPath<BibleEntryState, [String]>) -> Binding<String> {
    Binding(get: { draft[keyPath: key].joined(separator: ",") }, set: { draft[keyPath: key] = $0.components(separatedBy: ",") })
  }
  private func fieldText(_ fields: [String: String]) -> String {
    fields.sorted { $0.key < $1.key }.map { "\($0.key): \($0.value)" }.joined(separator: "\n")
  }
  private func select(_ entry: BibleEntry) {
    selected = entry; draft = entry.state; fields = fieldText(entry.state.fields); dirty = false; message = ""
  }
  private func save() {
    var next = draft
    next.title = next.title.trimmingCharacters(in: .whitespacesAndNewlines)
    next.aliases = next.aliases.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
    next.tags = next.tags.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
    next.fields = [:]
    for line in fields.components(separatedBy: .newlines) where !line.trimmingCharacters(in: .whitespaces).isEmpty {
      guard let colon = line.firstIndex(of: ":"), colon != line.startIndex else { message = "Use one custom field per line: Name: value"; return }
      next.fields[String(line[..<colon]).trimmingCharacters(in: .whitespaces)] = String(line[line.index(after: colon)...]).trimmingCharacters(in: .whitespaces)
    }
    do { for condition in (next.aiAccess?.conditions ?? [:]).values { _ = try BibleAccess.sceneFacts(condition) } }
    catch { message = error.localizedDescription; return }
    commit(next, reason: "Edited")
  }
  private func commit(_ state: BibleEntryState, reason: String) {
    guard var entry = selected else { return }
    if entries.contains(where: { $0.id == entry.id }) { entry.revise(state, reason: reason) } else { entry.state = state }
    store.saveBibleEntry(entry)
    select(entry)
    message = "Saved locally"
  }
  private func importJSON() {
    struct ImportFile: Decodable { var bibleEntries: [BibleEntry] }
    let panel = NSOpenPanel()
    panel.allowedContentTypes = [.json]
    panel.allowsMultipleSelection = false
    guard panel.runModal() == .OK, let url = panel.url else { return }
    let accessed = url.startAccessingSecurityScopedResource()
    defer { if accessed { url.stopAccessingSecurityScopedResource() } }
    do {
      let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
      guard size <= 20 * 1024 * 1024 else { message = "Story Bible imports must be under 20 MiB"; return }
      let file = try JSONDecoder().decode(ImportFile.self, from: Data(contentsOf: url))
      let copies = try BibleEntry.importedCopies(file.bibleEntries, novelId: store.envelope.project.id)
      for entry in copies { store.saveBibleEntry(entry) }
      message = "Imported as new entries"
    } catch { message = "Import failed: \(error.localizedDescription)" }
  }
  private func export(markdown: Bool) {
    let panel = NSSavePanel()
    panel.nameFieldStringValue = markdown ? "story-bible.md" : "story-bible.json"
    panel.allowedContentTypes = markdown ? [.plainText] : [.json]
    guard panel.runModal() == .OK, let url = panel.url else { return }
    do {
      let data: Data
      if markdown { data = Data(BibleEntry.markdown(entries).utf8) }
      else {
        let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        data = try encoder.encode(["bibleEntries": entries])
      }
      try data.write(to: url, options: .atomic)
      message = "Exported"
    } catch { message = "Export failed: \(error.localizedDescription)" }
  }
}
