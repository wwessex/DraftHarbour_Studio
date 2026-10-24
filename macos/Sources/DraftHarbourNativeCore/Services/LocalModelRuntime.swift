import CryptoKit
import Darwin
import Foundation
import Security

/// A reviewed artifact identity. No paths, download URLs or secrets come from a project.
public struct LocalRuntimeCatalog: Sendable {
  public var manifestSHA256: String
  public var platform: String
  public init(manifestSHA256: String, platform: String) {
    self.manifestSHA256 = manifestSHA256
    self.platform = platform
  }
  public static let development = LocalRuntimeCatalog(
    manifestSHA256: "bec8fcc53a370b0a19de9cef4a8f4234add5a31feb54dcad56a8b34b260eb4e3", platform: "darwin-arm64")
}

public struct LocalRuntimeManifest: Decodable, Sendable {
  public struct FileRecord: Decodable, Sendable { public var bytes: UInt64; public var sha256: String }
  public var schema_version: Int
  public var engine: String
  public var platform: String
  public var model_id: String
  public var context_limit: Int
  public var max_output_tokens: Int
  public var model: String
  public var executable: String
  public var files: [String: FileRecord]
}

public enum LocalRuntimeFailure: Error, LocalizedError {
  case unavailable(String)
  public var errorDescription: String? { if case .unavailable(let message) = self { return message }; return nil }
}

public enum LocalRuntimePackage {
  public static var platform: String {
    #if arch(arm64)
    return "darwin-arm64"
    #else
    return "darwin-x86_64"
    #endif
  }
  public static func sha256(_ url: URL) throws -> String {
    let handle = try FileHandle(forReadingFrom: url)
    defer { try? handle.close() }
    var hash = SHA256()
    while let data = try handle.read(upToCount: 8 * 1024 * 1024), !data.isEmpty { hash.update(data: data) }
    return hash.finalize().map { String(format: "%02x", $0) }.joined()
  }
  public static func file(_ name: String, in root: URL) throws -> URL {
    let parts = name.split(separator: "/", omittingEmptySubsequences: false)
    guard !name.isEmpty, !name.contains("\\"), !name.contains(":"),
          parts.allSatisfy({ !$0.isEmpty && $0 != "." && $0 != ".." }) else {
      throw LocalRuntimeFailure.unavailable("Unsafe local model package path.")
    }
    var path = root
    for part in parts {
      path.appendPathComponent(String(part))
      let values = try path.resourceValues(forKeys: [.isSymbolicLinkKey])
      guard values.isSymbolicLink != true else { throw LocalRuntimeFailure.unavailable("Linked package files are not allowed.") }
    }
    guard try path.resourceValues(forKeys: [.isRegularFileKey]).isRegularFile == true else {
      throw LocalRuntimeFailure.unavailable("A local model package file is missing.")
    }
    return path
  }
  public static func verify(_ root: URL, catalog: LocalRuntimeCatalog = .development, platform: String = Self.platform) throws -> LocalRuntimeManifest {
    let root = root.standardizedFileURL.resolvingSymlinksInPath()
    guard catalog.platform == platform else { throw LocalRuntimeFailure.unavailable("No verified model package is available for this computer yet.") }
    let manifestURL = try file("manifest.json", in: root)
    guard (try manifestURL.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? Int.max) <= 1_048_576,
          try sha256(manifestURL) == catalog.manifestSHA256 else {
      throw LocalRuntimeFailure.unavailable("Local model manifest verification failed.")
    }
    let manifest = try JSONDecoder().decode(LocalRuntimeManifest.self, from: Data(contentsOf: manifestURL))
    guard manifest.schema_version == 1, manifest.engine == "llama.cpp", manifest.platform == platform,
          manifest.model_id.range(of: "^[a-z0-9][a-z0-9._-]{0,127}$", options: .regularExpression) != nil,
          (512...4096).contains(manifest.context_limit), (1...512).contains(manifest.max_output_tokens),
          manifest.files[manifest.model] != nil, manifest.files[manifest.executable] != nil else {
      throw LocalRuntimeFailure.unavailable("Unsupported local model package.")
    }
    for (name, record) in manifest.files {
      let path = try file(name, in: root)
      guard UInt64(try path.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) == record.bytes,
            try sha256(path) == record.sha256 else { throw LocalRuntimeFailure.unavailable("Local model file verification failed.") }
    }
    var actual = Set<String>()
    // Build names relative to each directory. macOS URL enumeration can return
    // /private/var even when resolvingSymlinksInPath spells the root as /var.
    func inventory(_ directory: URL, prefix: String = "", depth: Int = 0) throws {
      guard depth <= 32 else { throw LocalRuntimeFailure.unavailable("Local package nesting is too deep.") }
      for name in try FileManager.default.contentsOfDirectory(atPath: directory.path) {
        let path = directory.appendingPathComponent(name)
        let values = try path.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey, .isDirectoryKey])
        guard values.isSymbolicLink != true else { throw LocalRuntimeFailure.unavailable("Linked package files are not allowed.") }
        if values.isRegularFile == true { actual.insert(prefix + name) }
        else if values.isDirectory == true { try inventory(path, prefix: prefix + name + "/", depth: depth + 1) }
        else { throw LocalRuntimeFailure.unavailable("Unsupported local package file.") }
      }
    }
    try inventory(root)
    guard actual == Set(manifest.files.keys).union(["manifest.json"]) else {
      throw LocalRuntimeFailure.unavailable("The local model package contains unverified files.")
    }
    return manifest
  }
}

// Synchronous process ownership also works during applicationWillTerminate.
private final class LocalRuntimeOwner: @unchecked Sendable {
  private let lock = NSLock()
  private var process: Process?
  private var folder: URL?
  private var revision = 0
  var epoch: Int { lock.withLock { revision } }
  var running: Bool { lock.withLock { process?.isRunning == true } }
  func install(_ child: Process, folder: URL, epoch: Int) throws {
    try lock.withLock {
      guard revision == epoch else { throw CancellationError() }
      self.process = child; self.folder = folder
      do { try child.run() } catch { self.process = nil; self.folder = nil; throw error }
    }
  }
  func stop() {
    lock.withLock {
      revision += 1
      if let process, process.isRunning {
        process.terminate()
        // SIGKILL is bounded and applies only to the owned child, never a discovered PID.
        let end = Date().addingTimeInterval(2)
        while process.isRunning && Date() < end { Thread.sleep(forTimeInterval: 0.02) }
        if process.isRunning { kill(process.processIdentifier, SIGKILL) }
      }
      process = nil
      if let folder { try? FileManager.default.removeItem(at: folder) }
      folder = nil
    }
  }
  deinit { stop() }
}

private final class LocalOnlySessionDelegate: NSObject, URLSessionTaskDelegate, @unchecked Sendable {
  func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse,
                  newRequest request: URLRequest, completionHandler: @escaping @Sendable (URLRequest?) -> Void) { completionHandler(nil) }
}

public actor NativeLocalModelRuntime {
  public static let shared = NativeLocalModelRuntime()
  public static let modelID = "narratryx-craft-v1-q4-k-m"
  public static let endpoint = "draftharbour-local://runtime"
  public static var packageURL: URL {
    FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
      .appendingPathComponent("DraftHarbour/LocalAI/bundle", isDirectory: true)
  }
  private nonisolated let owner = LocalRuntimeOwner()
  private let root: URL
  private let catalog: LocalRuntimeCatalog
  private var token = ""
  private var base: URL?
  private var busy = false
  private let session: URLSession
  public init(root: URL = NativeLocalModelRuntime.packageURL, catalog: LocalRuntimeCatalog = .development) {
    self.root = root; self.catalog = catalog
    let configuration = URLSessionConfiguration.ephemeral
    configuration.connectionProxyDictionary = [:]
    configuration.timeoutIntervalForRequest = 125
    self.session = URLSession(configuration: configuration, delegate: LocalOnlySessionDelegate(), delegateQueue: nil)
  }
  public nonisolated func stopNow() { owner.stop() }
  public func inspect() async throws -> String {
    let root = root, catalog = catalog
    let manifest = try await Task.detached { try LocalRuntimePackage.verify(root, catalog: catalog) }.value
    return manifest.model_id
  }
  private func request(_ path: String, body: Data? = nil, timeout: TimeInterval = 125) async throws -> Data {
    guard let base, owner.running else { throw LocalRuntimeFailure.unavailable("Local AI is stopped. Try again to restart it.") }
    var request = URLRequest(url: base.appendingPathComponent(path), timeoutInterval: timeout)
    request.httpMethod = body == nil ? "GET" : "POST"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.httpBody = body
    let (data, response) = try await session.data(for: request)
    guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
      throw LocalRuntimeFailure.unavailable("Local AI could not complete this request. Try a shorter passage or restart Local AI.")
    }
    return data
  }
  private func start() async throws {
    if owner.running { return }
    let epoch = owner.epoch
    let root = root, catalog = catalog
    let manifest = try await Task.detached { try LocalRuntimePackage.verify(root, catalog: catalog) }.value
    try Task.checkCancellation()
    guard epoch == owner.epoch else { throw CancellationError() }
    var bytes = [UInt8](repeating: 0, count: 32)
    guard SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes) == errSecSuccess else {
      throw LocalRuntimeFailure.unavailable("Unable to create private local authentication.")
    }
    token = bytes.map { String(format: "%02x", $0) }.joined()
    let folder = FileManager.default.temporaryDirectory.appendingPathComponent("draftharbour-local-\(UUID().uuidString)")
    try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: false, attributes: [.posixPermissions: 0o700])
    do {
      let key = folder.appendingPathComponent("access-token")
      guard FileManager.default.createFile(atPath: key.path, contents: Data((token + "\n").utf8), attributes: [.posixPermissions: 0o600]) else {
        throw LocalRuntimeFailure.unavailable("Unable to create private local authentication.")
      }
      let process = Process()
      process.executableURL = root.appendingPathComponent(manifest.executable)
      process.currentDirectoryURL = root
      // A reserved port is selected locally; any bind race fails readiness/authentication.
      let port = try Self.availablePort()
      base = URL(string: "http://127.0.0.1:\(port)")!
      process.arguments = ["-m", root.appendingPathComponent(manifest.model).path, "--host", "127.0.0.1", "--port", String(port),
        "--api-key-file", key.path, "--alias", manifest.model_id, "--ctx-size", String(manifest.context_limit),
        "--parallel", "1", "--no-context-shift", "--no-webui"]
      process.standardInput = FileHandle.nullDevice
      process.standardOutput = FileHandle.nullDevice; process.standardError = FileHandle.nullDevice
      try owner.install(process, folder: folder, epoch: epoch)
      let deadline = Date().addingTimeInterval(120)
      while Date() < deadline {
        try Task.checkCancellation()
        guard owner.running, owner.epoch == epoch else { throw LocalRuntimeFailure.unavailable("Local AI stopped during startup.") }
        if let data = try? await request("v1/models", timeout: 2),
           let payload = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let models = payload["data"] as? [[String: Any]], models.contains(where: { $0["id"] as? String == manifest.model_id }) { return }
        try await Task.sleep(for: .milliseconds(100))
      }
      throw LocalRuntimeFailure.unavailable("Local AI startup timed out.")
    } catch {
      owner.stop(); token = ""; base = nil
      try? FileManager.default.removeItem(at: folder)
      throw error
    }
  }
  private static func availablePort() throws -> UInt16 {
    let descriptor = socket(AF_INET, SOCK_STREAM, 0)
    guard descriptor >= 0 else { throw LocalRuntimeFailure.unavailable("Unable to reserve a local port.") }
    defer { close(descriptor) }
    var address = sockaddr_in(); address.sin_family = sa_family_t(AF_INET); address.sin_addr.s_addr = inet_addr("127.0.0.1")
    let bound = withUnsafePointer(to: &address) { pointer in
      pointer.withMemoryRebound(to: sockaddr.self, capacity: 1) { bind(descriptor, $0, socklen_t(MemoryLayout<sockaddr_in>.size)) }
    }
    var size = socklen_t(MemoryLayout<sockaddr_in>.size)
    let named = withUnsafeMutablePointer(to: &address) { pointer in
      pointer.withMemoryRebound(to: sockaddr.self, capacity: 1) { getsockname(descriptor, $0, &size) }
    }
    guard bound == 0, named == 0 else { throw LocalRuntimeFailure.unavailable("Unable to reserve a local port.") }
    return UInt16(bigEndian: address.sin_port)
  }
  public func generate(_ request: AIRequest) async throws -> AIResponse {
    guard !busy else { throw LocalRuntimeFailure.unavailable("Local AI is already generating a draft.") }
    let policy = NativeOperationalGuardrails.shared.currentPolicy()
    guard policy.disableAIProviders != true, policy.disabledAIProviderTypes?.contains(.customLLM) != true else {
      throw LocalRuntimeFailure.unavailable("Local AI is disabled by managed policy.")
    }
    busy = true
    defer { busy = false }
    return try await withTaskCancellationHandler {
      do {
        try await start()
        try Task.checkCancellation()
        let prompt = [request.context ?? "", request.prompt].filter { !$0.isEmpty }.joined(separator: "\n\n")
        guard prompt.utf8.count <= 65_536 else { throw LocalRuntimeFailure.unavailable("Use a shorter passage for Local AI.") }
        let payload: [String: Any] = ["model": Self.modelID, "messages": [["role": "user", "content": prompt]],
          "max_tokens": 512, "stream": false, "temperature": 0, "seed": 42, "cache_prompt": false,
          "chat_template_kwargs": ["enable_thinking": false]]
        let started = Date()
        let data = try await self.request("v1/chat/completions", body: JSONSerialization.data(withJSONObject: payload))
        try Task.checkCancellation()
        let decoded = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        let choices = decoded?["choices"] as? [[String: Any]]
        let message = choices?.first?["message"] as? [String: Any]
        guard let text = message?["content"] as? String, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
          throw LocalRuntimeFailure.unavailable("Local AI returned no draft.")
        }
        return AIResponse(text: text, provider: "managed-local", model: Self.modelID, latencyMs: Int(Date().timeIntervalSince(started) * 1000))
      } catch { owner.stop(); token = ""; base = nil; throw error }
    } onCancel: { self.owner.stop() }
  }
}

public struct ManagedLocalAIProvider: AIProvider {
  public var id: String
  public var displayName: String { "On this computer (experimental)" }
  public init(id: String = "managed-local") { self.id = id }
  public func generate(_ request: AIRequest) async throws -> AIResponse { try await NativeLocalModelRuntime.shared.generate(request) }
}
