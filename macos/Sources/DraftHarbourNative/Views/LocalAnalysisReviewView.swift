import DraftHarbourNativeCore
import SwiftUI

struct LocalAnalysisReviewView: View {
  @Bindable var store: ProjectStore
  @State private var findings: [ManuscriptReviewFinding] = []
  @State private var overview = ""
  @State private var status = ""
  @State private var task: Task<Void, Never>?

  var body: some View {
    GroupBox("Local AI — All \(store.projectType == .screenplay ? "Scenes" : "Chapters")") {
      VStack(alignment: .leading, spacing: 12) {
        Text("Review plot, characters, pacing and voice using a local model. Suggestions do not change your draft.")
          .foregroundStyle(.secondary)
        HStack {
          Button("Review All \(store.projectType == .screenplay ? "Scenes" : "Chapters")") { start() }
            .disabled(task != nil || store.envelope.sections.isEmpty)
          if task != nil {
            Button("Cancel Review") { task?.cancel(); status = "Review cancelled. Partial feedback is shown below." }
          }
        }
        Text(status).font(.callout).foregroundStyle(.secondary)
        if !overview.isEmpty {
          Text("Overall Feedback And Suggestions").font(.headline)
          Text(overview).textSelection(.enabled)
        }
        ForEach(Array(findings.enumerated()), id: \.offset) { _, finding in
          DisclosureGroup(finding.title) { Text(finding.feedback).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }
        }
      }
      .frame(maxWidth: .infinity, alignment: .leading)
    }
    .onDisappear { task?.cancel() }
  }

  private func start() {
    let snapshot = store.envelope
    findings = []; overview = ""; status = "Connecting to local model…"
    task = Task { @MainActor in
      defer { task = nil }
      do {
        guard let config = UserDefaults.standard.string(forKey: "DraftHarbour.aiSetup.mode") == "local" ? AIProviderConfig.managedLocalDefault() : snapshot.aiProviders.first(where: { $0.enabled && NativeAIProviderFactory.isLocalProvider($0) }) else {
          throw LocalRuntimeFailure.unavailable("Configure a local model in Settings > AI before running Analysis.")
        }
        let provider = try NativeAIProviderFactory().provider(from: config)
        let result = try await LocalManuscriptReview.run(envelope: snapshot, provider: provider) { message, partial in
          await MainActor.run {
            if !Task.isCancelled { status = message; findings = partial }
          }
        }
        overview = result.overview
        status = "Review complete. \(result.emptyCount) empty sections skipped. Feedback refers to the manuscript at the start of this review."
      } catch {
        if !Task.isCancelled { status = error.localizedDescription }
      }
    }
  }
}
