import ipaddress, socket, os, logging, json, sys
from openai import OpenAI
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QProcess
from PyQt6 import QtCore
from Widgets import ScannerStyle

FORMAT = f'%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='scanner_log.log', filemode='a', format=FORMAT)
def error_msg(title='', msg=''):

    warn = QtWidgets.QMessageBox(parent=None)
    warn.setIcon(QtWidgets.QMessageBox.Icon.NoIcon)
    warn.setStyleSheet(ScannerStyle.error_msg)
    warn.setWindowTitle(title)
    warn.setText(msg)

    label = warn.findChild(QtWidgets.QLabel, "qt_msgbox_label")
    if label:
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    button = warn.findChild(QtWidgets.QDialogButtonBox)
    if button:
        button.setCenterButtons(True)
    warn.exec()
    
def chatbot(api, model_opt="nvidia/nemotron-3-nano-30b-a3b:free", content="", role="You are a professional security auditor who has worked over 30 years in this field. You have to provide solutions to help the user to solve the network security issues."):


    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api
    )

    completion = client.chat.completions.create(
        model= model_opt,
        messages=[
            {"role" : "system", "content" : role},
            {"role" : "user", "content" : content}
        ]
    )

    return completion.choices[0].message.content
def filecount():
    try:
        total = os.listdir('History')
        total.sort(key=lambda f: os.path.getmtime(os.path.join('History',f)), reverse=True)
        files = []
        for i in total:
            if i.endswith('.json'):
                files.append(i)
        return files
    except FileNotFoundError:
        pass

def storehistory(result, filename):
    try:
        dir = 'History'      
        os.mkdir(dir)
        with open(filename, 'x') as f:
            json.dump(result, f)    
        
        return filename
    
    except FileExistsError:
        
        newfile = filename.split('/')[-1]
        newfile = newfile.split('.json')[0]
        repeated = 0
        final = f"{dir}/{newfile}.json"

        while os.path.exists(final):
            repeated += 1
            final = f"{dir}/{newfile}-{repeated}.json"

        with open(final, 'x') as f:
            json.dump(result, f, indent=4) 

        return final
    
def valid_ip(ip):
    try:
        ipaddr = ip.split('.')
        if int(ipaddr[-1]) > 0 and int(ipaddr[-1]) < 255:
            if ipaddress.ip_address(ip):
                return True
        else:
            return False
            
    except Exception:
        return False

def valid_web(ip): 
    try:
        if ip[0].isdigit() != True:
            check_web = socket.gethostbyname(ip)
        if check_web:
            return True
        
    except socket.gaierror:
        return False
    except Exception:
        return False

def valid_range(ip):
    try:
        ip1, ip2 = ip.split('-')
        parseip = ip1.split('.')
        if int(parseip[-1]) != int(ip2):
            if ( 1 <= int(parseip[-1]) <= 253) and ( 2 <= int(ip2) <= 254):
                return valid_ip(ip1)
            else:
                return False
    except Exception:
        return False
    
def error_handle(ip):
    try:
        cond1 = valid_ip(ip)
        cond2 = valid_web(ip)
        cond3 = valid_range(ip)
        
        if cond1 or cond2 or cond3:
            return True
        else:
            return False
    
    except Exception as e:
        logging.error(f'{str(e)}')
        return False

def restart():
    
    app = QApplication.instance()
    if not QProcess.startDetached(sys.executable, sys.argv):
        QMessageBox.warning(
            None,
            "Restart",
            "Could not restart the application. Please close and open it manually.",
        )
        QMessageBox.setStyleSheet(ScannerStyle.error_msg)
        return
    if app is not None:
        app.quit()

class collapse_section(QtWidgets.QGroupBox):

    def __init__(self, title:str, start_open:bool, parent=None):
        super().__init__(parent)
        self.content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        self.content.setStyleSheet("""
                                    background: #F5F9FF;
                                    border-radius: 8px;
                                """)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(5)

        self._toggle = QtWidgets.QToolButton()
        self._toggle.setMinimumSize(35, 35)
        self._toggle.setStyleSheet(ScannerStyle.toolbtnstylesheet)
        self._toggle.setCheckable(True)
        self._toggle.setChecked(start_open)
        self._toggle.setArrowType(QtCore.Qt.ArrowType.DownArrow if start_open else QtCore.Qt.ArrowType.RightArrow)
        self._title = QtWidgets.QLabel(title)
        self._title.setMinimumHeight(40)
        self._title_style(start_open)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(self._toggle)
        header.addWidget(self._title)

        body = QtWidgets.QVBoxLayout(self)
        body.addLayout(header)
        body.addWidget(self.content)

        self.content.setVisible(start_open)
        self._toggle.toggled.connect(self._toggled)

    def _toggled(self, display: bool):
        self.content.setVisible(display)
        self._title_style(display)
        self._toggle.setArrowType(QtCore.Qt.ArrowType.DownArrow if display else QtCore.Qt.ArrowType.RightArrow)
    
    def _title_style(self, toggled:bool):
        if toggled:
            self._title.setStyleSheet("""
                                font-size: 16px;
                                font: bold;
                                text-align: left;
                                color: #FFFFFF;
                                background: #6488EA;
                                border: 0px solid #000000;
                                border-radius: 8px;
                                padding: 10px;
                            """)
        else:
            self._title.setStyleSheet("""
                            font-size: 16px;
                            font: bold;
                            text-align: left;
                            color: #FFFFFF;
                            background: #8FC9FF;
                            border: 0px solid #000000;
                            border-radius: 8px;
                            padding: 10px;
                        """)

    def _add_widget(self, widget):
        self.content_layout.addWidget(widget)
    
    def _add_layout(self, layout):
        self.content_layout.addLayout(layout)