import nmap, json, csv, os, re
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QDesktopServices
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from Widgets import function, ScannerStyle

class Worker(QThread):

    finished = pyqtSignal(object)
    
    def __init__(self, fn, ip, command):

        super().__init__()
        self.fn = fn
        self.ip = ip
        self.command = command
    
    def run(self):

        try:
            result = self.fn(self.ip, self.command)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(None)
            function.logging.error(f'{e}')
    
    def stop(self):
        if self.isRunning():
            self.terminate()
            self.wait()

class VulnWorker(QThread):

    finished = pyqtSignal(object, object, object)

    def __init__(self, api_vulner, query, section , loading):
        super().__init__()
        self.api= api_vulner
        self.query = query
        self.section = section
        self.loading = loading
    
    def run(self):

        try:
            import vulners
            vulners_api = vulners.VulnersApi(api_key=self.api)
            result =None            

            if self.query:
                result = vulners_api.search.search_bulletins_all(
                    self.query,
                    limit=1, 
                    fields=["published", "title", "description", "cvelist", "cvss", "type"]
                )
            
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
                elif not isinstance(result, dict):
                    result = None

            self.finished.emit(result, self.section, self.loading)

        except Exception as e:
            function.logging.error(f"Error fetching vulnerability data from database: {str(e)}")
            self.finished.emit(None, self.section, self.loading)

class ChatWorker(QThread):

    finished = pyqtSignal(object)

    def __init__(self, target, prompt, api_ai):
        super().__init__()
        self.target = target
        self.prompt = prompt
        self.api = api_ai

    def run(self):
        from Widgets.function import chatbot
        result = chatbot(self.api,content=self.prompt)
        self.finished.emit(result)



class DebugWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, target_ip, nmap_path, ports=None, scripts=None, custom_cmd=None):
        super().__init__()
        self.nmap_path = nmap_path
        self.target_ip = target_ip
        self.ports = ports
        self.scripts = scripts
        self.custom_cmd = custom_cmd 
        self.process = None

    def run(self):
        try:

            if self.custom_cmd:
                
                final_cmd = self.custom_cmd.replace("nmap", f'"{self.nmap_path}"')

                import subprocess
                self.process = subprocess.Popen(
                    final_cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    shell=True, 
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                output, _ = self.process.communicate()
                self.finished.emit(output)
            
            else:

                import nmap
                nm = nmap.PortScanner(nmap_search_path=('nmap', self.nmap_path))
                
                arg_list = ["-sV", "-d"]
                if self.ports:
                    arg_list.append(f"-p {self.ports}")
                if self.scripts:
                    arg_list.append(f"--script {self.scripts}")
                else:
                    arg_list.append("--script vuln")
                
                full_args = " ".join(arg_list)
                nm.scan(hosts=self.target_ip, arguments=full_args)
                
                self.finished.emit(nm.scanstats().get('uphosts', '0') + " host up.\n" + nm.csv())
                
        except Exception as e:
            error_msg = f"Debug scan failed: {str(e)}"
            self.failed.appendPlainText(error_msg) if hasattr(self.failed, 'appendPlainText') else self.failed.emit(error_msg)
            function.logging.error(error_msg)

    def stop(self):
        if self.process:

            if os.name == 'nt':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else:
                import signal
                self.process.terminate()
                self.process.kill()

class Scan(QtWidgets.QWidget):

    progress_signal = QtCore.pyqtSignal(object)
    
    def __init__(self, nmap_path=None, api_vulners=None, api_ai=None, name="", placeholder="", command="", title=None):

        super().__init__()
        self.windowTitle = title
        self.nmap_path = nmap_path
        self.api_vulners = api_vulners
        self.api_ai = api_ai
        self.name = name
        self.placeholder = placeholder
        self.command = command
        self.progress_signal.connect(self._update_result)
        self.worker = None  
        self.vuln_worker_queue = []
        self.filepath = None
        self._progress()
        self.layout()

    def _clear_thread(self):

        if hasattr(self, 'vuln_worker_queue'):
            for worker in self.vuln_worker_queue:
                try:
                    worker.finished.disconnect()
                except:
                    pass
            self.vuln_worker_queue.clear()
        
        if self.worker and self.worker.isRunning():
            try:
                self.worker.finished.disconnect()
            except:
                pass

        import subprocess
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/IM", "nmap.exe"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            pass

        if hasattr(self, 'progressbar') and self.progressbar.isVisible():
            self.progressbar.hide()

    def _stop_button(self):
        
        if (self.worker and self.worker.isRunning()) or (hasattr(self, 'vuln_worker_queue') and len(self.vuln_worker_queue) > 0):
            self.sresult.setPlainText("Scan terminated")
            self._clear_thread()
        else:
            self.sresult.setPlainText("No scan in progress")

    def _runscan(self, command="-Pn -sn"):
        
        ip = self.inputscan.text()
        try:
            
            if function.error_handle(ip):
                if os.path.exists(self.nmap_path):
                    self._clear_thread()
                    self.progressbar.show()
                    self.worker = Worker(self._nmapscan, ip, command)
                    self.worker.finished.connect(self._scan_finished)
                    self.worker.start()
                else:
                    self.sresult.setPlainText(f"Invalid path!")
                    function.error_msg("Error", msg='Invalid path for Nmap.exe!')
                    function.logging.error(f"Invalid path: Nmap program was not found in path.")
            else:
                self.sresult.setPlainText(f"Invalid input!")
                function.error_msg("Error", msg='Invalid input!')
                function.logging.error(f"Invalid input: {ip}")

        except nmap.PortScannerError as e:
            function.logging.error(f"{e}")
        
    def _update_vuln_info(self, result, section, loading):

        if loading and loading.parent():
            loading.setParent(None)
            loading.deleteLater()

        if result and isinstance(result, dict):
            try:
                output = self._create_grid(result)
                section._add_widget(output)
            except Exception as e:
                function.logging.error(f"Error creating vulnerability grid: {str(e)}")
                error_label = QtWidgets.QLabel("Error displaying vulnerability information")
                error_label.setWordWrap(True)
                error_label.setStyleSheet("font-size: 14px; color: #E74C3C;")
                section._add_widget(error_label)
        else:
            nodata = QtWidgets.QLabel("No vulnerability data available")
            nodata.setWordWrap(True)
            nodata.setStyleSheet("font-size: 12px; color: #666;")
            section._add_widget(nodata)
    
    def _nmapscan(self, ip, command):

        nm = nmap.PortScanner(nmap_search_path=('nmap', self.nmap_path))
        scan_result = nm.scan(hosts=ip, arguments=command)
        fname = f"History/{ip}_{self.name}.json"
        self.filepath = function.storehistory(scan_result, fname)
        return scan_result


    def _scan_finished(self, scan_result):

        if scan_result:
            self.progressbar.hide()
            self.progress_signal.emit(scan_result) 

    def _update_result(self):

        with open(self.filepath, 'r') as f:
        
            content = json.load(f)

        if isinstance(content, list):
            content = content[0]

        uphosts = set()
        downhosts = content.get('nmap', {}).get('scanstats', {}).get('downhosts', '')
        openports = 0
        portnum = set()
        services = set()

        for host in content.get('scan', {}).values():

            if host.get('status', {}).get('state') == 'up':
                hostip = host.get('addresses', {}).get('ipv4')
                uphosts.add(hostip)
                        
            if "tcp" in host or "udp" in host:

                for port, ports in host.get('tcp', {}).items():
                    
                    portnum.add(port)
                    if ports.get('state') == 'open':
                        openports += 1
                    if ports.get('name') != '' and ports.get('name') != 'unknow':
                        services.add(ports.get('name'))

                for port, ports in host.get('udp', {}).items():
                    
                    portnum.add(port)
                    if ports.get('state') == 'open':
                        openports += 1
                    if ports.get('name') != '' and ports.get('name') != 'unknow':
                        services.add(ports.get('name'))

        self._update_card(self.ttluphosts, len(uphosts))
        self._update_card(self.ttldownhosts, downhosts)
        self._update_card(self.opports, openports)
        self._update_card(self.services, len(services))

        self.sresult.setPlainText(self._terminal_display(content))

        protocols = ['tcp', 'udp']
        port_table = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "Document", "Ports-Table.json")
        )
        with open(port_table, 'r') as f:
            port_info = json.load(f)
        try:
            self.model.removeRows(0, self.model.rowCount())
            for host, hostinfo in content.get('scan', {}).items():

                hostname = QStandardItem(host)
                for i in protocols:
                    if hostinfo.get(i):
                        for tcp, port_meta in hostinfo[i].items():

                            port_key = str(tcp)
                            fallback_key = "49152"
                            ports_table = None

                            if port_key in port_info:
                                ports_table = port_info.get(port_key)
                            else:
                                try:
                                    if int(tcp) >= 49152 and fallback_key in port_info:
                                        ports_table = port_info.get(fallback_key)
                                except Exception:
                                    ports_table = None

                            if isinstance(ports_table, dict):
                                name_text = ports_table.get("name", "Undefined")
                                desc_text = ports_table.get("description", "Undefined")
                                level_text = ports_table.get("risk_level", "Unknown")
                                name = QStandardItem(str(name_text))
                                level = QStandardItem(str(level_text))
                            else:
                                name = QStandardItem("Undefined")
                                level = QStandardItem("Unknown")
                                desc_text = "Undefined"

                            space = QStandardItem('')
                            protocol = QStandardItem(str(i))
                            port = QStandardItem(str(tcp))
                            state = QStandardItem(port_meta.get('state', ''))
                            service = QStandardItem(port_meta.get('name', ''))
                            version = QStandardItem(port_meta.get('version', '')) if port_meta.get('version') else QStandardItem('None')
                            extrainfo = QStandardItem(port_meta.get('extrainfo', '')) if port_meta.get('extrainfo') else QStandardItem('None')
                            
                            cols = [protocol, port, state, name, service, version, extrainfo, level]
                            if desc_text:
                                tooltip = f"Description: {desc_text}"
                                for item in cols:
                                    item.setToolTip(tooltip)
                            hostname.appendRow([space, protocol, port, state, name, service, version, extrainfo, level])

                        self.model.appendRow([hostname])

            self.tree.setModel(self.model)


        except Exception as e:
            function.logging.error(f"Error creating tree view: {str(e)}")

    def layout(self):

        self.layoutcon = QtWidgets.QGridLayout(self)
        self.layoutcon.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layoutcon.setContentsMargins(10, 10, 10, 10)
        
        self.title1 = QtWidgets.QLabel(self)
        self.title1.setStyleSheet(ScannerStyle.scannernamestylesheet)
        self.title1.setFixedHeight(30)
        self.title1.setText(self.name)

        self.inputscan = QtWidgets.QLineEdit(self)
        self.inputscan.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.inputscan.setPlaceholderText(self.placeholder)
        self.inputscan.setStyleSheet(ScannerStyle.fieldstylesheet)
        self.inputscan.setFixedHeight(30)
        self.inputscan.returnPressed.connect(lambda: self._runscan(self.command))
                                             
        self.inputbtn = QtWidgets.QPushButton(self)
        self.inputbtn.setText('Start Scan')
        self.inputbtn.setStyleSheet(ScannerStyle.scanbtnstylesheet)
        self.inputbtn.setMinimumSize(75, 40)
        self.stopbtn = QtWidgets.QPushButton(self)
        self.stopbtn.setText('Stop Scan')
        self.stopbtn.setStyleSheet(ScannerStyle.stopbtnstylesheet)
        self.stopbtn.setMinimumSize(75, 40)
        self.inputbtn.clicked.connect(lambda: self._runscan(self.command))
        self.stopbtn.clicked.connect(self._stop_button)
        self.chcolmod = QtWidgets.QPushButton(self)
        self.chcolmod.setText('Current Mode: Interactive')
        self.chcolmod.setStyleSheet(ScannerStyle.resbtnstylesheet)
        self.chcolmod.setMinimumSize(75, 40)
        self.chcolmod.clicked.connect(self._change_col_mode)

        self.title2 = QtWidgets.QLabel(self)
        self.title2.setStyleSheet(ScannerStyle.scannertitlestylesheet)
        self.title2.setText('Result: ')
        self.title2.setFixedHeight(30)

        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setStyleSheet(ScannerStyle.tabstyle)

        self.sumcontainer = QtWidgets.QWidget()
        self.sumcontainer.setStyleSheet(ScannerStyle.containerstyle)

        self.sumlayout = QtWidgets.QVBoxLayout(self.sumcontainer)
        self.sumlayout.setContentsMargins(5, 10, 5, 10)
        self.sumlayout.setSpacing(10)

        self.sumtitle = QtWidgets.QLabel("Quick Summary")
        self.sumtitle.setStyleSheet(ScannerStyle.summarytitle)
        self.sumlayout.addWidget(self.sumtitle)

        self.cardcontainer = QtWidgets.QWidget()
        self.cardlayout = QtWidgets.QHBoxLayout(self.cardcontainer)
        self.cardlayout.setContentsMargins(0, 5, 0, 0)
        self.cardlayout.setSpacing(5)

        self.ttluphosts = self._create_card("Total Up Hosts", "None")
        self.ttldownhosts = self._create_card("Total Down Hosts", "None")
        self.opports = self._create_card("Total Open Ports", "None")
        self.services = self._create_card("Services", "None")

        self.cardlayout.addWidget(self.ttluphosts)
        self.cardlayout.addWidget(self.ttldownhosts)
        self.cardlayout.addWidget(self.opports)
        self.cardlayout.addWidget(self.services)
        self.sumlayout.addWidget(self.cardcontainer)

        self.Nmapoutput = QtWidgets.QLabel("Terminal")
        self.Nmapoutput.setStyleSheet(ScannerStyle.scannertitlestylesheet)
        self.scrollarea = QtWidgets.QScrollArea()
        self.scrollarea.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.scrollarea.setStyleSheet(ScannerStyle.scrollstyle)

        self.sresult = QtWidgets.QPlainTextEdit()
        self.inputscan.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.sresult.setStyleSheet(ScannerStyle.terminal)
        self.sresult.setContentsMargins(5, 5, 5, 5)
        self.sresult.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.sresult.setReadOnly(True)
        self.scrollarea.setWidget(self.sresult)
        self.scrollarea.setWidgetResizable(True)

        self.text_tab = QtWidgets.QWidget()
        self.textlayout = QtWidgets.QVBoxLayout(self.text_tab)
        self.textlayout.setContentsMargins(10, 10, 10, 10)
        self.textlayout.setSpacing(10)

        self.textlayout.addWidget(self.sumcontainer)
        self.textlayout.addWidget(self.Nmapoutput)
        self.textlayout.addWidget(self.scrollarea, 1)

        self.tree_tab = QtWidgets.QWidget()
        self.treelayout = QtWidgets.QVBoxLayout(self.tree_tab)
        self.treelayout.setContentsMargins(10, 10, 10, 10)
        self.treelayout.setSpacing(10)

        self.treetitle = QtWidgets.QLabel('Hierarchical View')
        self.treetitle.setStyleSheet(ScannerStyle.scannertitlestylesheet)

        self.tree = QtWidgets.QTreeView()
        self.tree.setStyleSheet(ScannerStyle.treestyle)
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(['Host', 'Protocol', 'Port', 'State', 'Name', 'Service', 'Version', 'Extra Info', 'Risk Level'])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setModel(self.model)
        self.tree.setHeaderHidden(False)

        self.treectrl = QtWidgets.QHBoxLayout()
        self.expandbtn = QtWidgets.QPushButton("Expand All")
        self.expandbtn.setStyleSheet(ScannerStyle.btnestylesheet)
        self.expandbtn.setMinimumSize(100, 40)
        self.expandbtn.clicked.connect(self.tree.expandAll)

        self.colbtn = QtWidgets.QPushButton("Collapse All")
        self.colbtn.setStyleSheet(ScannerStyle.btncstylesheet)
        self.colbtn.setMinimumSize(100, 40)
        self.colbtn.clicked.connect(self.tree.collapseAll)

        self.treectrl.addWidget(self.expandbtn)
        self.treectrl.addWidget(self.colbtn)
        self.treectrl.addWidget(self.chcolmod)
        self.treectrl.addStretch()

        self.treelayout.addWidget(self.treetitle)
        self.treelayout.addLayout(self.treectrl)
        self.treelayout.addWidget(self.tree, 1)

        self.tabs.addTab(self.text_tab, "Text Output")
        self.tabs.addTab(self.tree_tab, "Tree View")
        self.layoutcon.addWidget(self.title1, 0, 0, 1, 0)
        self.layoutcon.addWidget(self.inputscan, 1, 0)
        self.layoutcon.addWidget(self.inputbtn, 1, 1)
        self.layoutcon.addWidget(self.stopbtn, 1, 2)
        self.layoutcon.addWidget(self.title2, 2, 0, 1, 0)
        self.layoutcon.addWidget(self.tabs, 4, 0, 1, 0)
        self.layoutcon.addWidget(self.progressbar, 5, 0, 1, 0)

    def _create_card(self, title, value):

        card = QtWidgets.QWidget()
        card.setStyleSheet(ScannerStyle.cardstylesheet)

        cardlayout = QtWidgets.QVBoxLayout(card)
        cardlayout.setContentsMargins(0, 0, 0, 0)
        cardlayout.setSpacing(5)

        titlelabel = QtWidgets.QLabel(title)    
        titlelabel.setStyleSheet(ScannerStyle.cardtitlestylesheet)
        titlelabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 

        valuelabel = QtWidgets.QLabel(value)
        valuelabel.setStyleSheet(ScannerStyle.cardvaluestylesheet)
        valuelabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)   

        cardlayout.addWidget(titlelabel)
        cardlayout.addWidget(valuelabel)

        return card
    
    def _update_card(self, card, value):

        layout = card.layout()
        valuelabel = None

        if layout and layout.count() > 0:
            valuelabel = layout.itemAt(1).widget()
        if valuelabel:
            valuelabel.setText(str(value))

    def _comprehensive(self):

        self.comcontainer = QtWidgets.QWidget()
        self.comcontainer.setStyleSheet(ScannerStyle.containerstyle)
        
        comlayout = QtWidgets.QVBoxLayout(self.comcontainer)
        comlayout.setContentsMargins(15, 10, 15, 10)
        comlayout.setSpacing(10)
        
        comtitle = QtWidgets.QLabel("Detailed Result")
        comtitle.setStyleSheet(ScannerStyle.summarytitle)
        comlayout.addWidget(comtitle)
        
        self.host_tabs = QtWidgets.QTabWidget()
        self.host_tabs.setStyleSheet(ScannerStyle.tabstyle)
        comlayout.addWidget(self.host_tabs)
        
        self.tabs.addTab(self.comcontainer, "Detailed Result")
        
        self.comprehensive_initialized = True

    def _update_comprehensive_result(self):

        if not hasattr(self, 'comprehensive_initialized') or not self.comprehensive_initialized:
            return
            
        self.host_tabs.clear()

        with open(self.filepath, 'r') as f:
            content = json.load(f)
        
        if isinstance(content, list):
            content = content[0]

        for ip, host in content.get('scan', {}).items():
            host_tab = self._create_host_tab(ip, host, type='c')
            self.host_tabs.addTab(host_tab, ip)

    def _vuln(self):

        vulncontainer = QtWidgets.QWidget()
        vulncontainer.setStyleSheet(ScannerStyle.containerstyle)
        
        vulnlayout = QtWidgets.QVBoxLayout(vulncontainer)
        vulnlayout.setContentsMargins(15, 10, 15, 10)
        vulnlayout.setSpacing(10)
        
        vulntitle = QtWidgets.QLabel("Vulnerability Result")
        vulntitle.setStyleSheet(ScannerStyle.summarytitle)
        vulnlayout.addWidget(vulntitle)
        
        self.host_tabs = QtWidgets.QTabWidget()
        self.host_tabs.setStyleSheet(ScannerStyle.tabstyle)
        vulnlayout.addWidget(self.host_tabs)
        
        solcontainer = QtWidgets.QWidget()
        solcontainer.setStyleSheet(ScannerStyle.containerstyle)
        
        solvulnlayout = QtWidgets.QVBoxLayout(solcontainer)
        solvulnlayout.setContentsMargins(15, 10, 15, 10)
        solvulnlayout.setSpacing(10)
        
        solvulntitle = QtWidgets.QLabel("Vulnerability Solutions")
        solvulntitle.setStyleSheet(ScannerStyle.summarytitle)
        solvulnlayout.addWidget(solvulntitle)
        
        self.host_tabs_sol = QtWidgets.QTabWidget()
        self.host_tabs_sol.setStyleSheet(ScannerStyle.tabstyle)
        solvulnlayout.addWidget(self.host_tabs_sol)

        self.tabs.addTab(vulncontainer, "Vulnerability Result")
        self.tabs.addTab(solcontainer, "Vulnerability Solutions")
        
        self.vulnerability_initialized = True

    def _update_vuln_result(self):

        if not hasattr(self, 'vulnerability_initialized') or not self.vulnerability_initialized:
            return

        self.host_tabs.clear()

        with open(self.filepath, 'r') as f:
            content = json.load(f)
        
        if isinstance(content, list):
            content = content[0]

        for ip, host in content.get('scan', {}).items():
            host_tab = self._create_host_tab(ip, host, type='v')
            self.host_tabs.addTab(host_tab, ip)

    def _update_vuln_sol(self):

        if not hasattr(self, 'vulnerability_initialized') or not self.vulnerability_initialized:
            return

        self.host_tabs_sol.clear()

        with open(self.filepath, 'r') as f:
            content = json.load(f)
        
        if isinstance(content, list):
            content = content[0]

        for ip, host in content.get('scan', {}).items():
            host_tab = self._create_vuln_chat(ip, host)
            self.host_tabs_sol.addTab(host_tab, ip)
    
    def _change_col_mode(self):

        header = self.tree.header()
        current_mode = header.sectionResizeMode(0)
        if current_mode == QHeaderView.ResizeMode.Interactive:
            for i in range(self.model.columnCount()):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
                self.chcolmod.setText("Current Mode: Resize To Contents")
        else:
            for i in range(self.model.columnCount()):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
                self.chcolmod.setText("Current Mode: Interactive")
            
    def _create_vuln_chat(self, ip, host):
        
        tab_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab_widget)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title_container = QtWidgets.QWidget()
        title_layout = QtWidgets.QHBoxLayout(title_container)
        vul_title = QtWidgets.QComboBox()
        vul_title.setStyleSheet(ScannerStyle.combo_all)
        script = self._format_vul_script(host)
        options = []
        for i in script:
            options.append(i["id"])
        vul_title.addItems(options)
        vul_title.setCurrentIndex(0)

        vul_chat = QtWidgets.QPushButton("View")
        vul_chat.setStyleSheet(ScannerStyle.scanbtnstylesheet)
        vul_chat.setMinimumSize(75, 40)

        title_layout.addWidget(vul_title)
        title_layout.addWidget(vul_chat)

        chat_container = QtWidgets.QWidget()
        chat_layout = QtWidgets.QVBoxLayout(chat_container)
        chat_title = QtWidgets.QLabel("Caution: The result is generated by AI, content is for reference only.")
        chat_title.setStyleSheet("""background: #FEC901; font-weight: bold; font-size: 16px;""")
        chat_scroll = QtWidgets.QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_result =QtWidgets.QPlainTextEdit()
        chat_result.setPlainText("Please select the vulnerability you would like to learn about from the list above.")
        chat_result.setStyleSheet(ScannerStyle.terminal)
        chat_result.setReadOnly(True)
        chat_scroll.setWidget(chat_result)
        chat_tabs = QtWidgets.QTabWidget()
        chat_tabs.setStyleSheet(ScannerStyle.tabstyle)
        chat_tabs.hide()
        if self.api_ai is None or self.api_ai == "":
            vul_chat.setDisabled(True)
            vul_chat.setStyleSheet("""
                                   background-color: transparent;
                                   border: solid 5px #8FC9FF;
                                   border-radius: 8px;""")
            vul_chat.setText("Invalid API")
        else:
            vul_chat.setDisabled(False)
        vul_chat.clicked.connect(lambda: self._deploy_chatbot(vul_title, chat_result, chat_tabs, chat_scroll))
        chat_layout.addWidget(chat_title)
        chat_layout.addWidget(chat_scroll)
        chat_layout.addWidget(chat_tabs)

        layout.addWidget(title_container)
        layout.addWidget(chat_container)
        return tab_widget

    def _deploy_chatbot(self, target, container, chat_tabs, chat_scroll):
        try:
            vuln = target.currentText().strip()
            chat_prompt = (f"Vulnerability: {vuln}\n"                       
                        "Task:\n"
                        "1) Explain what this vulnerability is.\n"
                        "2) Explain how to fix it.\n"
                        "3) Provide prevention steps and an IT admin action plan.\n"
                        "Output format:\n"
                        "Plain text only\n"
                        "[Sections] Issue, Risk, Fix Steps, Prevention, Action Plan\n"
                        "Strictly follow these headers for each section: Issue:\n[Describe here]\nRisk:\n[Describe here]\nFix Steps:\n[Describe here]\nPrevention:\n[Describe here]\nAction Plan\n[Describe here]"
                        "Returns plain text only, limiting the symbol and table use. Strict follow the output format."
                        )
            chat_tabs.clear()
            chat_tabs.hide()
            chat_scroll.show()
            container.show()
            container.setPlainText("Getting the result, please wait...")
            
            if hasattr(self, "chatworker") and self.chatworker and self.chatworker.isRunning():
                self.chatworker.terminate()
                self.chatworker.wait()
            self.chatworker = ChatWorker(target, chat_prompt, api_ai=self.api_ai)
            self.chatworker.finished.connect(
                lambda result: self._chat_finished(result, container, chat_tabs, chat_scroll)
            )
            self.chatworker.start()
        except Exception as e:
            function.logging.error(f"Error occur when deploying OpenAI: {str(e)}")

    def _chat_finished(self, result, container, chat_tabs, chat_scroll):
        text = result if isinstance(result, str) else str(result)
        clean = text.replace("```", "").replace("**", "").replace("##", "").strip()

        sections = self._parse_chat_sections(clean)
        chat_tabs.clear()

        titles = ["Issue", "Risk", "Fix Steps", "Prevention", "Action Plan"]

        if not sections:
            response = clean
            if response == "":
                response = "No response returned."
            tab = self._create_chat_tab(response)
            chat_tabs.addTab(tab, "Response")
            chat_scroll.hide()
            chat_tabs.show()
            return

        for title in titles:
            raw = sections.get(title, "")
            if raw is None:
                raw = ""
            content = raw.strip()
            if content == "":
                content = "No content returned for this section."
            tab = self._create_chat_tab(content)
            chat_tabs.addTab(tab, title)

        chat_scroll.hide()
        chat_tabs.show()

    def _create_chat_tab(self, content):

        tab_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setStyleSheet(ScannerStyle.comscrollstylesheet)

        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        chat_result = QtWidgets.QPlainTextEdit(content_widget)
        chat_result.setReadOnly(True)
        chat_result.setPlainText(content)
        chat_result.setStyleSheet(ScannerStyle.terminal)
        content_layout.addWidget(chat_result)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        return tab_widget

    def _parse_chat_sections(self, text: str):
        titles = ["Issue", "Risk", "Fix Steps", "Prevention", "Action Plan"]
        if not text:
            return {}
        s = str(text).strip()

        s = re.sub(r"(?im)^\s*(?:[-*]\s*)?Issue\s*:?\s*$", "#Issue#", s)
        s = re.sub(r"(?im)^\s*(?:[-*]\s*)?Risk\s*:?\s*$", "#Risk#", s)
        s = re.sub(r"(?im)^\s*(?:[-*]\s*)?Fix\s*Steps\s*:?\s*$", "#Fix Steps#", s)
        s = re.sub(r"(?im)^\s*(?:[-*]\s*)?Prevention\s*:?\s*$", "#Prevention#", s)
        s = re.sub(r"(?im)^\s*(?:[-*]\s*)?Action\s*Plan\s*:?\s*$", "#Action Plan#", s)

        raw_parts = s.split("#")
        parts = []

        for p in raw_parts:
            clean_p = p.strip()
    
            if clean_p != "":
                parts.append(clean_p)

        sections = {}
        i = 0
        while i + 1 < len(parts):
            key = parts[i]
            val = parts[i + 1]
            if key in titles and key not in sections:
                sections[key] = val
            i += 2
        return sections

    def _debug_window(self, target_ip):

        port_errors = {} 
        host_errors = [] 
        
        try:
            if self.filepath and os.path.exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    content = json.load(f)
                if isinstance(content, list): content = content[0]
                
                host_data = content.get('scan', {}).get(target_ip, {})
                
                for p in ['tcp', 'udp']:
                    if p in host_data:
                        for port, info in host_data[p].items():
                            scripts = info.get('script', {})
                            for s_id, s_output in scripts.items():
                                if "ERROR: Script execution failed" in str(s_output):
                                    if port not in port_errors: port_errors[port] = []
                                    port_errors[port].append(s_id)
                
                hostscripts = host_data.get('hostscript', [])
                for hs in hostscripts:
                    if "ERROR: Script execution failed" in str(hs.get('output')):
                        host_errors.append(hs.get('id'))

        except Exception as e:
            function.logging.error(f"Error parsing scan file: {str(e)}")

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Nmap Debug Result - {target_ip}")
        dialog.setStyleSheet("""background: #F5F9FF;""")
        dialog.resize(900, 700)
        layout = QtWidgets.QVBoxLayout(dialog)

        output_result = QtWidgets.QPlainTextEdit()
        output_result.setStyleSheet(ScannerStyle.terminal)
        output_result.setReadOnly(True)
        layout.addWidget(output_result)
        
        commands_to_run = []
        
        if port_errors:
            all_ports = ",".join([str(p) for p in port_errors.keys()])
            all_port_scripts = set()
            for s_list in port_errors.values(): all_port_scripts.update(s_list)
            scripts_str = ",".join(all_port_scripts)
            commands_to_run.append(f"nmap -p {all_ports} --script {scripts_str} -d {target_ip}")
        
        if host_errors:
            scripts_str = ",".join(host_errors)
            commands_to_run.append(f"nmap --script {scripts_str} -d {target_ip}")

        if not commands_to_run:
            commands_to_run.append(f"nmap --script vuln -d {target_ip}")


        preview = "The following debug commands will be executed:\n"
        for i, cmd in enumerate(commands_to_run):
            preview += f"[{i+1}] {cmd}\n"
        output_result.setPlainText(preview + "\nRunning command...\n" + "-"*50 + "\n")

        full_command = " && ".join(commands_to_run)
        
        def _output_result_alive(text):
            from PyQt6 import sip
            if not sip.isdeleted(output_result):
                output_result.appendPlainText(f"\nScan Finished:\n{text}")
            else:
                pass

        worker = DebugWorker(target_ip, self.nmap_path, custom_cmd=full_command)
        dialog.finished.connect(worker.stop)
        worker.finished.connect(_output_result_alive)
        worker.failed.connect(lambda text: _output_result_alive(f"Error: {text}"))

        closebtn = QtWidgets.QPushButton("Close")
        closebtn.clicked.connect(dialog.close)
        closebtn.setStyleSheet(ScannerStyle.stopbtnstylesheet)
        layout.addWidget(closebtn)

        if not hasattr(self, "_debug_worker"): self._debug_worker = []
        self._debug_worker.append(worker)
        worker.start()
        dialog.exec()

    def _create_host_tab(self, ip, host, type='c'):

        tab_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setStyleSheet(ScannerStyle.comscrollstylesheet)

        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        if type.lower() == 'c':

            self._add_info_section(content_layout, "Addresses", self._format_addresses(host))
            self._add_info_section(content_layout, "Vendor", self._format_vendor(host))
            self._add_info_section(content_layout, "Status", self._format_status(host))
            self._add_info_section(content_layout, "Uptime", self._format_uptime(host))
            self._add_info_table(content_layout, "Ports (TCP/UDP)", self._format_ports(host))
            os_section = self._add_os_section(host)
            content_layout.addWidget(os_section)

        elif type.lower() == 'v':
            
            script = self._format_vul_script(host)

            def _create_vuln_box(script):

                container = QtWidgets.QWidget()
                container_layout = QtWidgets.QVBoxLayout(container)

                for i in script:
                    section = function.collapse_section(f"Protocol: {i['Protocol']} Port: {i['Port']} Title: {i['id']}", start_open=False)
                    output = QtWidgets.QLabel(f"{i['output']}")
                    output.setStyleSheet(ScannerStyle.vulncontentstylesheet)
                    output.setContentsMargins(40, 10, 10, 10)
                    output.setWordWrap(True)
                    section._add_widget(output)
                    container_layout.addWidget(section)
                
                error_text = "ERROR: Script execution failed (use -d to debug)"
                for i in script:
                    if error_text in (i["output"]):
                        debugbtn = QtWidgets.QPushButton("Debug")
                        debugbtn.setStyleSheet(ScannerStyle.scanbtnstylesheet)
                        debugbtn.setMinimumSize(75, 40)
                        debugbtn.clicked.connect(lambda: self._debug_window(ip))
                        self.layoutcon.addWidget(debugbtn, 1, 3)
                        break

                return container
            
            def _explain_vuln(script):

                container = QtWidgets.QWidget()
                container_layout = QtWidgets.QVBoxLayout(container)
                section_count = []

                for i in script:
                    name = f"Title: {i['id']}"
                    section = function.collapse_section(name, start_open=False)
                    loading = QtWidgets.QLabel("Extracting Information...")
                    loading.setStyleSheet("color: #FF0000; font-size: 16px;")
                    section._add_widget(loading)

                    section_count.append({
                        'section': section,
                        'loading': loading,
                        'script_id': i['id']
                    })
                    container_layout.addWidget(section)
                
                for fetched in section_count:
                    vulnworker = VulnWorker(
                        api_vulner=self.api_vulners,
                        query=f"title:{fetched['script_id']}",
                        section=fetched['section'],
                        loading=fetched['loading']
                    )
                    vulnworker.finished.connect(self._update_vuln_info)
                    vulnworker.start()

                    if not hasattr(self, 'vuln_worker_queue'):
                        self.vuln_worker_queue = []
                    self.vuln_worker_queue.append(vulnworker)
                return container

            self._add_info_section(content_layout, "Script Result", _create_vuln_box(script))
            self._add_info_section(content_layout, "Script Explanation", _explain_vuln(script))

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        return tab_widget
    
    def _add_info_section(self, layout, title, content):

        section = QtWidgets.QWidget()
        section.setStyleSheet("background: #FFFFFF; border-radius: 5px; padding: 10px;")
        section_layout = QtWidgets.QVBoxLayout(section)
        section_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        section_layout.setContentsMargins(10, 10, 10, 10)
        section_layout.setSpacing(5)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #6488EA;")
        section_layout.addWidget(title_label)
        
        if isinstance(content, str):
            content_label = QtWidgets.QLabel(content)
            content_label.setStyleSheet("font-size: 12px; color: #333333;")
            content_label.setWordWrap(True)
            section_layout.addWidget(content_label)
        else:
            section_layout.addWidget(content)
        
        layout.addWidget(section)
    
    def _add_info_table(self, layout, title, content):


        section = QtWidgets.QWidget()
        section.setStyleSheet("background: #FFFFFF;")
        section_layout = QtWidgets.QVBoxLayout(section)
        section_layout.setContentsMargins(0, 5, 5, 5)
        section_layout.setSpacing(0)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #6488EA;")
        section_layout.addWidget(title_label)
        

        header = content[1]
        info = content[0]

        if "No ports found" not in str(info):
            table = QtWidgets.QTableWidget()
            table.setStyleSheet(ScannerStyle.tablestyle)
            table.setRowCount(len(info))
            table.setColumnCount(len(header))
            table.setHorizontalHeaderLabels(header)

            for row, row_data in enumerate(info):
                table.setRowHeight(row, 30)
                for col in range(len(header)):
                    data = QtWidgets.QTableWidgetItem(str(row_data[col]))
                    table.setItem(row, col, data)
            
            def _clicked_port(row, col):

                if col == 1:
                    cell = table.item(row, col)
                    if cell:
                        port = cell.text()
                        url = self._check_port(port)
                        if url:
                            url = QtCore.QUrl(url)
                            QDesktopServices.openUrl(url)
            table.cellClicked.connect(_clicked_port)

            table.horizontalHeader().setVisible(True)
            table.setCornerButtonEnabled(False) 
            verheader = table.verticalHeader()
            verheader.setVisible(False)
            verheader.setFixedWidth(0)
            table.setAlternatingRowColors(True)
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setMinimumHeight(40)
            table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            table.resizeColumnsToContents()
            table.resizeRowsToContents()
            table.setViewportMargins(0, 0, 0, 0)
            verheader.setFixedWidth(0)

            section_layout.addWidget(table)
        else:
            no_ports_label = QtWidgets.QLabel("No ports found")
            no_ports_label.setStyleSheet("font-size: 12px; color: #666666;")
            section_layout.addWidget(no_ports_label)

        layout.addWidget(section)
    
    def _add_os_section(self, host):

        section = QtWidgets.QWidget()
        section.setStyleSheet("background: #FFFFFF; border-radius: 5px; padding: 10px;")
        section_layout = QtWidgets.QVBoxLayout(section)
        section_layout.setContentsMargins(10, 10, 10, 10)
        section_layout.setSpacing(10)
        
        title_label = QtWidgets.QLabel("OS Match")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #6488EA;")
        section_layout.addWidget(title_label)
        
        osmatch = host.get('osmatch', [])
        if osmatch:

            fig = Figure(figsize=(6, 3), tight_layout=True)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            name_list = []
            for match in osmatch:  
                name = match.get('name', 'N/A')
                name_list.append(f"{name}")

            accuracy = [int(m.get("accuracy", 0) or 0) for m in osmatch]
            name_list.reverse()
            accuracy.reverse()

            bars = ax.barh(range(len(accuracy)), accuracy, height=0.5, color = "#00d0ef")
            ax.set_yticks(range(len(name_list)))
            ax.set_yticklabels(name_list, ha="right", fontsize=8)
            ax.set_xlim(0, 100)
            ax.bar_label(bars, labels= accuracy)
            ax.set_xlabel("Accuracy (%)")

            canvas.draw()
            section_layout.addWidget(canvas)

            osfamily = set()
            for match in osmatch:
                for os in match.get('osclass', []):
                    fam = os.get('osfamily', 'N/A')
                    osfamily.add(fam)
            
            osguess = QtWidgets.QLabel("OS Family: ")
            osres = QtWidgets.QLabel(f"The host has a high probability of running on {','.join(osfamily)}!")

            section_layout.addWidget(osguess)
            section_layout.addWidget(osres)   
        else:
            no_data = QtWidgets.QLabel("No OS match data available")
            no_data.setStyleSheet("font-size: 12px; color: #666666;")
            section_layout.addWidget(no_data)
        
        return section
    
    def _format_addresses(self, host):

        addresses = host.get('addresses', {})
        lines = []
        if addresses.get('ipv4'):
            lines.append(f"IPv4: {addresses.get('ipv4')}")
        if addresses.get('mac'):
            lines.append(f"MAC: {addresses.get('mac')}")
        hostnames = host.get('hostnames', [])
        if hostnames:
            names = ', '.join([h.get('name', '') for h in hostnames])
            lines.append(f"Hostnames: {names}")
        return '\n'.join(lines) if lines else "N/A"
    
    def _format_vendor(self, host):

        vendor = host.get('vendor', {})
        if vendor:
            return '\n'.join([f"{mac}: {name}" for mac, name in vendor.items()])
        return "N/A"
    
    def _format_status(self, host):

        status = host.get('status', {})
        state = status.get('state', 'N/A')
        reason = status.get('reason', 'N/A')
        return f"State: {state}\nReason: {reason}"
    
    def _format_uptime(self, host):

        uptime = host.get('uptime', {})
        if uptime:
            seconds = uptime.get('seconds', 'N/A')
            lastboot = uptime.get('lastboot', 'N/A')
            return f"Seconds: {seconds}\nLast Boot: {lastboot}"
        return "N/A"
    
    def _format_ports(self, host):

        header = ["Port", "Port Number", "State", "Name", "Product", "Version"]
        lines = []
        tcp = host.get('tcp', {})
        udp = host.get('udp', {})
        
        if tcp:
            for port, info in tcp.items():
                state = info.get('state', 'N/A')
                name = info.get('name', 'N/A')
                product = info.get('product', 'N/A')
                version = info.get('version', 'N/A')
                lines.append(["tcp", port, state, name, product, version])
        
        if udp:
            for port, info in udp.items():
                state = info.get('state', 'N/A')
                name = info.get('name', 'N/A')
                product = info.get('product', 'N/A')
                version = info.get('version', 'N/A')
                lines.append(["udp", port, state, name, product, version])
        
        return lines if lines else "No ports found", header
    
    def _format_vul_script(self, host):

        script = []
        tcp = host.get('tcp', {})
        udp = host.get('udp', {})
        host_script = host.get('hostscript', [])

        if tcp:
            for port, info in tcp.items():
                if info.get('script', {}):
                    for id, output in info['script'].items():
                        if id:
                            script.append({
                                'Protocol': 'tcp',
                                'Port': port,
                                'id': id,
                                'output': output
                            }) 
                        else:
                            script.append({
                                'Protocol': 'tcp',
                                'Port': port,
                                'id': 'N/A',
                                'output': 'N/A'
                            }) 
        if udp:
            for port, info in udp.items():
                if info.get('script', {}):
                    for id, output in info['script'].items():
                        if id:
                            script.append({
                                'Protocol': 'udp',
                                'Port': port,
                                'id': id,
                                'output': output
                            }) 
                        else:
                            script.append({
                                'Protocol': 'udp',
                                'Port': port,
                                'id': 'N/A',
                                'output': 'N/A'
                            }) 
        if host_script:
            for j in host_script:
                if j.get('id', ''):
                    script.append({
                        'Protocol': 'N/A',
                        'Port': 'N/A',
                        'id': j['id'],
                        'output': j['output']
                    }) 

        return script
    
    def _terminal_display(self, content):

        if isinstance(content, list):
            content = content[0]

        rows = []
        rows.append('#' * 50 + '\n')
        rows.append('NMAP SCAN RESULTS' + '\n')
        rows.append('#' * 50 + '\n\n')

        nmap = content.get('nmap', {})
        rows.append(f"Command: {nmap.get('command_line', 'N/A')}\n")
        rows.append(f"Scan Info: {nmap.get('scaninfo', 'N/A')}\n\n")
        
        stats = nmap.get('scanstats', {})
        rows.append(f"Time: {stats.get('timestr', 'N/A')}\n")
        rows.append(f"Elapsed: {stats.get('elapsed', 'N/A')} seconds\n")
        rows.append(f"Online Hosts: {stats.get('uphosts', 'N/A')}\n")
        rows.append(f"Offline Hosts: {stats.get('downhosts', 'N/A')}\n")
        rows.append(f"Total Hosts: {stats.get('totalhosts', 'N/A')}\n\n")

        rows.append('#' * 50 + '\n')
        rows.append('HOST(S) DETAILS' + '\n')
        rows.append('#' * 50 + '\n\n')

        for ip, host in content.get('scan', {}).items():
            rows.append(f"Host: {ip}\n")
            rows.append("-" * 50 + "\n")
            rows.append(f"Hostnames: {', '.join(h['name'] for h in host.get('hostnames', []))}\n")
            rows.append(f"IPv4: {host.get('addresses', {}).get('ipv4', 'N/A')}\n")
            rows.append(f"MAC: {host.get('addresses', {}).get('mac', 'N/A')}\n")
            rows.append(f"State: {host.get('status', {}).get('state', 'N/A')}\n\n")
            
            tcp = host.get('tcp', {})
            if tcp:
                rows.append("Open Ports:\n")
                rows.append(f"  Title   | State | Reaseon | Name | Product | Version | Extrainfo | Conf | Cpe\n")
                for port, meta in tcp.items():
                    rows.append(f"  Port {port}: {meta.get('state', 'N/A') or 'N/A'} | {meta.get('reason', 'N/A') or 'N/A'} | {meta.get('name', 'N/A') or 'N/A'} | {meta.get('product', 'N/A') or 'N/A'} | {meta.get('version', 'N/A') or 'N/A'} | {meta.get('extrainfo', 'N/A') or 'N/A'} | {meta.get('conf', 'N/A') or 'N/A'} | {meta.get('cpe', 'N/A') or 'N/A'}\n")
                    
                    if meta.get('script', {}):
                        rows.append(f"Vulner Script Result(Port{port}):\n")
                        for title, result in meta.get('script', {}).items():
                            rows.append(f" {title}: {result}\n")
                rows.append("\n") 

            udp = host.get('udp', {})
            if udp:
                rows.append("Open Ports:\n")
                for port, meta in udp.items():
                    rows.append(f"  Port {port}: {meta.get('state', 'N/A') or 'N/A'} | {meta.get('reason', 'N/A') or 'N/A'} | {meta.get('name', 'N/A') or 'N/A'} | {meta.get('product', 'N/A') or 'N/A'} | {meta.get('version', 'N/A') or 'N/A'} | {meta.get('extrainfo', 'N/A') or 'N/A'} | {meta.get('conf', 'N/A') or 'N/A'} | {meta.get('cpe', 'N/A') or 'N/A'}\n")
                    
                    if meta.get('script', {}):
                        rows.append(f"Vulner Script Result(Port{port}):\n")
                        for title, result in meta.get('script', {}).items():
                            rows.append(f" {title}: {result}\n")
                rows.append("\n") 

            hostscript = host.get('hostscript', [])
            if hostscript:
                rows.append('Host Script Result:\n')
                for r in hostscript:
                    rows.append(f"ID: {r['id']}\n")
                    rows.append(f"Output: {r['output']}\n")
                rows.append('\n')

            rows.append('\n')

        return "".join(rows)
    
    def _progress(self):

        self.progressbar = QtWidgets.QProgressBar()
        self.progressbar.setStyleSheet(ScannerStyle.barstyle)
        self.progressbar.setRange(0, 0)
        self.progressbar.setValue(20)
        self.progressbar.setMinimumWidth(500)
        self.progressbar.hide()

    def _check_port(self, port):

        url="https://datatracker.ietf.org/doc/html/"
        port_csv = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "Document", "service-names-port-numbers.csv")
        )

        try:
            with open(port_csv, 'r', encoding='utf-8') as f:
                read_csv = csv.reader(f)
                for row in read_csv:
                    if len(row) > 8:
                        if row[1] == port and row[8].strip():
                            uri = row[8]
                            uri = uri.strip('[]')
                            return f"{url}{uri}"
                return function.error_msg(title="Error", msg="No reference documentation found for this port!\nYou may try to search the internet!")
        except Exception as e:
            function.logging.error(f'Error reading {port_csv}: {str(e)}')
        
        return None
    
    def _create_grid(self, result):

        grid = QtWidgets.QWidget()
        grid.setStyleSheet(ScannerStyle.vulgridstylesheet)  
        
        gridlayout = QtWidgets.QVBoxLayout(grid)
        gridlayout.setSpacing(5)
        gridlayout.setContentsMargins(10, 10, 10, 10)

        vtype = result.get('type', '')
        title = result.get('title', 'Unknown')
        published = result.get('published', 'Unknown')
        descri = result.get('description', 'Unknown')
        cvelist = result.get('cvelist', [])
        cvss = result.get('cvss', {})

        if vtype:
            typelabel = QtWidgets.QLabel(f"Type: {vtype}")
            typelabel.setStyleSheet("font-size: 12px; font-weight: bold; color: #0E1111;")
            gridlayout.addWidget(typelabel)
        
        titlelabel = QtWidgets.QLabel(title)
        titlelabel.setStyleSheet("font-size: 12px; font-weight: bold; color: #0E1111;")
        titlelabel.setWordWrap(True)
        gridlayout.addWidget(titlelabel)
        
        datelabel = QtWidgets.QLabel(f"Published: {published}")
        datelabel.setStyleSheet("font-size: 12px; color: #0E1111;")
        gridlayout.addWidget(datelabel)
        
        if cvss and isinstance(cvss, dict):
            cvsscontainer = QtWidgets.QWidget()
            cvssscore = cvss.get('score', 'N/A')
            cvsslayout = QtWidgets.QHBoxLayout(cvsscontainer)
            cvsslabel = QtWidgets.QLabel(f"CVSS Score:")
            cvsslabel.setStyleSheet("font-size: 12px; color: #0E1111; font-weight: bold; border: none; padding: 0px;")
            if 'N/A' not in str(cvssscore):

                scorebar = QtWidgets.QProgressBar()
                scorebar.setRange(0, 100)
                scorebar.setValue(int(float(cvssscore) * 10))
                scorebar.setFormat(f"{float(cvssscore)}/10")
                if float(cvssscore) < 4:
                    color = "#6FC276"
                elif  float(cvssscore) < 7:
                    color = "#FFF49B"
                elif  float(cvssscore) < 9:
                    color = "#F5CA7B"
                else:
                    color = "#FF2C2C"
                scorebar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 3px solid #0E1111;
                        text-align:center;
                        color:#FFFFFF;
                        height: 20px;
                        border-radius: 8px;
                        width:150px;
                        padding: 0px;
                        margin: 0px;
                    }}
                    QProgressBar::chunk {{
                        background: {color};
                        border-radius: 7px;
                        margin: 0px;
                        width: 5px;
                    }}
                """)
                cvsslayout.addWidget(cvsslabel)
                cvsslayout.addWidget(scorebar)
            else:
                score = QtWidgets.QLabel(f"{cvssscore}")
                score.setStyleSheet("font-size: 12px; color: #000000; font-weight: bold; border: none;")
                cvsslayout.addWidget(cvsslabel)
                cvsslayout.addWidget(score)
            gridlayout.addWidget(cvsscontainer)

        if cvelist:
            cvetext = ', '.join(cvelist[:5])
            if len(cvelist) > 5:
                cvetext += f" (+{len(cvelist) - 5} more)"
            cvelabel = QtWidgets.QLabel(f"CVEs: {cvetext}")
            cvelabel.setStyleSheet("font-size: 12px; color: #0E1111;")
            gridlayout.addWidget(cvelabel)
        
        desclabel = QtWidgets.QPlainTextEdit(descri)
        desclabel.setContentsMargins(5, 5, 5, 5)
        desclabel.setLineWrapMode(desclabel.LineWrapMode.NoWrap)
        desclabel.setFrameStyle(1)
        desclabel.setReadOnly(True)
        gridlayout.addWidget(desclabel)

        return grid 
    



