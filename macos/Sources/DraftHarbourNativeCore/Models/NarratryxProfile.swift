import Foundation

/// Setup metadata only. Model serving and training remain outside the application.
public enum NarratryxProfile {
  public static let model = "narratryx-craft-v1"
  public static let baseModel = "narratryx-base"
  public static let label = "Narratryx (experimental)"
  public static let help = "Experimental fiction model. Review every suggestion; improved literary quality is not established. Connect to your inference service—no training is required on this device."

  public static func configuration(endpoint: String = "", id: String = makeIdentifier()) -> AIProviderConfig {
    AIProviderConfig(
      id: id,
      provider: .customLLM,
      label: label,
      endpoint: endpoint.trimmingCharacters(in: .whitespacesAndNewlines),
      model: model,
      keychainAccount: nil
    )
  }

  public static func recognizes(_ model: String) -> Bool {
    model.hasPrefix("narratryx-")
  }
}
