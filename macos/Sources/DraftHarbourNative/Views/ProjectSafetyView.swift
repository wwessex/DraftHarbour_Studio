import DraftHarbourNativeCore
import SwiftUI

struct ProjectSafetyView: View {
  @Bindable var store: ProjectStore
  var restoreCopy: (DhprojEnvelope) -> Void
  private let service = ProjectSafetyService()
  @State private var backups: [VerifiedProjectBackup] = []
  @State private var name = ""
  @State private var error: String?

  var body: some View {
    VStack(alignment: .leading, spacing: 14) {
      Text("Backups, Recovery & Trash").font(.title2)
      Text("Includes manuscript, snapshots, comments, story bible, research notes and blueprint. Local copies share this device; export a copy for protection against device loss.")
        .foregroundStyle(.secondary)
      HStack {
        TextField("Backup name (optional)", text: $name)
        Button("Create Verified Backup") {
          perform { _ = try service.save(store.envelope, label: name.isEmpty ? "Manual" : name); try refresh() }
        }
      }
      List {
        SwiftUI.Section("Project backups · newest ten automatic copies, all manual copies") {
          ForEach(backups) { backup in
            HStack {
              VStack(alignment: .leading) {
                Text(backup.automatic ? "Automatic" : backup.label)
                Text(Date(timeIntervalSince1970: Double(backup.createdAt) / 1000).formatted()).font(.caption)
              }
              Spacer()
              Button("Restore as New Project") { perform { restoreCopy(try service.restore(backup)) } }
            }
          }
        }
        SwiftUI.Section("Trash · restores into a new chapter") {
          ForEach(store.envelope.deletedSections) { entry in
            HStack {
              Text(entry.section.title)
              Spacer()
              Button("Recover Chapter") { perform { _ = try store.restoreDeletedSection(id: entry.id) } }
            }
          }
        }
      }
      if let error { Text(error).foregroundStyle(.red).textSelection(.enabled) }
    }
    .padding(20).frame(minWidth: 650, minHeight: 460)
    .onAppear { perform { try refresh() } }
  }
  private func refresh() throws { backups = try service.list(projectID: store.envelope.project.id) }
  private func perform(_ action: () throws -> Void) {
    do { try action(); error = nil } catch { self.error = error.localizedDescription }
  }
}

struct RecoveryComparisonView: View {
  let saved: DhprojEnvelope
  let recovery: RecoverySnapshot
  var restore: () -> Void
  var later: () -> Void
  var body: some View {
    VStack(alignment: .leading, spacing: 14) {
      Text("Recover Unsaved Writing").font(.title2)
      Text("Recovery opens a separate project file and keeps the current document.")
      HSplitView {
        textColumn("Saved", saved)
        textColumn("Recovered", recovery.envelope)
      }
      HStack { Button("Later", action: later); Spacer(); Button("Recover as New Project", action: restore).buttonStyle(.borderedProminent) }
    }.padding(20).frame(minWidth: 760, minHeight: 450)
  }
  private func textColumn(_ title: String, _ envelope: DhprojEnvelope) -> some View {
    VStack(alignment: .leading) {
      Text(title).font(.headline)
      ScrollView { Text(envelope.sections.map { $0.title + "\n" + ($0.content ?? "") }.joined(separator: "\n\n")).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }
    }.padding(8)
  }
}
