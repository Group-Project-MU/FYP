from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt

DEFAULT_FRAMELESS_RESIZE_MARGIN = 6


def frameless_edges_at(
    window: QtWidgets.QWidget,
    local_pos: QtCore.QPoint,
    margin: int = DEFAULT_FRAMELESS_RESIZE_MARGIN,
) -> QtCore.Qt.Edge:
   
    w, h = window.width(), window.height()
    if w < margin * 2 or h < margin * 2:
        return QtCore.Qt.Edge(0)
    x, y = local_pos.x(), local_pos.y()
    edges = QtCore.Qt.Edge(0)
    if x <= margin:
        edges |= QtCore.Qt.Edge.LeftEdge
    if y <= margin:
        edges |= QtCore.Qt.Edge.TopEdge
    if x >= w - margin:
        edges |= QtCore.Qt.Edge.RightEdge
    if y >= h - margin:
        edges |= QtCore.Qt.Edge.BottomEdge
    return edges


class FramelessResizeSupport(QtCore.QObject):

    def __init__(
        self,
        window: QtWidgets.QWidget,
        margin: int = DEFAULT_FRAMELESS_RESIZE_MARGIN,
    ):
        super().__init__(window)
        self._window = window
        self._margin = margin
        app = QtWidgets.QApplication.instance()
        if app:
            app.installEventFilter(self)

    def cleanup(self):
        app = QtWidgets.QApplication.instance()
        if app:
            app.removeEventFilter(self)

    def eventFilter(self, watched, event):
        w = self._window
        if (
            event.type() == QtCore.QEvent.Type.MouseButtonPress
            and isinstance(event, QtGui.QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and w is not None
            and w.isVisible()
            and not w.isMaximized()
        ):
            gp = event.globalPosition().toPoint()
            if QtWidgets.QApplication.topLevelAt(gp) == w:
                local = w.mapFromGlobal(gp)
                if w.rect().contains(local):
                    edges = frameless_edges_at(w, local, self._margin)
                    if edges:
                        wh = w.windowHandle()
                        if wh is not None and wh.startSystemResize(edges):
                            return True
        return super().eventFilter(watched, event)


def enable_frameless_resize(
    window: QtWidgets.QWidget,
    margin: int = DEFAULT_FRAMELESS_RESIZE_MARGIN,
) -> FramelessResizeSupport:

    return FramelessResizeSupport(window, margin)


class CustomTitleBar(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

        self.setStyleSheet("""
            QWidget {
                border: none;
                border-radius: 9px;
            }
            QLabel {
                color: #6488EA;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #6488EA;
                font-size: 16px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.4);
            }
            QPushButton#closeButton:hover {
                background: #E74C3C;
            }
        """)
        self._setup_ui()
        self.oldposition = None
    
    def _setup_ui(self):
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 1, 1, 1)
        layout.setSpacing(10)
        
        self.title_label = QtWidgets.QLabel("Advanced Network Scanner")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)

        self.minimize_btn = QtWidgets.QPushButton("−")
        self.minimize_btn.setFixedSize(40, 40)
        self.minimize_btn.setToolTip("Minimize")
        self.minimize_btn.clicked.connect(self._minimize_window)
        
        self.maximize_btn = QtWidgets.QPushButton("□")
        self.maximize_btn.setFixedSize(40, 40)
        self.maximize_btn.setToolTip("Maximize")
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        
        self.close_btn = QtWidgets.QPushButton("×")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self._close_window)

        layout.addStretch(1)
        layout.addWidget(self.title_label, 1)
        layout.addStretch(1)
        layout.addWidget(self.minimize_btn, 1)
        layout.addWidget(self.maximize_btn, 1)
        layout.addWidget(self.close_btn, 1)
    
    def set_title(self, title):
        self.title_label.setText(title)
    
    def _minimize_window(self):
        if self.parent_window:
            self.parent_window.showMinimized()
    
    def _toggle_maximize(self):
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
                self.maximize_btn.setText("□")
                self.maximize_btn.setToolTip("Maximize")
            else:
                self.parent_window.showMaximized()
                self.maximize_btn.setText("▢")
                self.maximize_btn.setToolTip("Restore")
    
    def _close_window(self):
        if self.parent_window:
            self.parent_window.close()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldposition = event.globalPosition().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.oldposition and event.buttons() == Qt.MouseButton.LeftButton:
            if self.parent_window:
                delta = event.globalPosition().toPoint() - self.oldposition
                new_pos = self.parent_window.pos() + delta
                self.parent_window.move(new_pos)
                self.oldposition = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.oldposition = None
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()
        super().mouseDoubleClickEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
