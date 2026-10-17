import Foundation
import ZIPFoundation

public struct EPUBExporter: Exporter {
  public let format: ExportFormat = .epub
  public init() {}
  public func export(_ envelope: DhprojEnvelope, request: ExportRequest) throws -> ExportedFile {
    guard !envelope.sections.isEmpty else { throw CocoaError(.fileWriteInvalidFileName) }
    let archive = try Archive(data: Data(), accessMode: .create)
    func add(_ name: String, _ text: String, stored: Bool = false) throws {
      let data = Data(text.utf8)
      try archive.addEntry(with: name, type: .file, uncompressedSize: Int64(data.count), compressionMethod: stored ? .none : .deflate) { position, size in
        data.subdata(in: Int(position)..<Int(position) + size)
      }
    }
    try add("mimetype", "application/epub+zip", stored: true)
    try add("META-INF/container.xml", """
    <?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>
    """)
    var manifest = "", spine = "", contents = ""
    for (index, section) in envelope.sections.enumerated() {
      let id = "ch\(index + 1)", filename = "chapter-\(index + 1).xhtml"
      manifest += "<item id=\"\(id)\" href=\"\(filename)\" media-type=\"application/xhtml+xml\"/>"
      spine += "<itemref idref=\"\(id)\"/>"
      contents += "<li><a href=\"\(filename)\">\(xml(section.title))</a></li>"
      let prose = (section.content ?? "").replacingOccurrences(of: #"!\[([^\]]*)\]\([^\)]*\)"#, with: "[Image omitted from text-only EPUB: $1]", options: .regularExpression)
      let paragraphs = prose.components(separatedBy: "\n").map { line -> String in
        var text = xml(line)
        text = text.replacingOccurrences(of: #"\*\*([^*]+)\*\*"#, with: "<strong>$1</strong>", options: .regularExpression)
        text = text.replacingOccurrences(of: #"\*([^*]+)\*"#, with: "<em>$1</em>", options: .regularExpression)
        return "<p>\(text.isEmpty ? "<br/>" : text)</p>"
      }.joined(separator: "\n")
      try add("EPUB/" + filename, """
      <?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml" lang="en"><head><title>\(xml(section.title))</title></head><body><h1>\(xml(section.title))</h1>\(paragraphs)</body></html>
      """)
    }
    try add("EPUB/nav.xhtml", """
    <?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head><title>Contents</title></head><body><nav epub:type="toc"><h1>Contents</h1><ol>\(contents)</ol></nav></body></html>
    """)
    let formatter = ISO8601DateFormatter()
    try add("EPUB/package.opf", """
    <?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:uuid:\(makeIdentifier())</dc:identifier><dc:title>\(xml(envelope.project.title))</dc:title><dc:language>en</dc:language><meta property="dcterms:modified">\(formatter.string(from: Date()))</meta></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>\(manifest)</manifest><spine>\(spine)</spine></package>
    """)
    guard let data = archive.data else { throw CocoaError(.fileWriteUnknown) }
    let filename = envelope.project.title.replacingOccurrences(of: "/", with: "-") + ".epub"
    return ExportedFile(filename: filename, contentType: "application/epub+zip", data: data)
  }
  private func xml(_ text: String) -> String {
    text.replacingOccurrences(of: "&", with: "&amp;").replacingOccurrences(of: "<", with: "&lt;").replacingOccurrences(of: ">", with: "&gt;").replacingOccurrences(of: "\"", with: "&quot;").replacingOccurrences(of: "'", with: "&apos;")
  }
}
