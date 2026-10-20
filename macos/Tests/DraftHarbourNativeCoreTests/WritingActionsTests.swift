import DraftHarbourNativeCore
import Foundation
import XCTest

final class WritingActionsTests: XCTestCase {
  struct Fixture: Decodable {
    var id: String
    var action: String
    var source: String
    var from: Int?
    var to: Int?
    var direction: String?
    var output: String
    var expected: String
    var target: String?
  }

  func testSharedPassageContractIncludingUTF16AndParagraphBoundaries() throws {
    let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    let cases = try JSONDecoder().decode([Fixture].self, from: Data(contentsOf: root.appendingPathComponent("fixtures/writing-actions.json")))
    for item in cases {
      let selection = item.from.map { NSRange(location: $0, length: item.to! - $0) }
      let plan = try WritingActions.prepare(try XCTUnwrap(WritingAction(rawValue: item.action)), source: item.source, selection: selection, direction: item.direction ?? "")
      XCTAssertEqual(try WritingActions.applying(plan, current: item.source, output: item.output), item.expected, item.id)
      if let target = item.target { XCTAssertTrue(plan.prompt.contains(target), item.id) }
      if item.action == "continue" { XCTAssertFalse(plan.prompt.contains("Opening.")) }
    }
  }

  func testEmptyInputAndStaleResultsAreRejected() throws {
    XCTAssertThrowsError(try WritingActions.prepare(.write, source: "Text"))
    XCTAssertThrowsError(try WritingActions.prepare(.continue, source: "  "))
    XCTAssertThrowsError(try WritingActions.prepare(.rewrite, source: ""))
    let plan = try WritingActions.prepare(.rewrite, source: "Original.")
    XCTAssertThrowsError(try WritingActions.applying(plan, current: "Edited meanwhile.", output: "Replacement."))
    XCTAssertThrowsError(try WritingActions.applying(plan, current: plan.source, output: " "))
  }
}
