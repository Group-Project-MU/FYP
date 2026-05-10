import nmap, json, os, shlex
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from Widgets import function, ScannerStyle, Scriptselector

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
    
class CustScan(QtWidgets.QWidget):

    progress_signal = QtCore.pyqtSignal(object)
    
    def __init__(self, nmap_path=None, name="", placeholder="", command="", title=None):

        super().__init__()
        self.window_title = title
        self.nmap_path = nmap_path
        self.name = name
        self.placeholder = placeholder
        self.progress_signal.connect(self._update_result)
        self.worker = None 
        self.filepath = None
        self._progress()
        self.layout()
        self.inputscan.textChanged.connect(self._update_command)

    def _update_command(self):
        self.command = self.inputscan.text()

    def _clear_thread(self):
        
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
            
    def closeEvent(self, event):
        self._clear_thread()
        if event:
            event.accept()

    def _runscan(self):
        
        parser_ip, parser_command = self._get_command(self.command)

        try:
            if parser_ip is not None and function.error_handle(parser_ip):

                self._clear_thread()
                self.progressbar.show()
                self.worker = Worker(self._nmapscan, parser_ip, parser_command)
                self.worker.finished.connect(self._scan_finished)
                self.worker.start()
            else:
                self.sresult.setPlainText(f"Invalid input!")
                function.error_msg("Error", msg=f'Invalid input!\n Command: {parser_command}\nIP: {parser_ip}')
                function.logging.error(f"Invalid command or ip: {parser_command}/{parser_ip}")

        except nmap.PortScannerError as e:
            function.logging.error(f"{e}")

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

    def _get_command(self, command):
        
        raw = (command or "").strip()
        arguments = shlex.split(raw, posix=False)

        if not arguments:
            function.error_msg("Error", "Empty command")
            return None, None
        
        first = arguments[0].lower()
        if "nmap" in first:
            arguments = arguments[1:]

        if len(arguments) < 1:
            function.error_msg("Error", "Invaild command")
            return None, None
        
        parser_ip = arguments[-1]
        parser_command = " ".join(arguments[:-1])
        return parser_ip, parser_command
    
    def _update_result(self):

        with open(self.filepath, 'r') as f:
        
            content = json.load(f)

        if isinstance(content, list):
            content = content[0]


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
        self.inputscan.returnPressed.connect(lambda: self._runscan())
                                             
        self.inputbtn = QtWidgets.QPushButton(self)
        self.inputbtn.setText('Start Scan')
        self.inputbtn.setStyleSheet(ScannerStyle.scanbtnstylesheet)
        self.inputbtn.setMinimumSize(75, 40)
        self.stopbtn = QtWidgets.QPushButton(self)
        self.stopbtn.setText('Stop Scan')
        self.stopbtn.setStyleSheet(ScannerStyle.stopbtnstylesheet)
        self.stopbtn.setMinimumSize(75, 40)

        self.scriptbtn = QtWidgets.QPushButton(self)
        self.scriptbtn.setText('Scripts')
        self.scriptbtn.setStyleSheet(ScannerStyle.scanbtnstylesheet)
        self.scriptbtn.setMinimumSize(75, 40)
        self.scriptbtn.clicked.connect(lambda: self._connect_selector())

        self.inputbtn.clicked.connect(lambda: self._runscan())
        self.stopbtn.clicked.connect(self._stop_button)

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

        self.sumtitle = QtWidgets.QLabel("Terminal")
        self.sumtitle.setStyleSheet(ScannerStyle.summarytitle)
        self.sumlayout.addWidget(self.sumtitle)

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
        self.textlayout.addWidget(self.scrollarea, 1)

        self.tree_tab = QtWidgets.QWidget()
        self.treelayout = QtWidgets.QVBoxLayout(self.tree_tab)
        self.treelayout.setContentsMargins(10, 10, 10, 10)
        self.treelayout.setSpacing(10)

        self.treetitle = QtWidgets.QLabel('Hierarchical View')
        self.treetitle.setStyleSheet("""
                                        QLabel{font-size: 20px;
                                                font: bold;
                                                text-align: left;
                                                color: #000000;
                                                background: #8FC9FF;
                                                color: #FFFFFF;
                                                margin: 15px, 10px, 15px, 10px;
                                                border-radius: 8px;
                                                padding-left: 5px;
                                                padding-top: 5px;
                                                padding-bottom: 5px;
                                        }
                                        """)

        self.tree = QtWidgets.QTreeView()
        self.tree.setStyleSheet(ScannerStyle.treestyle)
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(['Host', 'Protocol', 'Port', 'State', 'Name', 'Description', 'Service', 'Version', 'Extra Info', 'Risk Level'])
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
        self.chcolmod = QtWidgets.QPushButton(self)
        self.chcolmod.setText('Current Mode: Interactive')
        self.chcolmod.setStyleSheet(ScannerStyle.resbtnstylesheet)
        self.chcolmod.setMinimumSize(75, 40)
        self.chcolmod.clicked.connect(self._change_col_mode)

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
        self.layoutcon.addWidget(self.scriptbtn, 1, 3)
        self.layoutcon.addWidget(self.title2, 2, 0, 1, 0)
        self.layoutcon.addWidget(self.tabs, 4, 0, 1, 0)
        self.layoutcon.addWidget(self.progressbar, 5, 0, 1, 0)

    def _custom(self):

        self.comcontainer = QtWidgets.QWidget()
        self.comcontainer.setStyleSheet(ScannerStyle.containerstyle)
        
        comlayout = QtWidgets.QVBoxLayout(self.comcontainer)
        comlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        comlayout.setContentsMargins(15, 10, 15, 10)
        comlayout.setSpacing(10)
        
        comtitle = QtWidgets.QLabel("Script Result")
        comtitle.setStyleSheet(ScannerStyle.summarytitle)
        comlayout.addWidget(comtitle)
        
        self.host_tabs = QtWidgets.QTabWidget()
        self.host_tabs.setStyleSheet(ScannerStyle.tabstyle)
        comlayout.addWidget(self.host_tabs)
        
        self.tabs.addTab(self.comcontainer, "Script Result")
        
        self.script_initialized = True

    def _update_script_result(self):

        if not hasattr(self, 'script_initialized') or not self.script_initialized:
            return
            
        self.host_tabs.clear()

        with open(self.filepath, 'r') as f:
            content = json.load(f)
        
        if isinstance(content, list):
            content = content[0]

        for ip, host in content.get('scan', {}).items():
            host_tab = self._create_host_tab(host)
            self.host_tabs.addTab(host_tab, ip)

    def _create_host_tab(self, host):

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
        
        script = self._format_script(host)

        def _create_box(script):

            container = QtWidgets.QWidget()
            container_layout = QtWidgets.QVBoxLayout(container)

            if not script:
                empty = QtWidgets.QLabel("No script output for this host.")
                empty.setStyleSheet("font-size: 12px; color: #666666;")
                empty.setWordWrap(True)
                container_layout.addWidget(empty)
                return container

            for i in script:
                title = i.get("Title", "N/A")
                section = function.collapse_section(
                    f"Protocol: {i.get('Protocol', '')} Port: {i.get('Port', '')} Script: {title}",
                    start_open=False,
                )
                output = QtWidgets.QLabel(str(i.get("Content", "")))
                output.setStyleSheet(ScannerStyle.vulncontentstylesheet)
                output.setContentsMargins(10, 10, 10, 10)
                output.setWordWrap(True)
                section._add_widget(output)
                container_layout.addWidget(section)

            return container

        self._add_info_section(content_layout, "Script Result", _create_box(script))
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
    
    def _format_script(self, host):

        script = []
        tcp = host.get('tcp', {})
        udp = host.get('udp', {})
        host_script = host.get('hostscript', [])

        if tcp:
            for port, pinfo in tcp.items():
                for title, content in (pinfo.get('script') or {}).items():
                    script.append({
                        "Protocol": "tcp",
                        "Port": port,
                        "Title": title if title else "N/A",
                        "Content": content if content is not None else "",
                    })
        if udp:
            for port, pinfo in udp.items():
                for title, content in (pinfo.get('script') or {}).items():
                    script.append({
                        "Protocol": "udp",
                        "Port": port,
                        "Title": title if title else "N/A",
                        "Content": content if content is not None else "",
                    })
        if host_script:
            for j in host_script:
                if j.get('id', ''):
                    script.append({
                        "Protocol": "N/A",
                        "Port": "N/A",
                        "Title": j["id"],
                        "Content": j.get("output", ""),
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

    def _connect_selector(self):

        selector = Scriptselector.ScriptSelector(self)
        if selector.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            cmd = selector.selected_script
            self.inputscan.setText(cmd)



