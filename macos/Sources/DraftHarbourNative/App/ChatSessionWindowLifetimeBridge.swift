import AppKit
import DraftHarbourNativeCore
import SwiftUI

/// Closing a document cancels its request. Tab visibility and sidebar layout do not.
struct ChatSessionWindowLifetimeBridge: NSViewRepresentable {
  var session: AIChatSession
  func makeNSView(context: Context) -> WindowObserverView {
    let view = WindowObserverView()
    view.session = session
    return view
  }
  func updateNSView(_ view: WindowObserverView, context: Context) { view.session = session }

  final class WindowObserverView: NSView {
    var session: AIChatSession?
    private weak var observedWindow: NSWindow?
    override func viewDidMoveToWindow() {
      super.viewDidMoveToWindow()
      guard observedWindow !== window else { return }
      NotificationCenter.default.removeObserver(self, name: NSWindow.willCloseNotification, object: nil)
      observedWindow = window
      if let window {
        NotificationCenter.default.addObserver(self, selector: #selector(windowWillClose), name: NSWindow.willCloseNotification, object: window)
      }
    }
    @objc private func windowWillClose() { session?.cancel() }
  }
}
