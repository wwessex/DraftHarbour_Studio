import DraftHarbourNativeCore
import Foundation

/// Explicit development smoke, never part of app startup or training.
@main struct LocalRuntimeSmoke {
  static func main() async throws {
    let arguments = CommandLine.arguments
    let runtime: NativeLocalModelRuntime
    if arguments.count == 4, arguments[1] == "--install-test" {
      let source = URL(fileURLWithPath: arguments[2], isDirectory: true)
      let destination = URL(fileURLWithPath: arguments[3], isDirectory: true)
      guard !FileManager.default.fileExists(atPath: destination.path) else { throw LocalRuntimeFailure.unavailable("Installation smoke requires a fresh destination") }
      runtime = NativeLocalModelRuntime(root: destination)
      for _ in 0..<2 { _ = try await runtime.install(from: source) }
      _ = try await runtime.restorePrevious()
      print("Native verified installation, replacement and restore: passed")
    } else {
      guard arguments.count == 2 else { fatalError("Pass an existing bundle, or --install-test source fresh-destination") }
      runtime = NativeLocalModelRuntime(root: URL(fileURLWithPath: arguments[1], isDirectory: true))
    }
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
