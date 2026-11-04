import Foundation

public enum WritingAction: String, CaseIterable, Sendable {
  case write, rewrite, copyedit, `continue`
  public var replacesPassage: Bool { self == .rewrite || self == .copyedit }
  public var title: String { rawValue.capitalized }
}

public struct WritingPlan: Sendable {
  public var action: WritingAction
  public var source: String
  public var range: NSRange
  public var prompt: String
}

public struct CopyeditChange: Equatable, Sendable {
  public var before: String
  public var after: String
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
    var task: String
    switch action {
    case .write:
      guard !instructions.isEmpty else { throw failure("Describe what you want to write in the instruction box first.") }
      task = "Write new fiction from the author’s instructions. Use the project’s prose or screenplay format. Use the chapter context for continuity. Return only the new passage to append, without repeating existing text or adding commentary."
    case .continue:
      guard !trimmed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { throw failure("Write a paragraph first, or use Write to start a new scene.") }
      task = "Continue immediately after the final paragraph below. Match its voice, point of view, tense, format and continuity. Return only the next passage; do not repeat, rewrite or summarise the existing ending.\n\nFINAL PARAGRAPH:\n" + ns.substring(with: NSRange(location: start, length: end - start))
    case .rewrite, .copyedit:
      guard !trimmed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { throw failure("Select a passage or write a paragraph to rewrite first.") }
      if let selection, selection.location >= 0, selection.length > 0,
        selection.location <= ns.length, selection.length <= ns.length - selection.location,
        Range(selection, in: source) != nil {
        range = selection
      } else {
        if let selection, selection.length != 0 {
          throw failure("The selected passage is no longer valid. Select it again before rewriting.")
        }
        range = NSRange(location: start, length: end - start)
      }
      let target = ns.substring(with: range)
      guard !target.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { throw failure("Select a passage containing text to rewrite.") }
      task = "Rewrite only the target passage below. Preserve meaning, point of view, tense, format and the author’s voice unless instructed otherwise. Return one replacement passage only, without headings, alternatives or explanation. Do not continue the story or expand this target into a scene unless the author explicitly requests it.\n\nTARGET PASSAGE:\n" + target
    }
    if action == .copyedit {
      task = "Copyedit only TARGET PASSAGE. Correct clear spelling, punctuation and accidental repetition; preserve meaning, voice and all other wording. Return JSON only: {\"edits\":[{\"before\":\"exact unique original span\",\"after\":\"corrected span\"}]}. Use at most 32 non-overlapping edits. Each before span must occur exactly once in the original target. Return {\"edits\":[]} if no correction is needed. No markdown, prose or commentary.\n\nTARGET PASSAGE:\n" + ns.substring(with: range)
    }
    return WritingPlan(action: action, source: source, range: range,
      prompt: task + (instructions.isEmpty ? "" : "\n\nAUTHOR INSTRUCTIONS:\n" + instructions))
  }

  public static func copyeditPreview(_ plan: WritingPlan, json: String) throws -> String {
    try copyeditReview(plan, json: json).text
  }

  public static func copyeditReview(_ plan: WritingPlan, json: String) throws -> (text: String, changes: [CopyeditChange]) {
    func invalid() -> NSError { failure("The copyedit proposal could not be verified. Generate again; no manuscript text was changed.") }
    guard let data = json.data(using: .utf8),
      let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
      Set(object.keys) == ["edits"], let proposals = object["edits"] as? [[String: Any]], proposals.count <= 32 else { throw invalid() }
    let target = (plan.source as NSString).substring(with: plan.range)
    let ns = target as NSString
    var edits: [(NSRange, String)] = []
    for proposal in proposals {
      guard Set(proposal.keys) == ["before", "after"], let before = proposal["before"] as? String, !before.isEmpty,
        let after = proposal["after"] as? String else { throw invalid() }
      let range = ns.range(of: before, options: .literal)
      guard range.location != NSNotFound, Range(range, in: target) != nil else { throw invalid() }
      let rest = NSRange(location: range.location + 1, length: ns.length - range.location - 1)
      guard ns.range(of: before, options: .literal, range: rest).location == NSNotFound else { throw invalid() }
      edits.append((range, after))
    }
    edits.sort { $0.0.location < $1.0.location }
    for index in edits.indices where index > 0 {
      guard NSMaxRange(edits[index - 1].0) <= edits[index].0.location else { throw invalid() }
    }
    var result = target
    for (range, after) in edits.reversed() { result = (result as NSString).replacingCharacters(in: range, with: after) }
    guard !result.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { throw invalid() }
    let changes = result.utf16.elementsEqual(target.utf16) ? [] : edits.compactMap { range, after -> CopyeditChange? in
      let before = ns.substring(with: range)
      return before.utf16.elementsEqual(after.utf16) ? nil : CopyeditChange(before: before, after: after)
    }
    return (result, changes)
  }

  public static func applying(_ plan: WritingPlan, current: String, output: String) throws -> String {
    guard current.utf16.elementsEqual(plan.source.utf16) else { throw failure("The chapter changed after generation. Generate again before applying this suggestion.") }
    let text = output.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !text.isEmpty else { throw failure("The model returned no passage to apply.") }
    let separator = plan.action.replacesPassage || current.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "" : current.hasSuffix("\n\n") ? "" : current.hasSuffix("\n") ? "\n" : "\n\n"
    let target = (current as NSString).substring(with: plan.range)
    let replacement = plan.action == .copyedit ? output : plan.action.replacesPassage
      ? String(target.prefix(while: { $0.isWhitespace })) + text + String(target.reversed().prefix(while: { $0.isWhitespace }).reversed())
      : separator + text
    return (current as NSString).replacingCharacters(in: plan.range, with: replacement)
  }
}
