from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QMessageBox
import os
from Widgets import ScannerStyle

class HelpDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Guide - Advanced Network Scanner")
        self.setStyleSheet("""background: #F5F9FF;""")
        self.setMinimumSize(800, 600)
        self.stocontent = []
        self.page = 0
        self.read_content()
        self.layout()
        self.valid_btns("0")
        self.valid_btns("1")

    def layout(self):

        layout = QtWidgets.QVBoxLayout(self)
        hcontainer = QtWidgets.QWidget()
        hlayout = QtWidgets.QHBoxLayout(hcontainer)

        self.text = QtWidgets.QTextEdit()
        self.text.setStyleSheet(ScannerStyle.help_text)
        self.text.setReadOnly(True)
        self.text.setHtml(self.style + self.stocontent[self.page])
        layout.addWidget(self.text)
        
        self.closebtn = QtWidgets.QPushButton("Close")
        self.closebtn.setStyleSheet(ScannerStyle.btncstylesheet)
        self.nextbtn = QtWidgets.QPushButton("Next")
        self.nextbtn.setStyleSheet(ScannerStyle.btnestylesheet)
        self.backbtn = QtWidgets.QPushButton("Back")
        self.backbtn.setStyleSheet(ScannerStyle.btnestylesheet)
       
        hlayout.addWidget(self.backbtn)
        hlayout.addWidget(self.closebtn)
        hlayout.addWidget(self.nextbtn)
        layout.addWidget(hcontainer)

        self.closebtn.clicked.connect(self.close)
        self.nextbtn.clicked.connect(lambda: self.valid_btns("1"))
        self.backbtn.clicked.connect(lambda: self.valid_btns("0"))
    
    def read_content(self):

        doc_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "Document"))
        help_path = os.path.join(doc_dir, "Help.txt")
        with open(help_path, 'r', encoding="utf-8") as f:
            content = f.read()

        self.style = ""
        style_start = content.find("<style>")
        style_end = content.find("</style>")
        if style_start != -1 and style_end != -1:
            self.style = content[style_start:style_end + len("</style>")]

        content = content.split("<h1>") 
        for addcontent in content:
            if addcontent != '' and "<style>" not in addcontent:
                add = f"<h1>{addcontent}"
                self.stocontent.append(add) 
                

    def valid_btns(self, btn=""):

        if self.page <= 0:
            self.backbtn.setDisabled(True)
            self.nextbtn.setDisabled(False)
            
        elif self.page >= len(self.stocontent)-1:
            self.nextbtn.setDisabled(True)
            self.backbtn.setDisabled(False)
            
        else:
            self.backbtn.setDisabled(False)
            self.nextbtn.setDisabled(False)

        if btn == "1":
            self.page += 1
            self.text.setHtml(self.style + self.stocontent[self.page])
            return self.valid_btns()
        elif btn == "0":
            self.page -= 1
            self.text.setHtml(self.style + self.stocontent[self.page]) 
            return self.valid_btns()


