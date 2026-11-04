import DraftHarbourNativeCore
import Foundation
import XCTest

final class StoryBibleReferenceTests: XCTestCase {
  func testCanonReferencesAreReadOnlyScopedAndBounded() throws {
    var envelope = DhprojCodec.newProject(title: "References")
    envelope.sections[0].content = "Do not send this chapter to a selected rewrite."
    var mara = BibleEntry(novelId: envelope.project.id)
    mara.state.title = "Mara"
    mara.state.status = "canon"
    mara.state.body = "Cannot swim."
    mara.state.aliases = ["Captain Venn"]
    mara.state.fields = ["Voice": "Quiet"]
    var quay = BibleEntry(novelId: envelope.project.id)
    quay.state.title = "Quay"
    quay.state.status = "canon"
    quay.state.body = "Gate closes at dusk."
    var draft = BibleEntry(novelId: envelope.project.id)
    draft.state.body = "DRAFT SECRET"
    var archived = mara
    archived.id = "archive"
    archived.state.archived = true
    archived.state.body = "ARCHIVE SECRET"
    var other = mara
    other.novelId = "other"
    other.state.body = "OTHER PROJECT SECRET"
    envelope.bibleEntries = [quay, mara, draft, archived, other]
    let before = envelope.bibleEntries
    let references = AIWorkflowServices.storyBibleReferences(envelope: envelope, query: "Captain Venn")
    XCTAssertTrue(references.contains("Cannot swim."))
    XCTAssertTrue(references.contains("Quiet"))
    XCTAssertTrue(references.contains("read-only project data"))
    XCTAssertFalse(references.contains("SECRET"))
    XCTAssertFalse(references.contains("Do not send this chapter"))
    XCTAssertLessThan(try XCTUnwrap(references.range(of: "Cannot swim.")).lowerBound,
                      try XCTUnwrap(references.range(of: "Gate closes")).lowerBound)
    XCTAssertEqual(envelope.bibleEntries, before)
    XCTAssertEqual(AIWorkflowServices.storyBibleReferences(envelope: envelope, maxCharacters: 1), "")
    envelope.bibleEntries[0].state.body = String(repeating: "x", count: 6000)
    let bounded = AIWorkflowServices.storyBibleReferences(envelope: envelope, maxCharacters: 1100)
    XCTAssertLessThanOrEqual(bounded.count, 1100)
    XCTAssertTrue(bounded.contains("Cannot swim."))
    XCTAssertTrue(bounded.contains("omitted for space"))
    XCTAssertFalse(bounded.contains("xxx"))
  }
}
