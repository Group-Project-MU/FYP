from PyQt6 import QtWidgets, QtCore
from datetime import datetime
from Widgets import ScannerStyle, Scanner, CustomScanner, function
import os, json

class History(QtWidgets.QWidget):

    def __init__(self, nmap_path=None, api_vulners=None, api_ai=None):

        super().__init__()
        self.nmap_path = nmap_path
        self.api_vulners = api_vulners
        self.api_ai = api_ai
        self.layout()
        self.all_history_records = []
        self.old_history_records = []
        self.latest_history_records = []
        self.qscan_history_records = []
        self.cscan_history_records = []
        self.vscan_history_records = []
        self.ascan_history_records = []
        self._orderbytype(self.hislist)
        self._orderbydate(self.hislist)
        self.bydate = True
        self.inputhis.textChanged.connect(self._searchhis)
        self.filter_list.currentTextChanged.connect(self._filter)
        self.opened_windows = []

    def get_key(self, api_type):

        with open('config.json', 'r', encoding="utf-8") as f:
            config = json.load(f)
            key = config[api_type]
            if key and key != None:
                return key
            else:
                return None
            
    def _showhis(self, filename):
        
        with open(filename, 'r') as f:
            content = json.load(f)

        if isinstance(content, list):
            content = content[0]

        nmap_command = content.get('nmap', {}).get('command_line', '')

        if "quick" in str(filename).lower():
            res = Scanner.Scan(nmap_path=self.nmap_path, api_vulners=self.api_vulners, api_ai=self.api_ai, name="History Review", placeholder=nmap_command, command="")
            res.setWindowTitle(f"History review: Quick Scan - {filename}")
            res.filepath = filename

        elif "comprehensive" in str(filename).lower():
            res = Scanner.Scan(nmap_path=self.nmap_path, api_vulners=self.api_vulners, api_ai=self.api_ai, name="History Review", placeholder=nmap_command)
            res.filepath = filename
            res._comprehensive()
            if hasattr(res, 'comprehensive_initialized') and res.comprehensive_initialized:
                res._update_comprehensive_result()

        elif "vulnerability" in str(filename).lower():
            res = Scanner.Scan(nmap_path=self.nmap_path, api_vulners=self.api_vulners, api_ai=self.api_ai, name="History Review", placeholder=nmap_command, command="")
            res.filepath = filename
            res._vuln()        
            if hasattr(res, 'vulnerability_initialized') and res.vulnerability_initialized:
                res._update_vuln_result()
                res._update_vuln_sol()

        elif "custom" in str(filename).lower():
            res = CustomScanner.CustScan(nmap_path=self.nmap_path, name="History Review", placeholder=nmap_command, command="")
            res.scriptbtn.setDisabled(True)
            res.scriptbtn.setStyleSheet("""background-color: rgba(0, 0, 0, 0)""")
            res.setWindowTitle(f"History review: Custom Scan - {filename}")
            res.filepath = filename
            res._custom()
            if hasattr(res, 'script_initialized') and res.script_initialized:
                res._update_script_result()
        
        else:
            function.error_msg(title="Error", msg="Cannot read this file!")
            return

        res.title2.setText(f"Result: {filename}")
        res.sresult.setPlainText(res._terminal_display(content))
        res.inputbtn.setDisabled(True)
        res.stopbtn.setDisabled(True)
        res.inputbtn.setStyleSheet("""background-color: rgba(0, 0, 0, 0)""")
        res.stopbtn.setStyleSheet("""background-color: rgba(0, 0, 0, 0)""")
        res.inputscan.setDisabled(True)
        res._update_result()
        res.show()
        self.opened_windows.append(res)
        res.destroyed.connect(lambda: self._distroyed_window(res))

    def _distroyed_window(self, window):

        if window in self.opened_windows:
            self.opened_windows.remove(window)

    def _searchhis(self):

        search_text = self.inputhis.text()
        search_text = search_text.lower().strip()

        for data in self.all_history_records:

            container = data['container']
            filename = data['filename']
            date = data['date_info']

            if (search_text in filename.lower() or search_text in date.lower()):

                container.setVisible(True)
            
            else:

                container.setVisible(False)

    def _filter(self):

        if self.filter_list.currentData() == "Date":
            self._orderbydate(self.hislist)
        elif self.filter_list.currentData() == "Type":
            self._orderbytype(self.hislist)

    def _orderbydate(self, grid):

        try:

            self.all_history_records, self.old_history_records, self.latest_history_records = [], [], []
            oldhistory = []
            latest = []

            if not hasattr(self, 'buttongroup'):
                self.buttongroup = QtWidgets.QButtonGroup()
            else:
                while grid.count():
                    item = grid.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                for button in self.buttongroup.buttons():
                    self.buttongroup.removeButton(button)

            result = _filecount()
            today = datetime.today()
            if result is not None:
                for i in result:
                        
                    filename = i.split('.json')[0]
                    filepath = os.path.join('History', i)

                    try:
                        mtime = os.path.getmtime(filepath)
                        date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                        filedate = datetime.fromtimestamp(mtime)  

                        if (today - filedate).days > 3:
                            oldhistory.append({
                                'file': i,
                                'filename': filename,
                                'filepath': filepath,
                                'date_info': date_str
                            })

                        else:
                            latest.append({
                                'file': i,
                                'filename': filename,
                                'filepath': filepath,
                                'date_info': date_str
                            })

                    except Exception as e:

                        oldhistory.append({
                            'file': i,
                            'filename': filename,
                            'filepath': filepath,
                            'date_info': "Unkonwn"
                        })

                if latest:

                    latestbtn = QtWidgets.QPushButton("Latest Record (Last 3 Days)")
                    latestbtn.setStyleSheet(ScannerStyle.showbtnstylesheet)
                    latestbtn.setMinimumSize(100, 30)
                    latestbtn.setCheckable(True)

                    latestcontainer = QtWidgets.QWidget()
                    latestlayout = QtWidgets.QVBoxLayout(latestcontainer)
                    latestlayout.setSpacing(5)
                    latestcontainer.setContentsMargins(-10, -10, -10, -10)

                    for i in latest:

                        filename = i['filename']
                        filepath = i['filepath']
                        date_str = i['date_info']

                        container = QtWidgets.QWidget()
                        container.setStyleSheet(ScannerStyle.btngroupstylesheet)
                        container_layout = QtWidgets.QVBoxLayout(container)
                        container_layout.setContentsMargins(5, 5, 5, 5)
                        
                        btnname = filename
                        resbtn = QtWidgets.QPushButton(btnname)
                        resbtn.setStyleSheet(ScannerStyle.hisbtnstylesheet)
                        resbtn.setFixedHeight(50)
                        
                        resbtn.clicked.connect(lambda checked=False, f=filepath: self._showhis(f))
                        
                        date_label = QtWidgets.QLabel(date_str)
                        date_label.setStyleSheet(ScannerStyle.datestylesheet)
                        date_label.setFixedHeight(20)
                        
                        container_layout.addWidget(resbtn)
                        container_layout.addWidget(date_label)
                        
                        self.buttongroup.addButton(resbtn)
                        latestlayout.addWidget(container)

                        self.latest_history_records.append({
                            'container' : container,
                            'filename' : filename,
                            'date_info' : date_str,
                            'btnname' : btnname,
                            'button' : resbtn
                            })
                        
                    grid.addWidget(latestbtn)
                    grid.addWidget(latestcontainer)
                    latestbtn.toggled.connect(lambda checked: latestcontainer.setVisible(not checked))
                    latestbtn.toggled.connect(lambda checked: latestbtn.setText("Show Latest Record" if checked else "Hide Latest Record"))

                if oldhistory:

                    oldbtn = QtWidgets.QPushButton("Old Record (More than 3 Days)")
                    oldbtn.setStyleSheet(ScannerStyle.showbtnstylesheet)
                    oldbtn.setMinimumSize(100, 30)
                    oldbtn.setCheckable(True)

                    oldcontainer = QtWidgets.QWidget()
                    oldlayout = QtWidgets.QVBoxLayout(oldcontainer)
                    oldlayout.setContentsMargins(0, 0, 0, 0)
                    oldlayout.setSpacing(5)

                    for i in oldhistory:

                        filename = i['filename']
                        filepath = i['filepath']
                        date_str = i['date_info']

                        container = QtWidgets.QWidget()
                        container.setStyleSheet(ScannerStyle.btngroupstylesheet)
                        container_layout = QtWidgets.QVBoxLayout(container)
                        container_layout.setContentsMargins(5, 5, 5, 5)
                        
                        btnname = filename
                        resbtn = QtWidgets.QPushButton(btnname)
                        resbtn.setStyleSheet(ScannerStyle.hisbtnstylesheet)
                        resbtn.setFixedHeight(50)
                        resbtn.clicked.connect(lambda checked=False, f=filepath: self._showhis(f))
                        
                        date_label = QtWidgets.QLabel(date_str)
                        date_label.setStyleSheet(ScannerStyle.datestylesheet)
                        date_label.setFixedHeight(20)
                        
                        container_layout.addWidget(resbtn)
                        container_layout.addWidget(date_label)
                        
                        self.buttongroup.addButton(resbtn)
                        oldlayout.addWidget(container)

                        self.old_history_records.append({
                            'container' : container,
                            'filename' : filename,
                            'date_info' : date_str,
                            'btnname' : btnname,
                            'button' : resbtn
                            })
                        
                    grid.addWidget(oldbtn)
                    grid.addWidget(oldcontainer)
                    oldbtn.toggled.connect(lambda checked: oldcontainer.setVisible(not checked))
                    oldbtn.toggled.connect(lambda checked: oldbtn.setText("Show Older Record" if checked else "Hide Older Record"))
                
                self.all_history_records = self.old_history_records + self.latest_history_records
                self.bydate = True

        except Exception as e:
            function.logging.error(f"Error in _orderbytype: {str(e)}")
            #import traceback
            #traceback.print_exc() 

    def _orderbytype(self, grid):

        try:
            qscan, cscan, vscan, ascan = [], [], [], []
            self.all_history_records = []
            self.qscan_history_records = []
            self.cscan_history_records = []
            self.vscan_history_records = []
            self.ascan_history_records = []

            if not hasattr(self, 'buttongroup'):
                self.buttongroup = QtWidgets.QButtonGroup()
            else:
                while grid.count():
                    item = grid.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                for button in self.buttongroup.buttons():
                    self.buttongroup.removeButton(button)

            result = _filecount()
            if result is not None:
                for i in result:
                        
                    filename = i.split('.json')[0]
                    filepath = os.path.join('History', i)
                    scantype = filename.split('_')[1]
                    
                    mtime = os.path.getmtime(filepath)
                    date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')

                    try:

                        if "Quick Scan" in str(scantype): 
                            qscan.append({
                                'file': i,
                                'filename': filename,
                                'filepath': filepath,
                                'date_info': date_str
                            })

                        elif "Comprehensive Scan" in str(scantype): 
                            cscan.append({
                                'file': i,
                                'filename': filename,
                                'filepath': filepath,
                                'date_info': date_str
                            })
                        
                        elif "Vulnerability Scan" in str(scantype): 
                            vscan.append({
                                'file': i,
                                'filename': filename,
                                'filepath': filepath,
                                'date_info': date_str
                            })

                        elif "Custom Scan" in str(scantype): 
                            ascan.append({
                                'file': i,
                                'filename': filename,
                                'filepath': filepath,
                                'date_info': date_str
                            })
                        
                        else:
                            continue

                    except Exception as e:
                        function.logging.error(msg=f"{str(e)}")

                if qscan:

                    qbtn = QtWidgets.QPushButton("Hide Quick Scan Record")
                    qbtn.setStyleSheet(ScannerStyle.showbtnstylesheet)
                    qbtn.setMinimumSize(100, 30)
                    qbtn.setCheckable(True)

                    qcontainer = QtWidgets.QWidget()
                    qlayout = QtWidgets.QVBoxLayout(qcontainer)
                    qlayout.setSpacing(5)
                    qcontainer.setContentsMargins(-10, -10, -10, -10)

                    for i in qscan:

                        filename = i['filename']
                        filepath = i['filepath']
                        date_str = i['date_info']

                        container = QtWidgets.QWidget()
                        container.setStyleSheet(ScannerStyle.btngroupstylesheet)
                        container_layout = QtWidgets.QVBoxLayout(container)
                        container_layout.setContentsMargins(5, 5, 5, 5)
                        
                        btnname = filename.split('_')[0]
                        resbtn = QtWidgets.QPushButton(btnname)
                        resbtn.setStyleSheet(ScannerStyle.hisbtnstylesheet)
                        resbtn.setFixedHeight(50)
                        resbtn.clicked.connect(lambda checked=False, f=filepath: self._showhis(f))
                        
                        date_label = QtWidgets.QLabel(date_str)
                        date_label.setStyleSheet(ScannerStyle.datestylesheet)
                        date_label.setFixedHeight(20)
                        
                        container_layout.addWidget(resbtn)
                        container_layout.addWidget(date_label)
                        
                        self.buttongroup.addButton(resbtn)
                        qlayout.addWidget(container)

                        self.qscan_history_records.append({
                            'container' : container,
                            'filename' : filename,
                            'date_info' : date_str,
                            'btnname' : btnname,
                            'button' : resbtn
                            })
                        
                    grid.addWidget(qbtn)
                    grid.addWidget(qcontainer)
                    qbtn.toggled.connect(lambda checked: qcontainer.setVisible(not checked))
                    qbtn.toggled.connect(lambda checked: qbtn.setText("Show Quick Scan Record" if checked else "Hide Quick Scan Record"))

                if cscan:

                    cbtn = QtWidgets.QPushButton("Hide Comprehensive Scan Record")
                    cbtn.setStyleSheet(ScannerStyle.showbtnstylesheet)
                    cbtn.setMinimumSize(100, 30)
                    cbtn.setCheckable(True)

                    ccontainer = QtWidgets.QWidget()
                    clayout = QtWidgets.QVBoxLayout(ccontainer)
                    clayout.setContentsMargins(0, 0, 0, 0)
                    clayout.setSpacing(5)

                    for i in cscan:

                        filename = i['filename']
                        filepath = i['filepath']
                        date_str = i['date_info']

                        container = QtWidgets.QWidget()
                        container.setStyleSheet(ScannerStyle.btngroupstylesheet)
                        container_layout = QtWidgets.QVBoxLayout(container)
                        container_layout.setContentsMargins(5, 5, 5, 5)
                        
                        btnname = filename.split('_')[0]
                        resbtn = QtWidgets.QPushButton(btnname)
                        resbtn.setStyleSheet(ScannerStyle.hisbtnstylesheet)
                        resbtn.setFixedHeight(50)
                        resbtn.clicked.connect(lambda checked=False, f=filepath: self._showhis(f))
                        
                        date_label = QtWidgets.QLabel(date_str)
                        date_label.setStyleSheet(ScannerStyle.datestylesheet)
                        date_label.setFixedHeight(20)
                        
                        container_layout.addWidget(resbtn)
                        container_layout.addWidget(date_label)
                        
                        self.buttongroup.addButton(resbtn)
                        clayout.addWidget(container)

                        self.cscan_history_records.append({
                            'container' : container,
                            'filename' : filename,
                            'date_info' : date_str,
                            'btnname' : btnname,
                            'button' : resbtn
                            })
                        
                    grid.addWidget(cbtn)
                    grid.addWidget(ccontainer)
                    cbtn.toggled.connect(lambda checked: ccontainer.setVisible(not checked))
                    cbtn.toggled.connect(lambda checked: cbtn.setText("Show Comprehensive Scan Record" if checked else "Hide Comprehensive Scan Record"))
                
                if vscan:

                    vbtn = QtWidgets.QPushButton("Hide Vulnerability Scan Record")
                    vbtn.setStyleSheet(ScannerStyle.showbtnstylesheet)
                    vbtn.setMinimumSize(100, 30)
                    vbtn.setCheckable(True)

                    vcontainer = QtWidgets.QWidget()
                    vlayout = QtWidgets.QVBoxLayout(vcontainer)
                    vlayout.setContentsMargins(0, 0, 0, 0)
                    vlayout.setSpacing(5)

                    for i in vscan:

                        filename = i['filename']
                        filepath = i['filepath']
                        date_str = i['date_info']

                        container = QtWidgets.QWidget()
                        container.setStyleSheet(ScannerStyle.btngroupstylesheet)
                        container_layout = QtWidgets.QVBoxLayout(container)
                        container_layout.setContentsMargins(5, 5, 5, 5)
                        
                        btnname = filename.split('_')[0]
                        resbtn = QtWidgets.QPushButton(btnname)
                        resbtn.setStyleSheet(ScannerStyle.hisbtnstylesheet)
                        resbtn.setFixedHeight(50)
                        resbtn.clicked.connect(lambda checked=False, f=filepath: self._showhis(f))
                        

                        date_label = QtWidgets.QLabel(date_str)
                        date_label.setStyleSheet(ScannerStyle.datestylesheet)
                        date_label.setFixedHeight(20)
                        
                        container_layout.addWidget(resbtn)
                        container_layout.addWidget(date_label)
                        
                        self.buttongroup.addButton(resbtn)
                        vlayout.addWidget(container)

                        self.vscan_history_records.append({
                            'container' : container,
                            'filename' : filename,
                            'date_info' : date_str,
                            'btnname' : btnname,
                            'button' : resbtn
                            })

                    grid.addWidget(vbtn)
                    grid.addWidget(vcontainer)
                    vbtn.toggled.connect(lambda checked: vcontainer.setVisible(not checked))
                    vbtn.toggled.connect(lambda checked: vbtn.setText("Show Vulnerability Scan Record" if checked else "Hide Vulnerability Scan Record"))

                if ascan:

                    abtn = QtWidgets.QPushButton("Hide Custom Scan Record")
                    abtn.setStyleSheet(ScannerStyle.showbtnstylesheet)
                    abtn.setMinimumSize(100, 30)
                    abtn.setCheckable(True)

                    acontainer = QtWidgets.QWidget()
                    alayout = QtWidgets.QVBoxLayout(acontainer)
                    alayout.setContentsMargins(0, 0, 0, 0)
                    alayout.setSpacing(5)

                    for i in ascan:

                        filename = i['filename']
                        filepath = i['filepath']
                        date_str = i['date_info']

                        container = QtWidgets.QWidget()
                        container.setStyleSheet(ScannerStyle.btngroupstylesheet)
                        container_layout = QtWidgets.QVBoxLayout(container)
                        container_layout.setContentsMargins(5, 5, 5, 5)
                        
                        btnname = filename.split('_')[0]
                        resbtn = QtWidgets.QPushButton(btnname)
                        resbtn.setStyleSheet(ScannerStyle.hisbtnstylesheet)
                        resbtn.setFixedHeight(50)
                        resbtn.clicked.connect(lambda checked=False, f=filepath: self._showhis(f))
                        
                        date_label = QtWidgets.QLabel(date_str)
                        date_label.setStyleSheet(ScannerStyle.datestylesheet)
                        date_label.setFixedHeight(20)
                        
                        container_layout.addWidget(resbtn)
                        container_layout.addWidget(date_label)
                        
                        self.buttongroup.addButton(resbtn)
                        alayout.addWidget(container)

                        self.ascan_history_records.append({
                            'container' : container,
                            'filename' : filename,
                            'date_info' : date_str,
                            'btnname' : btnname,
                            'button' : resbtn
                            })
                    
                    grid.addWidget(abtn)
                    grid.addWidget(acontainer)
                    abtn.toggled.connect(lambda checked: acontainer.setVisible(not checked))
                    abtn.toggled.connect(lambda checked: abtn.setText("Show Custom Scan Record" if checked else "Hide Custom Scan Record"))

                self.all_history_records = self.qscan_history_records + self.cscan_history_records + self.vscan_history_records + self.ascan_history_records
                self.bydate = False

        except Exception as e:
            function.logging.error(f"Error in _orderbytype: {str(e)}")
            #import traceback
            #traceback.print_exc() 

    def layout(self):

        self.hisgrid = QtWidgets.QVBoxLayout(self)
        self.hisgrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollarea2 = QtWidgets.QScrollArea()
        self.scrollarea2.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.scrollarea2.setWidgetResizable(True)
        self.scrollarea2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollarea2.setStyleSheet(ScannerStyle.hisscrollstylesheet)

        self.hislistbtn = QtWidgets.QWidget()
        self.hislist = QtWidgets.QVBoxLayout(self.hislistbtn)
        self.hislistbtn.setStyleSheet("""border: 0px solid #0000FF;""")
        self.hislist.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.hislist.setContentsMargins(10, 10, 10, 10)
        self.scrollarea2.setWidget(self.hislistbtn)

        title3 = QtWidgets.QLabel()
        title3.setStyleSheet(ScannerStyle.hislabelstylesheet)
        title3.setText('History')
        title3.setFixedHeight(30)

        self.inputhis = QtWidgets.QLineEdit(self)
        self.inputhis.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.inputhis.setPlaceholderText('For searching history')
        self.inputhis.setStyleSheet('border: 2px solid #6488EA; border-radius: 8px; padding-left: 5px;')
        self.inputhis.setFixedHeight(30)
        self.inputhis.setMinimumWidth(90)

        self.filter_list = QtWidgets.QComboBox()
        self.filter_list.setStyleSheet(ScannerStyle.combo_all)
        self.filter_list.addItem("Order By Date", "Date")
        self.filter_list.addItem("Order By Scanning Methods", "Type")

        self.hisgrid.addWidget(title3)
        self.hisgrid.addWidget(self.inputhis)
        self.hisgrid.addWidget(self.filter_list)
        self.hisgrid.addWidget(self.scrollarea2)
        
def _filecount():
    try:
        total = os.listdir('History')
        total.sort(key=lambda f: os.path.getmtime(os.path.join('History',f)), reverse=True)
        files = []
        for i in total:
            if i.endswith('.json'):
                files.append(i)
        if len(files) > 0:
            return files
        else:
            return None
    except FileNotFoundError:
        pass
