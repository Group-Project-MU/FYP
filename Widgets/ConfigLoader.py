from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialog
from PyQt6 import QtCore
from Widgets import ScannerStyle, function
import json
import sys
import os

_init_launch = None

class nmaploader(QMainWindow):
    
    def readpath(self):

        select = QFileDialog()
        select.setNameFilter("(*.exe)")
        select.setFileMode(QFileDialog.FileMode.ExistingFile)
        select.exec()

        return select.selectedFiles()
    
class nmapscriptloader(QMainWindow):

    def readpath(self):

        select = QFileDialog()
        select.setFileMode(QFileDialog.FileMode.Directory)
        select.exec()

        return select.selectedFiles()

class apiloader(QDialog):

    def __init__(self, parent=None, title="Vulners API Key"):
        super().__init__(parent)
        self.title = title
        self.setWindowTitle(self.title)
        self.vulners_api, self.openroute_api = self.load_demo()
        self.setStyleSheet("""background: #F5F9FF;text-align: left;font-size: 16px;font: bold;""")
        self.setMinimumSize(800, 100)
        self.api_key = None
        self._layout()

    def _layout(self):

        layout = QVBoxLayout(self)
        title = QLabel(self.title)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        layout.addWidget(title)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Please enter your API key if you already have one.")
        self.defaultbtn = QPushButton("Demo Vulners Key")
        self.defaultbtn.setStyleSheet("""background: #6488EA;color: #FFFFFF;font-size: 16px;font: bold;text-align: center;border-radius: 8px;""")
        self.defaultbtn.clicked.connect(lambda: self.input_field.setText(str(self.vulners_api)))
        self.default2btn = QPushButton("Demo OpenRouter Key")
        self.default2btn.setStyleSheet("""background: #6488EA;color: #FFFFFF;font-size: 16px;font: bold;text-align: center;border-radius: 8px;""")
        self.default2btn.clicked.connect(lambda: self.input_field.setText(str(self.openroute_api)))

        layout.addWidget(self.input_field)

        button_layout = QHBoxLayout()
        self.okbtn = QPushButton("OK")
        self.okbtn.setStyleSheet(ScannerStyle.btnestylesheet)
        self.okbtn.clicked.connect(self.accept)
        self.cancelbtn = QPushButton("Cancel")
        self.cancelbtn.setStyleSheet(ScannerStyle.btncstylesheet)
        self.cancelbtn.clicked.connect(self.reject)
        button_layout.addWidget(self.defaultbtn)
        button_layout.addWidget(self.default2btn)
        button_layout.addWidget(self.okbtn)
        button_layout.addWidget(self.cancelbtn)
        layout.addLayout(button_layout)

    def accept(self):

            key = self.input_field.text().strip()
            if key:
                self.api_key = key
                super().accept()
            else:
                function.error_msg("Warning", "API key cannot be empty.")
                return
    
    def load_demo(self):
        with open('demo_keys.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
            vulners_api = data['vulners_api']
            openroute_api = data['openroute_api']
        return vulners_api, openroute_api

def get_app():

    global _init_launch
    app = QApplication.instance()
    if app is None:
        _init_launch = QApplication(sys.argv)
        app = _init_launch
    return app

def getapi(api_type='vulners_api', critical=True):

    while True:
        try:
            with open('config.json', 'r', encoding="utf-8") as f:
                config = json.load(f)
            key = config[api_type]
            if key and key != None:
                return key
            elif critical == True:
                enterapi(msg='Please enter a valid key.')
            else:
                return None
        except KeyError:
            if critical:
                enterapi(msg='Please enter a valid key.')
            else:
                return None
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            enterapi(msg='Please enter your key.', api_type=api_type)
            return False

def enterapi(parent = None, msg='', api_type='vulners_api'):

    app = get_app() 

    if msg:

        warn = QMessageBox(parent)
        warn.setWindowTitle("Warning")
        warn.setText(msg)
        warn.setStyleSheet(ScannerStyle.error_msg)
        warn.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        exitbtn = warn.exec() 

        if exitbtn == QMessageBox.StandardButton.Cancel:
            sys.exit()

    dialog = apiloader(parent=parent, title=api_type)
    if dialog.exec() == QDialog.DialogCode.Accepted and dialog.api_key:
        _update_data(api_type, dialog.api_key)
        return True
    else:
        return False

def getnmap():

    while True:
        try:
            with open('config.json', 'r', encoding="utf-8") as f:
                path = json.load(f)
            valid = path['path']
            filename = os.path.basename(valid)
            if 'nmap.exe' in filename:
                return valid
            else:
                selectnmap(msg='Please select a valid path!')
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            selectnmap(msg='Please select the Nmap.exe path first.')
    
def selectnmap(warning = 'Warning', msg ='error message'):

    app = get_app() 
    
    if warning != None:
        warn = QMessageBox()
        warn.setWindowTitle(warning)
        warn.setText(msg)
        warn.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        warn.setStyleSheet(ScannerStyle.error_msg)

        exitbtn = warn.exec() 

        if exitbtn == QMessageBox.StandardButton.Cancel:
            sys.exit()

    display = nmaploader()
    path = display.readpath()
    
    if path and len(path) > 0:
        _update_data('path', path[0])
    
def getscript():

    while True:
        try:
            with open('config.json', 'r', encoding="utf-8") as f:
                data = json.load(f)
            folder = data['script']
            if os.path.isdir(folder):
                return folder 
            else:
                selectscriptfolder(msg='Please choose a valid script folder.')
        except (FileNotFoundError, KeyError):
            selectscriptfolder(msg='Please select the Nmap script folder first.')
    
def selectscriptfolder(warning = 'Warning', msg ='error message'):

    window = QApplication.instance()
    if window == None:
        window = QApplication(sys.argv)
    
    if warning != None:
        warn = QMessageBox()
        warn.setWindowTitle(warning)
        warn.setText(msg)
        warn.setStandardButtons(QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel) 
        warn.setStyleSheet(ScannerStyle.error_msg)
        warn.exec()

    display = nmapscriptloader()
    path = display.readpath()
    
    if path and len(path) > 0:
        _update_data('script', path[0])
    
    else:
        sys.exit("No folder selected!")
   
def _update_data(key, value):

    data = {}
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                data = {}
                function.logging.error(f"Error occur when loading the config.json. {str(e)}")
    data[key] = value
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def show_onboarding():

    try:
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return True
    return data.get("onboarding_done") is not True


def onboarding_done():
    _update_data("onboarding_done", True)

def config_loader(main_window=None):

    try:
        load_nmap = getnmap()
        load_api_vulner = getapi(api_type='vulners_api', critical=True)
        load_api_ai = getapi(api_type='openroute_api', critical=False)
        api_vulner = load_api_vulner
        api_ai = load_api_ai

        return load_nmap, api_vulner, api_ai
    
    except Exception as e:
        
        from Widgets import log
        function.logging.error(f'{e}')
        return False, False, False
    


