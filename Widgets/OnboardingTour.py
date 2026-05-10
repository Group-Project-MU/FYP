import os, sys
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, QPoint
from Widgets import ScannerStyle

class Onboarding(QWidget):

    def __init__(self, parent, steps, on_complete=None):
        super().__init__(parent)
        self.steps = steps
        self.current_step = 0
        self._on_complete = on_complete

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.bubble = QFrame(self)
        self.bubble.setStyleSheet(
            "background: #EAF3FF;"
        )
        self.bubble_layout = QVBoxLayout(self.bubble)

        self.label = QLabel("")
        self.label.setStyleSheet(
            "background: #FFFFFF; color: #2E3A59; font-size: 16px; font-weight: 500;"
            "border: none; border-radius: 12px; padding: 18px 20px;"
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setMinimumWidth(280)
        self.label.setMaximumWidth(420)

        bottom = QHBoxLayout()
        bottom.addStretch()

        self.close_btn = QPushButton("close")
        self.close_btn.setStyleSheet(ScannerStyle.btncstylesheet)
        self.close_btn.setFixedSize(75, 40)
        self.close_btn.clicked.connect(self._finish_onboarding)
        bottom.addWidget(self.close_btn)
        bottom.addStretch()

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedSize(75, 40)
        self.next_btn.setStyleSheet(ScannerStyle.btnestylesheet)
        self.next_btn.clicked.connect(self.next_step)
        bottom.addWidget(self.next_btn)
        bottom.addStretch()

        self.bubble_layout.addWidget(self.label)
        self.bubble_layout.addLayout(bottom)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())
        if self.current_step < len(self.steps):
            self._place_bubble()

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.raise_()
        self.current_step = 0
        self.update_step()

    def _parse_step(self, index):
        step = self.steps[index]
        if len(step) >= 3:
            w, text, on_show = step[0], step[1], step[2]
        else:
            w, text, on_show = step[0], step[1], None
        return w, text, on_show

    def _invoke_complete(self):
        if self._on_complete is not None:
            cb = self._on_complete
            self._on_complete = None
            cb()

    def _finish_onboarding(self):
        self._invoke_complete()
        self.hide()

    def update_step(self):
        if self.current_step >= len(self.steps):
            self._invoke_complete()
            self.hide()
            return

        widget, text, on_show = self._parse_step(self.current_step)
        if on_show:
            on_show()

        self.label.setText(text)
        is_last = self.current_step >= len(self.steps) - 1
        self.next_btn.setText("Finish" if is_last else "Next")

        self._place_bubble()
        self.bubble.show()
        self.raise_()

    def _place_bubble(self):
        if self.current_step >= len(self.steps):
            return
        widget, _, _ = self._parse_step(self.current_step)
        if not self.parent():
            self.bubble.move(24, 80)
            return

        self.bubble.adjustSize()
        bubble_width, bubble_height = self.bubble.width(), self.bubble.height()

        if widget is None:
            x = max(8, (self.width() - bubble_width) // 2)
            y = max(8, (self.height() - bubble_height) // 2)
            self.bubble.move(x, y)
            return

        try:
            pos = widget.mapTo(self.parent(), QPoint(0, 0))
        except Exception:
            self.bubble.move(24, 80)
            return

        x = max(8, min(pos.x(), self.width() - bubble_width - 8))
        y = pos.y() + widget.height() + 10
        if y + bubble_height > self.height() - 8:
            y = max(8, pos.y() - bubble_height - 10)
        self.bubble.move(x, y)

    def next_step(self):
        self.current_step += 1
        self.update_step()


def build_program_tour_steps(main_window):

    m = main_window

    def safe(obj, fallback):
        return obj if obj is not None else fallback

    def tab_loc(tabs, index: int):

        try:
            bar = tabs.tabBar()
            r = bar.tabRect(index)
            tab = QWidget(m)
            tab.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            tab.setFixedSize(r.size())
            tab.move(bar.mapTo(m, r.topLeft()))
            tab.show()
            return tab
        except Exception:
            return tabs

    left = getattr(m, "leftwidget", m)
    top = getattr(m, "topwidget", m)
    stack = getattr(m, "stack", m)
    middle = getattr(m, "middlewidget", m)

    home = getattr(m, "homewidget", stack)
    qscan = getattr(m, "qscanwidget", stack)
    cscan = getattr(m, "cscanwidget", stack)
    vscan = getattr(m, "vscanwidget", stack)
    adv = getattr(m, "ascanwidget", stack)

    qscan_tabs = getattr(qscan, "tabs", None)
    cscan_tabs = getattr(cscan, "tabs", None)
    vscan_tabs = getattr(vscan, "tabs", None)

    return [
        (
            None,
            "Welcome to the Advanced Network Scanner!"
            "This is a guide to help you get started with the app!"
            "Before we start, please make sure you have Nmap installed on your system."
            "For details, please refer to the Help menu.",
            None,
        ),
        (
            stack,
            "Vulnerability Dashboard: Shows worldwide and regional vulnerabilities.",
            lambda: stack.setCurrentWidget(home) if hasattr(stack, "setCurrentWidget") else None,
        ),
        (
            left,
            "Quick Function Panel: Access commonly used functions by clicking buttons.",
            None,
        ),
        (
            getattr(left, "hisbtn", left),
            "History Panel: Toggle visibility and resize by dragging the handle.",
            None,
        ),
        (
            getattr(left, "qscanbtn", left),
            "Quick Scan: Fast scan of common ports for initial assessment.",
            lambda: stack.setCurrentWidget(qscan) if hasattr(stack, "setCurrentWidget") else None,
        ),
        (
            tab_loc(qscan_tabs, 0) if qscan_tabs else safe(qscan, stack),
            "Quick Scan - Text Output: Shows quick summary and terminal-style Nmap output.",
            lambda: (stack.setCurrentWidget(qscan), qscan_tabs.setCurrentIndex(0)) if qscan_tabs else (stack.setCurrentWidget(qscan) if hasattr(stack, "setCurrentWidget") else None),
        ),
        (
            tab_loc(qscan_tabs, 1) if qscan_tabs else safe(qscan, stack),
            "Quick Scan - Tree View: Shows results in a hierarchical view (host/protocol/port/service).",
            lambda: (stack.setCurrentWidget(qscan), qscan_tabs.setCurrentIndex(1)) if qscan_tabs else (stack.setCurrentWidget(qscan) if hasattr(stack, "setCurrentWidget") else None),
        ),
        (
            getattr(left, "cscanbtn", left),
            "Comprehensive Scan: Wider port range with OS detection and host details.",
            lambda: stack.setCurrentWidget(cscan) if hasattr(stack, "setCurrentWidget") else None,
        ),
        (
            tab_loc(cscan_tabs, 2) if cscan_tabs else safe(cscan, stack),
            "Comprehensive Scan - Detailed Result: Shows per-host detailed information in tabs (addresses, ports, OS match).",
            lambda: (stack.setCurrentWidget(cscan), cscan_tabs.setCurrentIndex(2)) if cscan_tabs else (stack.setCurrentWidget(cscan) if hasattr(stack, "setCurrentWidget") else None),
        ),
        (
            getattr(left, "vscanbtn", left),
            "Vulnerability Scan: Detects vulnerabilities using Nmap scripts (avoid scanning many targets).",
            lambda: stack.setCurrentWidget(vscan) if hasattr(stack, "setCurrentWidget") else None,
        ),
        (
            tab_loc(vscan_tabs, 2) if vscan_tabs else safe(vscan, stack),
            "Vulnerability Scan - Vulnerability Result: Grouped the detected scripts into sections to improve the readability.",
            lambda: (stack.setCurrentWidget(vscan), vscan_tabs.setCurrentIndex(2)) if vscan_tabs else (stack.setCurrentWidget(vscan) if hasattr(stack, "setCurrentWidget") else None),
        ),
        (
            tab_loc(vscan_tabs, 3) if vscan_tabs else safe(vscan, stack),
            "Vulnerability Scan - Vulnerability Solutions: Click the View button to ask for AI-generated explanations and fixes.",
            lambda: (stack.setCurrentWidget(vscan), vscan_tabs.setCurrentIndex(3)) if vscan_tabs else (stack.setCurrentWidget(vscan) if hasattr(stack, "setCurrentWidget") else None),
        ),
        (
            getattr(top, "scanbtn", top),
            "Custom Scan: Execute custom Nmap commands or use pre-defined scripts.",
            lambda: stack.setCurrentWidget(adv) if hasattr(stack, "setCurrentWidget") else None,
        ),
        (
            getattr(top, "exportbtn", top),
            "Export: Save current or historical scan results.",
            None,
        ),
        (
            getattr(top, "helpbtn", top),
            "Help: Access user guide with steps and tips.",
            None,
        ),
        (
            getattr(top, "settingbtn", top),
            "Settings: Configure Nmap path and API keys.",
            None,
        ),
        (
            safe(middle, m),
            "History Panel: Browse and search previous scan results.",
            None,
        ),
    ]


def program_onboarding(main_window, on_complete=None):
    steps = build_program_tour_steps(main_window)
    tour = Onboarding(main_window, steps, on_complete=on_complete)
    tour.setGeometry(main_window.rect())
    tour.show()
    tour.raise_()
    return tour


def init_onboarding(main_window, on_complete=None):
    from Widgets.ConfigLoader import onboarding_done, show_onboarding

    if not show_onboarding():
        return None

    def _on_done():
        onboarding_done()
        if on_complete:
            on_complete()

    return program_onboarding(main_window, on_complete=_on_done)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)

    from GUI import Main

    app = QApplication(sys.argv)
    window = Main()
    window.show()
    program_onboarding(window)
    sys.exit(app.exec())
