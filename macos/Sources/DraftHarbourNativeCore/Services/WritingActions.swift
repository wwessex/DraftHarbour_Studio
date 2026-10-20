import Foundation

public enum WritingAction: String, CaseIterable, Sendable {
  case write, rewrite, `continue`
  public var title: String { rawValue.capitalized }
}

public struct WritingPlan: Sendable {
  public var action: WritingAction
  public var source: String
  public var range: NSRange
  public var prompt: String
}

public enum WritingActions {
  private static func failure(_ message: String) -> NSError {
    NSError(domain: "DraftHarbour.WritingActions", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
  }

  public static func prepare(_ action: WritingAction, source: String, selection: NSRange? = nil, direction: String = "") throws -> WritingPlan {
    let trimmed = source.replacingOccurrences(of: "\\s+$", with: "", options: .regularExpression)
    let ns = source as NSString
    let end = (trimmed as NSString).length
    let regex = try NSRegularExpression(pattern: "(?:\\r?\\n)(?:[ \\t]*\\r?\\n)+")
    let last = regex.matches(in: trimmed, range: NSRange(location: 0, length: end)).last
    let start = last.map { NSMaxRange($0.range) } ?? 0
    var range = NSRange(location: ns.length, length: 0)
    let instructions = direction.trimmingCharacters(in: .whitespacesAndNewlines)
    let task: String
    switch action {
    case .write:
      guard !instructions.isEmpty else { throw failure("Describe what you want to write in the instruction box first.") }
      task = "Write new fiction from the author’s instructions. Use the project’s prose or screenplay format. Use the chapter context for continuity. Return only the new passage to append, without repeating existing text or adding commentary."
    case .continue:
      guard !trimmed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { throw failure("Write a paragraph first, or use Write to start a new scene.") }
      task = "Continue immediately after the final paragraph below. Match its voice, point of view, tense, format and continuity. Return only the next passage; do not repeat, rewrite or summarise the existing ending.\n\nFINAL PARAGRAPH:\n" + ns.substring(with: NSRange(location: start, length: end - start))
    case .rewrite:
      guard !trimmed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { throw failure("Select a passage or write a paragraph to rewrite first.") }
      if let selection, selection.location >= 0, selection.length > 0,
        selection.location <= ns.length, selection.length <= ns.length - selection.location,
        Range(selection, in: source) != nil {
        range = selection
      } else {
        range = NSRange(location: start, length: end - start)
      }
      let target = ns.substring(with: range)
      guard !target.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { throw failure("Select a passage containing text to rewrite.") }
      task = "Rewrite only the target passage below. Preserve meaning, point of view, tense, format and the author’s voice unless instructed otherwise. Return one replacement passage only, without headings, alternatives or explanation.\n\nTARGET PASSAGE:\n" + target
    }
    return WritingPlan(action: action, source: source, range: range,
      prompt: task + (instructions.isEmpty ? "" : "\n\nAUTHOR INSTRUCTIONS:\n" + instructions))
  }

  public static func applying(_ plan: WritingPlan, current: String, output: String) throws -> String {
    guard current == plan.source else { throw failure("The chapter changed after generation. Generate again before applying this suggestion.") }
    let text = output.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !text.isEmpty else { throw failure("The model returned no passage to apply.") }
    let separator = plan.action == .rewrite || current.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "" : current.hasSuffix("\n\n") ? "" : current.hasSuffix("\n") ? "\n" : "\n\n"
    let target = (current as NSString).substring(with: plan.range)
    let replacement = plan.action == .rewrite
      ? String(target.prefix(while: { $0.isWhitespace })) + text + String(target.reversed().prefix(while: { $0.isWhitespace }).reversed())
      : separator + text
    return (current as NSString).replacingCharacters(in: plan.range, with: replacement)
  }
}
