import Foundation
import DraftHarbourNativeCore
import XCTest
import ZIPFoundation

final class ProjectSafetyTests: XCTestCase {
  func testBackupMetadataCannotRedirectRotationToAnotherFile() throws {
    let folder = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: folder) }
    let service = ProjectSafetyService(directory: folder)
    let envelope = DhprojCodec.newProject(title: "Rotation boundary")
    let backup = try service.save(envelope)
    let projectFolder = try XCTUnwrap(FileManager.default.contentsOfDirectory(at: folder, includingPropertiesForKeys: nil).first)
    let record = projectFolder.appendingPathComponent(backup.id + ".json")
    for invalidID in ["../../unrelated", UUID().uuidString] {
      var damaged = backup
      damaged.id = invalidID
      try JSONEncoder().encode(damaged).write(to: record, options: .atomic)
      XCTAssertThrowsError(try service.list(projectID: envelope.project.id))
      XCTAssertTrue(FileManager.default.fileExists(atPath: record.path))
    }
  }

  func testRecoveryIdentifierCannotEscapeItsDirectory() {
    let folder = FileManager.default.temporaryDirectory.appendingPathComponent("RecoverySandbox")
    let service = SessionRecoveryService(baseDirectory: folder)
    XCTAssertEqual(service.recoveryURL(projectId: "../../outside").deletingLastPathComponent().path, folder.path)
    XCTAssertEqual(service.recoveryURL(projectId: "valid-project").lastPathComponent, "valid-project.recovery.json")
  }

  func testTrashPreservesManuscriptSnapshotsAndComments() throws {
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Safety"))
    store.updateActiveSectionContent("Alice arrived.")
    let section = try XCTUnwrap(store.activeSection)
    _ = try store.createSnapshot(label: "Milestone")
    _ = try store.addComment(text: "Keep", from: 0, to: 5)
    try store.deleteSection(id: section.id)
    let entry = try XCTUnwrap(store.envelope.deletedSections.first)
    XCTAssertEqual(entry.snapshots.count, 1)
    let restored = try store.restoreDeletedSection(id: entry.id)
    XCTAssertEqual(restored.content, "Alice arrived.")
    XCTAssertNotEqual(restored.id, section.id)
    XCTAssertTrue(store.envelope.commentThreads.contains { $0.chapterId == restored.id })
    XCTAssertEqual(store.envelope.deletedSections.count, 0)
    XCTAssertEqual(try DhprojCodec.decode(DhprojCodec.encode(store.envelope)).sections, store.envelope.sections)
  }

  func testSplitMergeAndSceneMovementPreserveWriting() throws {
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Operations"))
    store.updateActiveSectionContent("Alice\nBob")
    let left = try XCTUnwrap(store.activeSectionID)
    let scene = try store.createScene(initialData: Scene(title: "Arrival", summary: "Keep all metadata", tags: ["port"], wordGoal: 100))
    _ = try store.addComment(text: "Right", from: 6, to: 9)
    let right = try store.splitActiveSection(atUTF16: 6)
    XCTAssertEqual(right.content, "Bob")
    XCTAssertEqual(store.envelope.commentThreads.first?.anchor.from, 0)
    try store.moveScene(sceneID: scene.id, from: left, to: right.id)
    XCTAssertEqual(store.activeSection?.scenes.first, scene)
    store.selectSection(left)
    try store.mergeActiveSectionWithNext()
    XCTAssertTrue(store.activeSection?.content?.contains("Bob") == true)
    XCTAssertEqual(store.activeSection?.scenes.first, scene)
    XCTAssertEqual(store.envelope.deletedSections.count, 1)
  }

  func testCrossingCommentBlocksSplitAndRestoreKeepsSafetyVersion() throws {
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Anchors"))
    store.updateActiveSectionContent("abcdef")
    _ = try store.addComment(text: "Crossing", from: 1, to: 5)
    XCTAssertThrowsError(try store.splitActiveSection(atUTF16: 3))
    let snapshot = try store.createSnapshot(label: "Old")
    store.updateActiveSectionContent("New writing")
    try store.restoreSnapshot(id: snapshot.id)
    XCTAssertEqual(store.activeSection?.content, "abcdef")
    XCTAssertTrue(store.envelope.snapshots.contains { $0.label == "Before restore" && $0.doc == "New writing" })
  }

  func testAutomaticSnapshotsAreBoundedAndDeduplicated() throws {
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Retention"))
    _ = try store.createSnapshot(label: "Manual")
    for index in 0..<35 { store.updateActiveSectionContent("Draft \(index)"); try store.createAutoSnapshotForActiveSection() }
    try store.createAutoSnapshotForActiveSection()
    XCTAssertEqual(store.envelope.snapshots.filter { $0.label == "Auto" }.count, 30)
    XCTAssertEqual(store.envelope.snapshots.filter { $0.label == "Manual" }.count, 1)
  }

  func testBackupsRotateVerifyAndRestoreNewProject() throws {
    let folder = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: folder) }
    let service = ProjectSafetyService(directory: folder)
    var envelope = DhprojCodec.newProject(title: "Backup")
    let manual = try service.save(envelope, label: "Milestone")
    for index in 0..<12 { envelope.sections[0].content = "Version \(index)"; _ = try service.save(envelope, automatic: true) }
    _ = try service.save(envelope, automatic: true)
    XCTAssertEqual(try service.list(projectID: envelope.project.id).count, 11)
    let copy = try service.restore(manual)
    XCTAssertNotEqual(copy.project.id, envelope.project.id)
    XCTAssertNotEqual(copy.sections[0].id, envelope.sections[0].id)
    var damaged = manual; damaged.projectData.append(0)
    XCTAssertThrowsError(try service.restore(damaged))
  }

  func testAlignedDiffAndWholeNameEvidence() {
    let diff = SnapshotDiffServices.diff(old: "First\nLast", new: "First\nInserted\nLast")
    XCTAssertEqual(diff.filter { $0.kind == .removed }.count, 0)
    XCTAssertEqual(diff.filter { $0.kind == .added }.map(\.text), ["Inserted"])
    let section = Section(novelId: "n", order: 0, title: "Evidence", content: "Al met Alice. Malice stayed away.")
    XCTAssertEqual(EntityOccurrenceServices.find(names: ["Alice", "Al"], sections: [section]).count, 2)
  }

  func testReplacementContainingQueryTerminates() {
    let store = ProjectStore(envelope: DhprojCodec.newProject(title: "Replace"))
    store.updateActiveSectionContent("a a")
    XCTAssertEqual(store.replaceInActiveSection(query: "a", replacement: "aa"), 2)
    XCTAssertEqual(store.activeSection?.content, "aa aa")
  }

  func testLegacyImportAndEPUBStructure() throws {
    let envelope = DhprojCodec.newProject(title: "Escape & <Title>")
    var object = try XCTUnwrap(JSONSerialization.jsonObject(with: DhprojCodec.encode(envelope)) as? [String: Any])
    var sections = try XCTUnwrap(object["sections"] as? [[String: Any]])
    sections[0]["content"] = ["type": "doc", "content": [["type": "paragraph", "content": [["type": "text", "text": "Older writing"]]]]]
    object["sections"] = sections
    let restored = try DhprojCodec.decode(JSONSerialization.data(withJSONObject: object))
    XCTAssertEqual(restored.sections[0].content, "Older writing")
    let exported = try EPUBExporter().export(restored)
    let archive = try Archive(data: exported.data, accessMode: .read)
    let mime = try XCTUnwrap(archive["mimetype"])
    var bytes = Data(); _ = try archive.extract(mime) { bytes.append($0) }
    XCTAssertEqual(String(data: bytes, encoding: .utf8), "application/epub+zip")
    XCTAssertNotNil(archive["EPUB/package.opf"])
    XCTAssertNotNil(archive["EPUB/nav.xhtml"])
  }
}
