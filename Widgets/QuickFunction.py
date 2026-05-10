import os
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QIcon
from Widgets import ScannerStyle

class QuickFunction(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.isHide = False
        cwd = os.getcwd()
        self.filepath = os.path.join(cwd, "Icons")
        self.layout()

    def layout(self):

        grid = QtWidgets.QVBoxLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        box_container = QtWidgets.QWidget(self)
        box_container.setStyleSheet(ScannerStyle.leftbtnstylesheet)
        box = QtWidgets.QHBoxLayout(box_container)
        box_container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)
        box.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.note = QtWidgets.QLabel()
        self.note.setText('Quick Function')
        self.note.setStyleSheet(ScannerStyle.leftlabelstyle)
        self.note.setFixedSize(150, 50)
        self.hidebtn = QtWidgets.QPushButton()
        self.hidebtn.clicked.connect(self.hidden)
        self.hidebtn.setIcon(QIcon(os.path.join(self.filepath, "list-exp.png")))
        self.hidebtn.setStyleSheet(ScannerStyle.backbtnstylesheet)
        self.hidebtn.setFixedSize(50, 50)
        box.addWidget(self.note)
        box.addWidget(self.hidebtn)

        self.homebtn = QtWidgets.QPushButton()
        self.homebtn.setCheckable(True)
        self.homebtn.setText('Home')
        self.homebtn.setIcon(QIcon(os.path.join(self.filepath, "home.png")))
        self.homebtn.setFixedHeight(50)
        self.homebtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)

        self.hisbtn = QtWidgets.QPushButton()
        self.hisbtn.setCheckable(True)
        self.hisbtn.setText('History')
        self.hisbtn.setIcon(QIcon(os.path.join(self.filepath, "history.png")))
        self.hisbtn.setFixedHeight(50)
        self.hisbtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)
        self.hisbtn.setChecked(True)

        self.qscanbtn = QtWidgets.QPushButton()
        self.qscanbtn.setCheckable(True)
        self.qscanbtn.setText('Quick Scan')
        self.qscanbtn.setIcon(QIcon(os.path.join(self.filepath, "quick.png")))
        self.qscanbtn.setFixedHeight(50)
        self.qscanbtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)

        self.cscanbtn = QtWidgets.QPushButton()
        self.cscanbtn.setCheckable(True)
        self.cscanbtn.setText('Comprehensive Scan')
        self.cscanbtn.setIcon(QIcon(os.path.join(self.filepath, "comprehen.png")))
        self.cscanbtn.setFixedHeight(50)
        self.cscanbtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)

        self.vscanbtn = QtWidgets.QPushButton()
        self.vscanbtn.setCheckable(True)
        self.vscanbtn.setText('Vulnerability Scan')
        self.vscanbtn.setIcon(QIcon(os.path.join(self.filepath, "vuln.png")))
        self.vscanbtn.setFixedHeight(50)
        self.vscanbtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)

        self.exit = QtWidgets.QPushButton()
        self.exit.setText('Exit')
        self.exit.setIcon(QIcon(os.path.join(self.filepath, "exit.png")))
        self.exit.setFixedHeight(50)
        self.exit.setStyleSheet(ScannerStyle.exbtnstylesheet)

        btngroup = QtWidgets.QButtonGroup(self)
        btngroup.setExclusive(True)
        btngroup.addButton(self.homebtn)
        self.homebtn.setChecked(True)

        btngroup.addButton(self.qscanbtn)
        btngroup.addButton(self.cscanbtn)
        btngroup.addButton(self.vscanbtn)

        grid.addWidget(box_container)
        grid.addWidget(self.homebtn, 1)
        grid.addWidget(self.hisbtn, 1)
        grid.addWidget(self.qscanbtn, 1)
        grid.addWidget(self.cscanbtn, 1)
        grid.addWidget(self.vscanbtn, 1)
        grid.addStretch(1)
        grid.addWidget(self.exit, 1)

    def hidden(self):

        if not self.isHide: 

            self.homebtn.setText("")
            self.hisbtn.setText("")
            self.qscanbtn.setText("")
            self.cscanbtn.setText("")
            self.vscanbtn.setText("")
            self.exit.setText("")

            self.homebtn.setStyleSheet(ScannerStyle.hiddenbtnstylesheet)
            self.hisbtn.setStyleSheet(ScannerStyle.hiddenbtnstylesheet)
            self.qscanbtn.setStyleSheet(ScannerStyle.hiddenbtnstylesheet)
            self.cscanbtn.setStyleSheet(ScannerStyle.hiddenbtnstylesheet)
            self.vscanbtn.setStyleSheet(ScannerStyle.hiddenbtnstylesheet)
            self.exit.setStyleSheet(ScannerStyle.hiddenexbtnstylesheet)

            self.note.hide()
            self.hidebtn.setIcon(QIcon(os.path.join(self.filepath, "list.png")))
            self.isHide = True

        else:

            self.homebtn.setText("Home")
            self.hisbtn.setText("History")
            self.qscanbtn.setText("Quick Scan")
            self.cscanbtn.setText("Comprehensive Scan")
            self.vscanbtn.setText("Vulnerability Scan")

            self.homebtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)
            self.hisbtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)
            self.qscanbtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)
            self.cscanbtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)
            self.vscanbtn.setStyleSheet(ScannerStyle.leftbtnstylesheet)
            self.exit.setStyleSheet(ScannerStyle.exbtnstylesheet)

            self.exit.setText("Exit")
            self.note.show()
            self.hidebtn.setIcon(QIcon(os.path.join(self.filepath, "list-exp.png")))
            self.isHide = False

