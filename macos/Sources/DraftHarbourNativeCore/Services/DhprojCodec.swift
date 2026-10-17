import Foundation
import ZIPFoundation

public enum DhprojCodec {
  public static let currentAppVersion = "native-2.0.0"

  public static func decode(_ data: Data) throws -> DhprojEnvelope {
    guard data.count <= 100 * 1024 * 1024 else { throw CocoaError(.fileReadTooLarge) }
    if data.starts(with: [0x50, 0x4B, 0x03, 0x04]) {
      let archive = try Archive(data: data, accessMode: .read)
      guard let entry = archive["project.json"], entry.uncompressedSize <= 100 * 1024 * 1024 else {
        throw CocoaError(.fileReadCorruptFile)
      }
      var json = Data()
      _ = try archive.extract(entry) { chunk in
        guard json.count + chunk.count <= 100 * 1024 * 1024 else { throw CocoaError(.fileReadCorruptFile) }
        json.append(chunk)
      }
      guard !json.starts(with: [0x50, 0x4B, 0x03, 0x04]) else { throw CocoaError(.fileReadCorruptFile) }
      return try decode(json)
    }
    let decoder = JSONDecoder()
    let envelope = try decoder.decode(DhprojEnvelope.self, from: LegacyContentMarkdown.normalizeEnvelope(data))

    guard envelope.manifest.format == "dhproj" else {
      throw DraftHarbourError.unsupportedFormat(envelope.manifest.format)
    }

    guard envelope.manifest.version == 1 else {
      throw DraftHarbourError.unsupportedVersion(envelope.manifest.version)
    }

    let ids = envelope.sections.map(\.id)
    guard !envelope.project.id.isEmpty, Set(ids).count == ids.count,
      envelope.snapshots.allSatisfy({ ids.contains($0.chapterId) }),
      envelope.commentThreads.allSatisfy({ ids.contains($0.chapterId) }) else { throw CocoaError(.fileReadCorruptFile) }
    return normalize(envelope)
  }

  /// Import/restore copies never reuse manuscript identities or enable remote credentials.
  public static func copyAsNewProject(_ envelope: DhprojEnvelope) throws -> DhprojEnvelope {
    let data = try encode(envelope)
    let object = try JSONSerialization.jsonObject(with: data)
    var identifiers: [String: String] = [:]
    func collect(_ value: Any) {
      if let dictionary = value as? [String: Any] {
        if let id = dictionary["id"] as? String { identifiers[id] = makeIdentifier() }
        for child in dictionary.values { collect(child) }
      } else if let array = value as? [Any] { array.forEach(collect) }
    }
    collect(object)
    func remap(_ value: Any, key: String = "") -> Any {
      if let dictionary = value as? [String: Any] {
        return Dictionary(uniqueKeysWithValues: dictionary.map { (identifiers[$0.key] ?? $0.key, remap($0.value, key: $0.key)) })
      }
      if let array = value as? [Any] { return array.map { remap($0, key: key) } }
      if let string = value as? String, key.lowercased().hasSuffix("id") || key.lowercased().hasSuffix("ids") || key == "linkedCharacters" { return identifiers[string] ?? string }
      return value
    }
    var copy = try decode(JSONSerialization.data(withJSONObject: remap(object)))
    copy.settings.sync = nil
    copy.integrations = nil
    copy.aiProviders = []
    return copy
  }

  public static func encode(_ envelope: DhprojEnvelope, prettyPrinted: Bool = true) throws -> Data {
    let encoder = JSONEncoder()
    encoder.outputFormatting = prettyPrinted ? [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes] : [.withoutEscapingSlashes]
    return try encoder.encode(normalize(envelope))
  }

  public static func normalize(_ envelope: DhprojEnvelope) -> DhprojEnvelope {
    var normalized = envelope
    let projectType = normalized.project.projectType ?? normalized.projectType
    normalized.projectType = projectType
    normalized.project.projectType = projectType
    normalized.sections = normalized.sections
      .enumerated()
      .map { index, section in
        var copy = section
        copy.novelId = normalized.project.id
        copy.order = index
        return copy
      }
      .sorted { $0.order < $1.order }
    return normalized
  }

  public static func newProject(title: String = "Untitled Project", projectType: ProjectType = .book) -> DhprojEnvelope {
    let project = Project(title: title, projectType: projectType)
    let firstTitle = projectType == .screenplay ? "Scene 1" : "Chapter 1"
    let firstSection = Section(
      novelId: project.id,
      order: 0,
      title: firstTitle,
      content: ""
    )

    return DhprojEnvelope(
      manifest: DhprojManifest(appVersion: currentAppVersion, exportOptions: ExportOptions()),
      project: project,
      projectType: projectType,
      sections: [firstSection]
    )
  }
}
