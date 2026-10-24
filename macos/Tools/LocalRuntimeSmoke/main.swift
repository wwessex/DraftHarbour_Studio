import DraftHarbourNativeCore
import Foundation

/// Explicit development smoke, never part of app startup or training.
@main struct LocalRuntimeSmoke {
  static func main() async throws {
    guard CommandLine.arguments.count == 2 else { fatalError("Pass the verified development bundle directory") }
    let runtime = NativeLocalModelRuntime(root: URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true))
    defer { runtime.stopNow() }
    let model = try await runtime.inspect()
    let response = try await runtime.generate(AIRequest(prompt: "Continue in two sentences: A gull called across the quay.", projectType: .book))
    print("Native runtime model: \(model); nonempty: \(!response.text.isEmpty); latency_ms: \(response.latencyMs ?? 0)")
    let task = Task { try await runtime.generate(AIRequest(prompt: "Write a long harbour scene.", projectType: .book)) }
    try await Task.sleep(for: .milliseconds(300))
    task.cancel()
    var returnedDraft = false
    do { _ = try await task.value; returnedDraft = true }
    catch { if !task.isCancelled { throw error } }
    guard !returnedDraft else { throw LocalRuntimeFailure.unavailable("Cancellation returned a draft") }
    print("Native runtime cancellation: stopped without a draft")
    runtime.stopNow()
  }
}
