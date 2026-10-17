import DraftHarbourNativeCore
import XCTest

final class DhprojCodecTests: XCTestCase {
  private func sharedFixture(_ name: String) throws -> Data {
    let root = URL(fileURLWithPath: #filePath)
      .deletingLastPathComponent().deletingLastPathComponent()
      .deletingLastPathComponent().deletingLastPathComponent()
    return try Data(contentsOf: root.appendingPathComponent("fixtures/\(name)"))
  }

  func testSharedWebAndNativeContract() throws {
    let json = try sharedFixture("dhproj-v1.json")
    let envelope = try DhprojCodec.decode(json)
    XCTAssertEqual(envelope.sections.first?.content, "Alice watched the harbour.")
    XCTAssertEqual(envelope.storyBlueprint?.genre, "Mystery")
    XCTAssertEqual(envelope.worldEntries.first?.linkedCharacters, ["character-fixture"])
    XCTAssertEqual(try DhprojCodec.decode(DhprojCodec.encode(envelope)), envelope)
  }

  func testSharedWebZipContainer() throws {
    let base64 = String(decoding: try sharedFixture("dhproj-v1.zip.base64"), as: UTF8.self)
    let zipped = try XCTUnwrap(Data(base64Encoded: base64, options: .ignoreUnknownCharacters))
    let envelope = try DhprojCodec.decode(zipped)
    XCTAssertEqual(envelope.project.title, "Shared Harbour")
    XCTAssertEqual(envelope.characters.first?.name, "Alice")
  }

  func testDecodesCurrentDhprojV1Envelope() throws {
    let json = """
    {
      "manifest": {
        "format": "dhproj",
        "version": 1,
        "appVersion": "2.0.0",
        "createdAt": "2026-05-04T00:00:00.000Z"
      },
      "project": {
        "id": "project-1",
        "title": "The Native Draft",
        "projectType": "screenplay",
        "updatedAt": 1777852800000
      },
      "projectType": "screenplay",
      "sections": [
        {
          "id": "section-1",
          "novelId": "project-1",
          "order": 0,
          "title": "Scene 1",
          "updatedAt": 1777852800000,
          "content": "INT. ROOM - DAY\\n@JULES\\nWe made it native.",
          "summary": "",
          "pov": "",
          "status": "draft",
          "tags": [],
          "wordGoal": 0,
          "scenes": []
        }
      ],
      "snapshots": [],
      "commentThreads": [],
      "settings": {
        "autosaveMs": 750,
        "theme": "dark"
      },
      "goalTrends": []
    }
    """

    let envelope = try DhprojCodec.decode(Data(json.utf8))

    XCTAssertEqual(envelope.project.title, "The Native Draft")
    XCTAssertEqual(envelope.projectType, .screenplay)
    XCTAssertEqual(envelope.sections.first?.title, "Scene 1")
    XCTAssertEqual(envelope.settings.autosaveMs, 750)
  }

  func testRoundTripsNewProject() throws {
    let envelope = DhprojCodec.newProject(title: "Round Trip", projectType: .book)
    let data = try DhprojCodec.encode(envelope)
    let decoded = try DhprojCodec.decode(data)

    XCTAssertEqual(decoded.project.title, "Round Trip")
    XCTAssertEqual(decoded.projectType, .book)
    XCTAssertEqual(decoded.sections.count, 1)
    XCTAssertEqual(decoded.sections.first?.order, 0)
  }

  func testRejectsUnsupportedVersion() throws {
    let json = """
    {
      "manifest": { "format": "dhproj", "version": 99, "appVersion": "x", "createdAt": "now" },
      "project": { "id": "p", "title": "Bad", "projectType": "book", "updatedAt": 1 },
      "projectType": "book",
      "sections": []
    }
    """

    XCTAssertThrowsError(try DhprojCodec.decode(Data(json.utf8))) { error in
      XCTAssertEqual(error as? DraftHarbourError, .unsupportedVersion(99))
    }
  }
}
