import Foundation
import XCTest
@testable import DraftHarbourNativeCore

final class BibleAccessTests: XCTestCase {
  func testConditionalVisibilityAndRoundTrip() throws {
    var entry = BibleEntry(novelId: "a")
    entry.state.status = "canon"; entry.state.body = "PRIVATE"; entry.state.fields = ["Form": "Human hands", "Secret": "HIDDEN"]
    var access = BibleAIAccess(); access.hiddenFields = ["body", "field:Secret"]; access.conditions = ["field:Form": "form=human"]
    entry.state.aiAccess = access
    XCTAssertEqual(BibleAccess.inferenceEntry(entry)?.state.fields, [:])
    XCTAssertEqual(BibleAccess.inferenceEntry(entry, scene: try BibleAccess.sceneFacts("form=human"))?.state.fields, ["Form": "Human hands"])
    XCTAssertEqual(BibleAccess.inferenceEntry(entry)?.state.body, "")
    XCTAssertEqual(try JSONDecoder().decode(BibleEntry.self, from: JSONEncoder().encode(entry)), entry)
    let old = entry.state; entry.revise(old)
    XCTAssertEqual(entry.revisions[0].state.aiAccess, access)
    XCTAssertThrowsError(try BibleAccess.sceneFacts("form=human, form=wolf"))
    XCTAssertFalse(BibleAccess.matches("Joann arrives", name: "Ann"))
    XCTAssertTrue(BibleAccess.matches("Éva arrives", name: "éva"))
    access.hidden = true; entry.state.aiAccess = access
    XCTAssertNil(BibleAccess.inferenceEntry(entry))
    XCTAssertTrue(BibleAccess.controlledNames([entry]).contains(entry.state.title.lowercased()))
    var envelope = DhprojCodec.newProject(title: "Policy tests")
    entry.novelId = envelope.project.id; entry.state.title = "Mara"; entry.state.aiAccess?.hidden = false
    envelope.bibleEntries = [entry]
    envelope.characters = [CharacterEntity(novelId: envelope.project.id, name: " Mara ", description: "LEGACY_SECRET")]
    let index = AIProjectContextIndex(envelope: envelope)
    XCTAssertFalse(index.storyBibleText().contains("PRIVATE"))
    XCTAssertFalse(index.storyBibleText().contains("HIDDEN"))
    XCTAssertFalse(index.storyBibleText().contains("LEGACY_SECRET"))
    XCTAssertTrue(index.search("PRIVATE").isEmpty)
  }
}
