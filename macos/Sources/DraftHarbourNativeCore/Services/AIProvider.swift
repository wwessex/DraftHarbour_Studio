import Foundation

public struct AIRequest: Codable, Equatable, Sendable {
  public static let naturalWritingStyle = "Writing style: Follow the author's task, requested voice, language, scope and output format first. For new prose and rewrites, match the supplied author's voice, viewpoint, tense and register. Prefer concrete details, precise verbs, natural dialogue and varied sentence lengths. Avoid stock phrases, repetitive rhythms, inflated language, generic transitions and unnecessary summaries or explanations. For chat, feedback and suggestions, be direct, specific and conversational. Do not add deliberate mistakes, invented facts or claims of human authorship. For copyediting, grammar, translation and structured output, preserve meaning, edit boundaries, exact anchors and required schemas; apply style only where the task permits. Return only the requested output."

  public var styledPrompt: String {
    prompt.hasPrefix(Self.naturalWritingStyle + "\n\n") ? prompt : Self.naturalWritingStyle + "\n\n" + prompt
  }

  public var prompt: String
  public var context: String?
  public var projectType: ProjectType
  public var sectionTitle: String?
  public var model: String?

  public init(prompt: String, context: String? = nil, projectType: ProjectType, sectionTitle: String? = nil, model: String? = nil) {
    self.prompt = prompt
    self.context = context
    self.projectType = projectType
    self.sectionTitle = sectionTitle
    self.model = model
  }
}

public struct AIResponse: Codable, Equatable, Sendable {
  public var text: String
  public var provider: String
  public var model: String?
  public var latencyMs: Int?

  public init(text: String, provider: String, model: String? = nil, latencyMs: Int? = nil) {
    self.text = text
    self.provider = provider
    self.model = model
    self.latencyMs = latencyMs
  }
}

public protocol AIProvider: Sendable {
  var id: String { get }
  var displayName: String { get }
  func generate(_ request: AIRequest) async throws -> AIResponse
}

private final class AIEndpointSessionDelegate: NSObject, URLSessionTaskDelegate, @unchecked Sendable {
  func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse,
                  newRequest request: URLRequest, completionHandler: @escaping @Sendable (URLRequest?) -> Void) {
    completionHandler(nil)
  }
}

public struct OpenAICompatibleProvider: AIProvider {
  public var id: String
  public var displayName: String
  public var endpoint: URL
  public var apiKey: String?
  public var defaultModel: String
  public var session: URLSession

  public init(id: String, displayName: String, endpoint: URL, apiKey: String?, defaultModel: String, session: URLSession = .shared) {
    self.id = id
    self.displayName = displayName
    self.endpoint = endpoint
    self.apiKey = apiKey
    self.defaultModel = defaultModel
    self.session = session
  }

  public func generate(_ request: AIRequest) async throws -> AIResponse {
    let isLoopback = ["localhost", "127.0.0.1", "::1", "[::1]"].contains(endpoint.host?.lowercased() ?? "")
    guard apiKey?.isEmpty == false || isLoopback else {
      throw DraftHarbourError.providerNotConfigured(displayName)
    }

    let started = Date()
    var urlRequest = URLRequest(url: endpoint)
    if NarratryxProfile.recognizes(request.model ?? defaultModel) {
      urlRequest.timeoutInterval = 125
    }
    urlRequest.httpMethod = "POST"
    urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
    if let apiKey, !apiKey.isEmpty {
      urlRequest.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
    }

    let prompt = buildPrompt(request)
    let payload = ChatCompletionPayload(
      model: request.model ?? defaultModel,
      messages: [
        ChatMessage(role: "system", content: "You are DraftHarbour's native macOS writing assistant."),
        ChatMessage(role: "user", content: prompt)
      ]
    )
    urlRequest.httpBody = try JSONEncoder().encode(payload)

    let data: Data
    let response: URLResponse
    do {
      (data, response) = try await session.data(for: urlRequest, delegate: AIEndpointSessionDelegate())
    } catch let error as URLError where [.cannotConnectToHost, .cannotFindHost, .networkConnectionLost, .notConnectedToInternet, .timedOut].contains(error.code) {
      let local = ["localhost", "127.0.0.1", "::1", "[::1]"].contains(endpoint.host?.lowercased() ?? "")
      throw LocalRuntimeFailure.unavailable(local
        ? "Cannot reach the local AI server. Start your local model service, check its address in Settings > AI, then retry."
        : "Cannot reach the AI server. Check your connection and endpoint in Settings > AI, then retry.")
    }
    if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
      let payload = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
      let details = (payload?["error"] as? [String: Any])?["message"] as? String
      let explanation = details.map { " — " + String($0.prefix(240)) } ?? ""
      throw DraftHarbourError.providerNotConfigured("\(displayName) HTTP \(http.statusCode)\(explanation)")
    }

    let decoded = try JSONDecoder().decode(ChatCompletionResponse.self, from: data)
    return AIResponse(
      text: decoded.choices.first?.message.content ?? "",
      provider: id,
      model: request.model ?? defaultModel,
      latencyMs: Int(Date().timeIntervalSince(started) * 1000)
    )
  }

  private func buildPrompt(_ request: AIRequest) -> String {
    let sectionLabel = request.projectType == .screenplay ? "scene" : "chapter"
    if let context = request.context, !context.isEmpty {
      return "Current \(sectionLabel): \(request.sectionTitle ?? "Untitled")\n\n---\n\(context)\n---\n\n\(request.styledPrompt)"
    }
    return request.styledPrompt
  }
}

private struct ChatCompletionPayload: Codable {
  var model: String
  var messages: [ChatMessage]
}

private struct ChatMessage: Codable {
  var role: String
  var content: String
}

private struct ChatCompletionResponse: Codable {
  var choices: [Choice]

  struct Choice: Codable {
    var message: ChatMessage
  }
}
