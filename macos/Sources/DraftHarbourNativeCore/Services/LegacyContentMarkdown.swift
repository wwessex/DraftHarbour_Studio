import Foundation

/// Legacy rich-text documents use the same Markdown storage as current native drafts.
enum LegacyContentMarkdown {
  static func convert(_ value: Any, depth: Int = 0) -> String {
    guard depth < 100 else { return "" }
    if let text = value as? String { return text }
    guard let node = value as? [String: Any] else { return "" }
    let children = (node["content"] as? [Any] ?? []).map { convert($0, depth: depth + 1) }
    let text = children.joined()
    let type = node["type"] as? String ?? ""
    switch type {
    case "text":
      var result = node["text"] as? String ?? ""
      for mark in node["marks"] as? [[String: Any]] ?? [] {
        switch mark["type"] as? String {
        case "bold": result = "**" + result + "**"
        case "italic": result = "*" + result + "*"
        case "strike": result = "~~" + result + "~~"
        case "code": result = "`" + result + "`"
        default: break
        }
      }
      return result
    case "paragraph": return text + "\n\n"
    case "heading": return String(repeating: "#", count: min(6, max(1, (node["attrs"] as? [String: Any])?["level"] as? Int ?? 1))) + " " + text + "\n\n"
    case "hardBreak": return "\n"
    case "horizontalRule": return "\n---\n\n"
    case "blockquote": return text.components(separatedBy: "\n").map { "> " + $0 }.joined(separator: "\n") + "\n\n"
    case "codeBlock": return "```\n" + text + "\n```\n\n"
    case "listItem": return "- " + text.trimmingCharacters(in: .newlines) + "\n"
    case "image":
      let attrs = node["attrs"] as? [String: Any] ?? [:]
      return "![" + (attrs["alt"] as? String ?? "") + "](" + (attrs["src"] as? String ?? "") + ")"
    default: return text
    }
  }

  static func normalizeEnvelope(_ data: Data) throws -> Data {
    guard var object = try JSONSerialization.jsonObject(with: data) as? [String: Any] else { return data }
    for collection in ["sections", "snapshots"] {
      let field = collection == "sections" ? "content" : "doc"
      guard var entries = object[collection] as? [[String: Any]] else { continue }
      for index in entries.indices {
        if let document = entries[index][field] as? [String: Any] {
          entries[index][field] = convert(document).trimmingCharacters(in: .newlines)
        }
        if collection == "sections", var sync = entries[index]["sync"] as? [String: Any], let baseline = sync["lastSyncedContent"] as? [String: Any] {
          sync["lastSyncedContent"] = convert(baseline).trimmingCharacters(in: .newlines)
          entries[index]["sync"] = sync
        }
      }
      object[collection] = entries
    }
    return try JSONSerialization.data(withJSONObject: object)
  }
}
