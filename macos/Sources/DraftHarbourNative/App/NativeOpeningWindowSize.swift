import AppKit
import SwiftUI

@MainActor
enum NativeOpeningWindowSize {
  /// Use the normal desktop work area, excluding the menu bar and Dock.
  static func fillUsableScreen(_ window: NSWindow) {
    guard !window.styleMask.contains(.fullScreen), let screen = window.screen ?? NSScreen.main else { return }
    window.setFrame(screen.visibleFrame, display: true, animate: false)
  }
}

/// Applies once per document window, after AppKit has placed/restored it.
/// Subsequent activation and author resizing do not reapply the opening size.
struct NativeOpeningWindowSizeBridge: NSViewRepresentable {
  func makeNSView(context: Context) -> OpeningWindowView { OpeningWindowView() }
  func updateNSView(_ nsView: OpeningWindowView, context: Context) {}

  final class OpeningWindowView: NSView {
    private weak var fittedWindow: NSWindow?

    override func viewDidMoveToWindow() {
      super.viewDidMoveToWindow()
      NotificationCenter.default.removeObserver(self, name: NSWindow.didBecomeKeyNotification, object: nil)
      guard let window, fittedWindow !== window else { return }
      NotificationCenter.default.addObserver(self, selector: #selector(windowBecameKey(_:)), name: NSWindow.didBecomeKeyNotification, object: window)
      DispatchQueue.main.async { [weak self, weak window] in
        guard let self, let window, window.isVisible else { return }
        self.fitOnce(window)
      }
    }

    @objc private func windowBecameKey(_ notification: Notification) {
      guard let window = notification.object as? NSWindow else { return }
      fitOnce(window)
    }

    private func fitOnce(_ window: NSWindow) {
      guard fittedWindow !== window else { return }
      fittedWindow = window
      NotificationCenter.default.removeObserver(self, name: NSWindow.didBecomeKeyNotification, object: window)
      NativeOpeningWindowSize.fillUsableScreen(window)
    }
  }
}
