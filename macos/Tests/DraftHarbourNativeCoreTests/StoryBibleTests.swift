import DraftHarbourNativeCore
import Foundation
import XCTest

final class StoryBibleTests: XCTestCase {
  private func entries() throws -> [BibleEntry] {
    struct Fixture: Decodable { var bibleEntries: [BibleEntry] }
    let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    return try JSONDecoder().decode(Fixture.self, from: Data(contentsOf: root.appendingPathComponent("fixtures/story-bible-v1.json"))).bibleEntries
  }
  func testSharedFlatSchemaAndRevisionRestore() throws {
    var entry = try XCTUnwrap(entries().first)
    XCTAssertEqual(entry.state.title, "Mara")
    XCTAssertEqual(entry.state.linkedEntryIds, ["quay"])
    entry.revise(entry.revisions[0].state, reason: "Restored revision")
    XCTAssertEqual(entry.state.status, "draft")
    XCTAssertEqual(entry.revisions.count, 2)
    XCTAssertEqual(entry.revisions[1].state.status, "canon")
    let encoded = try JSONEncoder().encode(entry)
    let object = try XCTUnwrap(JSONSerialization.jsonObject(with: encoded) as? [String: Any])
    XCTAssertEqual(object["title"] as? String, "Mara")
    XCTAssertNil(object["state"])
    XCTAssertEqual(try JSONDecoder().decode(BibleEntry.self, from: encoded), entry)
  }
  func testProjectRoundTripAndCanonIsolation() throws {
    var envelope = DhprojCodec.newProject(title: "Story Bible", projectType: .book)
    envelope.bibleEntries = try BibleEntry.importedCopies(entries(), novelId: envelope.project.id)
    let copies = try BibleEntry.importedCopies(envelope.bibleEntries, novelId: envelope.project.id)
    XCTAssertEqual(copies[0].state.linkedEntryIds, [copies[1].id])
    XCTAssertEqual(copies[0].revisions[0].state.linkedEntryIds, [copies[1].id])
    XCTAssertNotEqual(copies[0].id, envelope.bibleEntries[0].id)
    XCTAssertEqual(try DhprojCodec.decode(DhprojCodec.encode(envelope)).bibleEntries, envelope.bibleEntries)
    XCTAssertTrue(AIProjectContextIndex(envelope: envelope).storyBibleText().contains("Cannot swim."))
    envelope.bibleEntries[0].state.status = "ai_suggestion"
    envelope.bibleEntries[1].state.archived = true
    XCTAssertFalse(AIProjectContextIndex(envelope: envelope).storyBibleText().contains("Cannot swim."))
    XCTAssertFalse(AIWorkflowServices.buildStoryContext(envelope: envelope, section: nil).contains("Cannot swim."))
  }
}
