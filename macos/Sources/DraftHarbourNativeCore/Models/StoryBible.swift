import Foundation

public struct BibleEntryState: Codable, Equatable, Sendable {
  public static let categories = ["character", "setting", "event", "plotArc", "scene", "theme", "worldbuilding", "research", "source"]
  public static let statuses = ["idea", "draft", "canon", "disputed", "superseded", "deprecated", "research", "ai_suggestion"]
  public static let templates: [String: [String: String]] = [
    "character": ["Goal": "", "Fear": "", "Voice": "", "Backstory": ""],
    "setting": ["Atmosphere": "", "Geography": "", "Ownership": ""],
    "event": ["Start": "", "End": "", "Participants": "", "Narrative order": "", "Chronological order": ""],
    "plotArc": ["Goal": "", "Stakes": "", "Setup": "", "Climax": "", "Resolution": ""],
    "scene": ["POV": "", "Location": "", "Purpose": "", "Outcome": ""],
    "theme": ["Question": "", "Motif": ""], "worldbuilding": ["Rules": "", "Exceptions": ""],
    "research": ["Question": "", "Sources": ""],
    "source": ["Creator": "", "Publisher": "", "URL": "", "Locator": "", "Rights": ""]
  ]
  public var aiAccess: BibleAIAccess?
  public var title = "Untitled entry"
  public var category = "character"
  public var status = "draft"
  public var body = ""
  public var aliases: [String] = []
  public var tags: [String] = []
  public var linkedEntryIds: [String] = []
  public var fields: [String: String] = [:]
  public var provenance = "Manual"
  public var validFrom = ""
  public var validTo = ""
  public var archived = false
  public init() {}
}

public struct BibleRevision: Codable, Equatable, Identifiable, Sendable {
  public var id: String
  public var createdAt: Int64
  public var reason: String
  public var state: BibleEntryState
}

public struct BibleEntry: Codable, Equatable, Identifiable, Sendable {
  public var id: String
  public var novelId: String
  public var createdAt: Int64
  public var updatedAt: Int64
  public var revisions: [BibleRevision]
  public var state: BibleEntryState
  enum CodingKeys: String, CodingKey { case id, novelId, createdAt, updatedAt, revisions }
  public init(novelId: String) {
    id = UUID().uuidString
    self.novelId = novelId
    createdAt = Int64(Date().timeIntervalSince1970 * 1000)
    updatedAt = createdAt
    revisions = []
    state = BibleEntryState()
  }
  public init(from decoder: Decoder) throws {
    let c = try decoder.container(keyedBy: CodingKeys.self)
    id = try c.decode(String.self, forKey: .id)
    novelId = try c.decode(String.self, forKey: .novelId)
    createdAt = try c.decode(Int64.self, forKey: .createdAt)
    updatedAt = try c.decode(Int64.self, forKey: .updatedAt)
    revisions = try c.decode([BibleRevision].self, forKey: .revisions)
    state = try BibleEntryState(from: decoder)
    guard BibleEntryState.categories.contains(state.category), BibleEntryState.statuses.contains(state.status) else {
      throw DecodingError.dataCorrupted(.init(codingPath: decoder.codingPath, debugDescription: "Unsupported Story Bible category or status"))
    }
  }
  public func encode(to encoder: Encoder) throws {
    try state.encode(to: encoder)
    var c = encoder.container(keyedBy: CodingKeys.self)
    try c.encode(id, forKey: .id)
    try c.encode(novelId, forKey: .novelId)
    try c.encode(createdAt, forKey: .createdAt)
    try c.encode(updatedAt, forKey: .updatedAt)
    try c.encode(revisions, forKey: .revisions)
  }
  public mutating func revise(_ next: BibleEntryState, reason: String = "Edited") {
    let now = Int64(Date().timeIntervalSince1970 * 1000)
    revisions.append(BibleRevision(id: UUID().uuidString, createdAt: now, reason: reason, state: state))
    state = next
    updatedAt = now
  }
  public static func importedCopies(_ entries: [BibleEntry], novelId: String) throws -> [BibleEntry] {
    guard Set(entries.map(\.id)).count == entries.count else {
      throw CocoaError(.fileReadCorruptFile)
    }
    let ids = Dictionary(uniqueKeysWithValues: entries.map { ($0.id, UUID().uuidString) })
    func remap(_ state: BibleEntryState) -> BibleEntryState {
      var result = state
      result.linkedEntryIds = state.linkedEntryIds.compactMap { ids[$0] }
      return result
    }
    return entries.map { entry in
      var copy = entry
      copy.id = ids[entry.id]!
      copy.novelId = novelId
      copy.state = remap(entry.state)
      copy.revisions = entry.revisions.map { revision in
        var result = revision
        result.id = UUID().uuidString
        result.state = remap(revision.state)
        return result
      }
      return copy
    }
  }
  public static func markdown(_ entries: [BibleEntry]) -> String {
    entries.filter { !$0.state.archived }.map { entry in
      let s = entry.state
      let fields = s.fields.sorted { $0.key < $1.key }.map { "\($0.key): \($0.value)" }.joined(separator: "\n")
      let links = s.linkedEntryIds.map { id in entries.first { $0.id == id }?.state.title ?? id }.joined(separator: ", ")
      return "# \(s.title)\n\nType: \(s.category)\nStatus: \(s.status)\nAliases: \(s.aliases.joined(separator: ", "))\nTags: \(s.tags.joined(separator: ", "))\nValid: \(s.validFrom) → \(s.validTo)\nProvenance: \(s.provenance)\n\n\(s.body)\n\n\(fields)\n\nLinks: \(links)"
    }.joined(separator: "\n\n---\n\n")
  }
}
