import DraftHarbourNativeCore
import Foundation
import XCTest

final class NaturalWritingStyleTests: XCTestCase {
  func testStyleRetainsAuthorTaskContextAndStructuredContract() throws {
    let prompt = "Return only JSON with exact source anchor 🐦. Copyedit only."
    let request = AIRequest(prompt: prompt, context: "Original manuscript.", projectType: .screenplay, sectionTitle: "Quay", model: "local")
    XCTAssertEqual(request.styledPrompt, AIRequest.naturalWritingStyle + "\n\n" + prompt)
    XCTAssertEqual(request.prompt, prompt)
    XCTAssertEqual(request.context, "Original manuscript.")
    XCTAssertTrue(request.styledPrompt.contains("apply style only where the task permits"))
    XCTAssertTrue(request.styledPrompt.contains("exact anchors and required schemas"))
    let decoded = try JSONDecoder().decode(AIRequest.self, from: JSONEncoder().encode(request))
    XCTAssertEqual(decoded, request)
    let alreadyStyled = AIRequest(prompt: request.styledPrompt, projectType: .book)
    XCTAssertEqual(alreadyStyled.styledPrompt, request.styledPrompt)
  }
}
