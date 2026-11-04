import Foundation

public struct BibleAIAccess: Codable, Equatable, Sendable {
  public var hidden: Bool?
  public var hiddenFields: [String]?
  public var conditions: [String: String]?
  public init() {}
}
public enum BibleAccess {
  public static func sceneFacts(_ text: String) throws -> [String: String] {
    var facts: [String: String] = [:]
    for item in text.components(separatedBy: ",") where !item.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
      let pair = item.components(separatedBy: "=").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
      guard pair.count == 2, !pair[0].isEmpty, !pair[1].isEmpty, facts[pair[0]] == nil else {
        throw NSError(domain: "DraftHarbour.SceneFacts", code: 1, userInfo: [NSLocalizedDescriptionKey: "Use unique scene facts as name=value, separated by commas."])
      }
      facts[pair[0]] = pair[1]
    }
    return facts
  }
  public static func visible(_ state: BibleEntryState, field: String, scene: [String: String] = [:]) -> Bool {
    guard state.aiAccess?.hidden != true, state.aiAccess?.hiddenFields?.contains(field) != true,
      let conditions = try? sceneFacts(state.aiAccess?.conditions?[field] ?? "") else { return false }
    return conditions.allSatisfy { scene[$0.key] == $0.value }
  }
  public static func inferenceEntry(_ entry: BibleEntry, scene: [String: String] = [:]) -> BibleEntry? {
    guard entry.state.status == "canon", !entry.state.archived, entry.state.aiAccess?.hidden != true else { return nil }
    var copy = entry
    var s = entry.state
    if !visible(s, field: "body", scene: scene) { s.body = "" }
    if !visible(s, field: "aliases", scene: scene) { s.aliases = [] }
    s.fields = s.fields.filter { visible(entry.state, field: "field:" + $0.key, scene: scene) }
    if !visible(s, field: "validity", scene: scene) { s.validFrom = ""; s.validTo = "" }
    s.provenance = ""; s.tags = []; s.linkedEntryIds = []; s.aiAccess = nil
    copy.state = s; copy.revisions = []
    return copy
  }
  public static func controlledNames(_ entries: [BibleEntry]) -> Set<String> {
    Set(entries.filter { $0.state.status == "canon" || $0.state.aiAccess?.hidden == true }
      .flatMap { [$0.state.title] + $0.state.aliases }.map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() })
  }
  public static func matches(_ query: String, name: String) -> Bool {
    let name = name.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !name.isEmpty else { return false }
    let pattern = "(?<![\\p{L}\\p{N}_])" + NSRegularExpression.escapedPattern(for: name) + "(?![\\p{L}\\p{N}_])"
    return query.range(of: pattern, options: [.regularExpression, .caseInsensitive]) != nil
  }
}
