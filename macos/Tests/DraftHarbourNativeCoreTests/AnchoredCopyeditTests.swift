import Foundation
import XCTest
@testable import DraftHarbourNativeCore

final class AnchoredCopyeditTests: XCTestCase {
  func testSharedCases() throws {
    let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    let cases = try JSONSerialization.jsonObject(with: Data(contentsOf: root.appendingPathComponent("fixtures/anchored-copyedit.json"))) as! [[String: Any]]
    for item in cases {
      let source = item["source"] as! String
      let plan = try WritingActions.prepare(.copyedit, source: source, selection: NSRange(location: 0, length: (source as NSString).length))
      let json = try item["raw"] as? String ?? String(data: JSONSerialization.data(withJSONObject: item["proposal"]!), encoding: .utf8)!
      if let expected = item["expected"] as? String {
        let review = try WritingActions.copyeditReview(plan, json: json)
        let output = review.text
        XCTAssertEqual(review.changes.isEmpty, source.utf16.elementsEqual(output.utf16))
        XCTAssertEqual(try WritingActions.applying(plan, current: source, output: output), expected, item["id"] as! String)
        XCTAssertThrowsError(try WritingActions.applying(plan, current: source + "changed", output: output))
      } else { XCTAssertThrowsError(try WritingActions.copyeditPreview(plan, json: json), item["id"] as! String) }
    }
  }
}
