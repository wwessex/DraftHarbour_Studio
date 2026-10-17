import CryptoKit
import Foundation

public struct DeletedSection: Codable, Equatable, Identifiable, Sendable {
  public var id: String = makeIdentifier()
  public var deletedAt: Int64 = currentTimeMilliseconds()
  public var section: Section
  public var snapshots: [Snapshot]
  public var comments: [CommentThread]
}

public struct VerifiedProjectBackup: Codable, Identifiable, Sendable {
  public var id: String
  public var createdAt: Int64
  public var automatic: Bool
  public var label: String
  public var checksum: String
  public var projectData: Data
}

/// Local safety copies are independent of the open document, with atomic writes.
public struct ProjectSafetyService {
  public var directory: URL
  public init(directory: URL? = nil) {
    self.directory = directory ?? FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
      .appendingPathComponent("DraftHarbourNative/Backups", isDirectory: true)
  }
  private func folder(_ projectID: String) -> URL {
    // Imported identifiers are data, never filesystem path components.
    directory.appendingPathComponent(SHA256.hash(data: Data(projectID.utf8)).map { String(format: "%02x", $0) }.joined(), isDirectory: true)
  }
  private func checksum(_ data: Data) -> String {
    SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
  }
  public func list(projectID: String) throws -> [VerifiedProjectBackup] {
    let path = folder(projectID)
    guard FileManager.default.fileExists(atPath: path.path) else { return [] }
    return try FileManager.default.contentsOfDirectory(at: path, includingPropertiesForKeys: nil)
      .filter { $0.pathExtension == "json" }
      .map { url in
        let backup = try JSONDecoder().decode(VerifiedProjectBackup.self, from: Data(contentsOf: url))
        guard UUID(uuidString: backup.id) != nil, url.lastPathComponent == backup.id + ".json" else {
          throw CocoaError(.fileReadCorruptFile)
        }
        return backup
      }
      .sorted { $0.createdAt > $1.createdAt }
  }
  @discardableResult
  public func save(_ envelope: DhprojEnvelope, automatic: Bool = false, label: String = "Manual") throws -> VerifiedProjectBackup {
    let data = try DhprojCodec.encode(envelope, prettyPrinted: false)
    let previous = try list(projectID: envelope.project.id)
    if automatic, let latest = previous.first(where: \.automatic), latest.checksum == checksum(data) { return latest }
    let backup = VerifiedProjectBackup(id: makeIdentifier(), createdAt: currentTimeMilliseconds(), automatic: automatic, label: label, checksum: checksum(data), projectData: data)
    let path = folder(envelope.project.id)
    try FileManager.default.createDirectory(at: path, withIntermediateDirectories: true)
    try JSONEncoder().encode(backup).write(to: path.appendingPathComponent(backup.id + ".json"), options: .atomic)
    // Verify the actual stored bytes before rotating older automatic copies.
    let written = try JSONDecoder().decode(VerifiedProjectBackup.self, from: Data(contentsOf: path.appendingPathComponent(backup.id + ".json")))
    _ = try restore(written)
    if automatic {
      for old in previous.filter(\.automatic).dropFirst(9) {
        try FileManager.default.removeItem(at: path.appendingPathComponent(old.id + ".json"))
      }
    }
    return backup
  }
  public func restore(_ backup: VerifiedProjectBackup) throws -> DhprojEnvelope {
    guard checksum(backup.projectData) == backup.checksum else { throw CocoaError(.fileReadCorruptFile) }
    return try DhprojCodec.copyAsNewProject(DhprojCodec.decode(backup.projectData))
  }
}

public struct EntityOccurrence: Identifiable, Sendable {
  public var id: String { "\(sectionID)-\(offset)" }
  public var sectionID: String
  public var title: String
  public var excerpt: String
  public var offset: Int
}

public enum EntityOccurrenceServices {
  public static func find(names: [String], sections: [Section], limit: Int = 100) -> [EntityOccurrence] {
    let terms = names.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
    guard !terms.isEmpty, limit > 0 else { return [] }
    let pattern = "(?<![\\p{L}\\p{N}_])(?:" + terms.map(NSRegularExpression.escapedPattern(for:)).joined(separator: "|") + ")(?![\\p{L}\\p{N}_])"
    guard let regex = try? NSRegularExpression(pattern: pattern, options: .caseInsensitive) else { return [] }
    var found: [EntityOccurrence] = []
    for section in sections {
      let text = MarkdownTools.plainText(from: section.content ?? "") as NSString
      regex.enumerateMatches(in: text as String, range: NSRange(location: 0, length: text.length)) { match, _, stop in
        guard let range = match?.range else { return }
        let start = max(0, range.location - 60)
        found.append(EntityOccurrence(sectionID: section.id, title: section.title, excerpt: text.substring(with: NSRange(location: start, length: min(text.length - start, range.length + 120))), offset: range.location))
        if found.count >= limit { stop.pointee = true }
      }
      if found.count >= limit { break }
    }
    return found
  }
}

extension ProjectStore {
  @discardableResult
  public func restoreDeletedSection(id: String) throws -> Section {
    guard let entry = envelope.deletedSections.first(where: { $0.id == id }) else { throw DraftHarbourError.invalidSelection }
    var recovered = entry.section
    recovered.id = makeIdentifier()
    recovered.scenes = recovered.scenes.map { scene in var copy = scene; copy.id = makeIdentifier(); return copy }
    recovered.order = envelope.sections.count
    recovered.novelId = envelope.project.id
    recovered.title += " (Recovered)"
    envelope.sections.append(recovered)
    envelope.snapshots += entry.snapshots.map { item in var copy = item; copy.id = makeIdentifier(); copy.chapterId = recovered.id; return copy }
    envelope.commentThreads += entry.comments.map { item in
      var copy = item; copy.id = makeIdentifier(); copy.chapterId = recovered.id
      copy.comments = copy.comments.map { item in var comment = item; comment.id = makeIdentifier(); return comment }
      return copy
    }
    envelope.deletedSections.removeAll { $0.id == id }
    activeSectionID = recovered.id
    markChanged()
    return recovered
  }

  @discardableResult
  public func splitActiveSection(atUTF16 offset: Int) throws -> Section {
    guard let current = activeSection, let index = envelope.sections.firstIndex(where: { $0.id == current.id }) else { throw DraftHarbourError.invalidSelection }
    let text = current.content ?? ""
    guard offset > 0, offset < (text as NSString).length,
      let splitRange = Range(NSRange(location: offset, length: 0), in: text),
      !envelope.commentThreads.contains(where: { $0.chapterId == current.id && $0.anchor.from < offset && $0.anchor.to > offset }) else { throw DraftHarbourError.invalidSelection }
    _ = try createSnapshot(label: "Before split")
    var right = current
    right.id = makeIdentifier(); right.title += " (continued)"; right.scenes = []
    right.content = String(text[splitRange.lowerBound...])
    envelope.sections[index].content = String(text[..<splitRange.lowerBound])
    envelope.sections.insert(right, at: index + 1)
    for i in envelope.commentThreads.indices where envelope.commentThreads[i].chapterId == current.id && envelope.commentThreads[i].anchor.from >= offset {
      envelope.commentThreads[i].chapterId = right.id
      envelope.commentThreads[i].anchor.from -= offset; envelope.commentThreads[i].anchor.to -= offset
    }
    renumberSections(); activeSectionID = right.id; markChanged()
    return envelope.sections[index + 1]
  }

  public func mergeActiveSectionWithNext() throws {
    guard let current = activeSection, let index = envelope.sections.firstIndex(where: { $0.id == current.id }), index + 1 < envelope.sections.count else { throw DraftHarbourError.invalidSelection }
    let next = envelope.sections[index + 1]
    _ = try createSnapshot(label: "Before merge")
    envelope.deletedSections.insert(DeletedSection(section: next, snapshots: envelope.snapshots.filter { $0.chapterId == next.id }, comments: envelope.commentThreads.filter { $0.chapterId == next.id }), at: 0)
    let separator = (current.content ?? "").isEmpty || (next.content ?? "").isEmpty ? "" : "\n\n"
    let shift = ((current.content ?? "") + separator).utf16.count
    envelope.sections[index].content = (current.content ?? "") + separator + (next.content ?? "")
    envelope.sections[index].summary = [current.summary, next.summary].filter { !$0.isEmpty }.joined(separator: "\n\n")
    envelope.sections[index].tags = Array(Set(current.tags + next.tags)).sorted()
    envelope.sections[index].wordGoal += next.wordGoal
    envelope.sections[index].scenes += next.scenes
    for i in envelope.commentThreads.indices where envelope.commentThreads[i].chapterId == next.id {
      envelope.commentThreads[i].chapterId = current.id
      envelope.commentThreads[i].anchor.from += shift; envelope.commentThreads[i].anchor.to += shift
    }
    for i in envelope.snapshots.indices where envelope.snapshots[i].chapterId == next.id { envelope.snapshots[i].chapterId = current.id }
    envelope.sections.remove(at: index + 1); renumberSections(); markChanged()
  }

  public func moveScene(sceneID: String, from sourceID: String, to targetID: String) throws {
    guard sourceID != targetID, let source = envelope.sections.firstIndex(where: { $0.id == sourceID }),
      let target = envelope.sections.firstIndex(where: { $0.id == targetID }), let index = envelope.sections[source].scenes.firstIndex(where: { $0.id == sceneID }) else { throw DraftHarbourError.invalidSelection }
    let scene = envelope.sections[source].scenes.remove(at: index)
    envelope.sections[target].scenes.append(scene); markChanged()
  }
}
