from PyQt6 import QtWidgets, QtCore, QtGui
import os, json, csv
from Widgets import ScannerStyle, function
from Widgets.ConfigLoader import selectnmap, selectscriptfolder, enterapi
from Widgets.OnboardingTour import program_onboarding

class Topmenu(QtWidgets.QWidget):

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.all_btns = []
        self.layout()


    def layout(self):

        self.layoutcontainer = QtWidgets.QHBoxLayout(self)
        self.layoutcontainer.setContentsMargins(5, 5, 5, 5)
        self.layoutcontainer.setSpacing(10)
        self.layoutcontainer.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)

        self.scanbtn = self._create_btn(name="Custom Scan")

        self.exportbtn = self._create_btn(name="Export")

        self.helpbtn = self._create_btn(name="Help")

        self.settingbtn = self._create_btn(name="Setting")
        self.settingbtn.clicked.connect(
            lambda: setting(main_window=self.main_window).show()
        )

        self.layoutcontainer.addWidget(self.scanbtn, 1)
        self.layoutcontainer.addWidget(self.exportbtn, 1)
        self.layoutcontainer.addWidget(self.helpbtn, 1)
        self.layoutcontainer.addWidget(self.settingbtn, 1)

    def _create_btn(self, name=""):

        if not self.all_btns:
            btn = QtWidgets.QPushButton(name)
            btn.setStyleSheet(ScannerStyle.topbtnstylesheet)
            self.all_btns.append(
                {'btn_name' : name,
                    'button' : btn
                })
        else:            

            repeated = [item['btn_name'] for item in self.all_btns]
                
            if name not in repeated:

                btn = QtWidgets.QPushButton(name)
                btn.setStyleSheet(ScannerStyle.topbtnstylesheet)
                self.all_btns.append(
                    {'btn_name' : name,
                        'button' : btn
                    })
            else:

                for item in self.all_btns:
                    if item['btn_name'] == name:
                        btn = item['button']
                        break
        btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        return btn 

class fileexport(QtWidgets.QDialog):

    def __init__(self, parent=None, current=None, history=None):
        super().__init__(parent)
        self.current = current
        self.history = history
        self.selected = None
        self.setStyleSheet("""background: #F5F9FF;""")
        self.setMinimumSize(700, 350)
        self.setWindowTitle("Export Scan Result")
        self.layout()
    
    def layout(self):

        displaylayout = QtWidgets.QVBoxLayout(self)
        displaylayout.setContentsMargins(10, 10, 10, 10)
        displaylayout.setSpacing(10)
        displaylayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        title = QtWidgets.QLabel("Export Scan Result")
        title.setMaximumHeight(50)
        title.setStyleSheet("""background: #6488EA; border: 1px solid #6488EA; border-radius: 8px; color: #FFFFFF; font-size: 20px; font: bold; text-align: left; padding-left: 5px;""")
        displaylayout.addWidget(title)

        selectresult = QtWidgets.QGroupBox("Select Result")
        selectlayout = QtWidgets.QVBoxLayout()

        self.currentresult = QtWidgets.QRadioButton("Current Scan Result")
        self.currentresult.setStyleSheet(ScannerStyle.radiobtn)
        self.currentresult.setEnabled(self.current != None)
        if self.current:
            self.currentresult.setChecked(True)
            self.selected = self.current
        selectlayout.addWidget(self.currentresult)

        if self.current:
            filetitle = QtWidgets.QLabel(F"File: {os.path.basename(self.current)}")
            filetitle.setStyleSheet("""background: #6488EA; color: #FFFFFF; font-size: 12px; text-align: left;""")
            selectlayout.addWidget(filetitle)

        self.historyresults = QtWidgets.QRadioButton("History Scan Results")
        self.historyresults.setStyleSheet(ScannerStyle.radiobtn)
        self.historyresults.setEnabled(self.history != None)
        if not self.current:
            self.historyresults.setChecked(True)
        selectlayout.addWidget(self.historyresults) 

        self.historylist = QtWidgets.QComboBox()
        self.historylist.setStyleSheet(ScannerStyle.combo_all)
        self.historylist.setEnabled(True)
        if self.history:
            self._historycombo()
        selectlayout.addWidget(self.historylist)

        self.selectedlabel = QtWidgets.QLabel("Not selected yet")
        self.selectedlabel.setStyleSheet(ScannerStyle.exporttitle)
        selectlayout.addWidget(self.selectedlabel)

        selectresult.setLayout(selectlayout)
        displaylayout.addWidget(selectresult)

  
        self.currentresult.toggled.connect(self._currentchanged)
        self.historyresults.toggled.connect(self._currentchanged)
        self.historylist.currentTextChanged.connect(self._historyselected)

        formatgroup = QtWidgets.QGroupBox("Export Format")
        formatlayout = QtWidgets.QVBoxLayout()

        self.csvfile = QtWidgets.QRadioButton(".csv")
        self.csvfile.setStyleSheet(ScannerStyle.radiobtn)
        self.csvfile.setChecked(True)
        self.txtfile = QtWidgets.QRadioButton(".txt")
        self.txtfile.setStyleSheet(ScannerStyle.radiobtn)

        formatlayout.addWidget(self.csvfile)
        formatlayout.addWidget(self.txtfile)

        formatgroup.setLayout(formatlayout)
        displaylayout.addWidget(formatgroup)

        btnlayout = QtWidgets.QHBoxLayout()
        btnlayout.addStretch()

        cancelbtn = QtWidgets.QPushButton("Cancel")
        cancelbtn.setStyleSheet(ScannerStyle.btncstylesheet)
        cancelbtn.setMinimumSize(75, 40)
        cancelbtn.clicked.connect(self.reject)
        exportbtn = QtWidgets.QPushButton("Export")
        exportbtn.setStyleSheet(ScannerStyle.btnestylesheet)
        exportbtn.setMinimumSize(75, 40)
        exportbtn.clicked.connect(self._exfile)

        
        btnlayout.addWidget(exportbtn)
        btnlayout.addWidget(cancelbtn)
        displaylayout.addLayout(btnlayout)
    
    def _historycombo(self):

        self.historylist.clear()
        self.historylist.addItem("Select a history record", "header")
        if hasattr(self.history, 'all_history_records'):
            for record in self.history.all_history_records:
                filename = record.get('filename', '')
                date_info = record.get('date_info', '')
                showtxt = f"{filename} ({date_info})"

                if record.get('filepath', ''):
                    filepath = record.get('filepath', '')
                else:
                    filepath = os.path.join(f"History/{filename}.json")
                self.historylist.addItem(showtxt, filepath)
        self.historylist.model().item(0).setEnabled(False)
    
    def _currentchanged(self):

        if self.currentresult.isChecked():
            self.selected = self.current
            self.historylist.setEnabled(False)
            self._selectedlabel()
        elif self.historyresults.isChecked():
            self.historylist.setEnabled(True)
            if self.historylist.count() > 0:
                self.selected = self.historylist.currentData()
                self._selectedlabel()
            else:
                self.selected = None
    
    def _historyselected(self):

        if self.historyresults.isChecked():
            self.selected = self.historylist.currentData()
        self._selectedlabel()

    def _selectedlabel(self):

        if hasattr(self, 'selectedlabel'):
            if self.selected:
                filename = os.path.basename(self.selected)
                self.selectedlabel.setText(f"Selected: {filename}")
                self.selectedlabel.setStyleSheet(ScannerStyle.exporttitle)
            else:
                self.selectedlabel.setText(f"Not selected yet")
                self.selectedlabel.setStyleSheet(ScannerStyle.exporttitle)  

    def _exfile(self):

        try:
            valid = bool(self.selected) and os.path.exists(self.selected)
        except (TypeError, OSError) as e:
            function.logging.error(str(e))
            valid = False
        if not valid:
            function.error_msg("Error", "Please select a file or file not found!")
            return

        if self.csvfile.isChecked():
            file = "csv"
        else:
            file = "txt"

        filename = os.path.splitext(os.path.basename(self.selected))[0]
        default = f"{filename}_export.{file}"

        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Export File", default, f"{file.upper()} Files (*.{file});;All Files (*)")
        
        if not filepath:
            return
        
        with open(self.selected, 'r', encoding='utf-8') as f:
            read = json.load(f)
        if isinstance(read, list):
            read = read[0]
        
        if self.csvfile.isChecked():
            self._tocsv(read, filepath)
        else:
            self._totxt(read, filepath)
                    
        self.accept()

    def _vuln_script_entries(self, host):
        
        entries = []
        tcp = host.get("tcp", {})
        udp = host.get("udp", {})
        host_script = host.get("hostscript", [])

        if tcp:
            for port, info in tcp.items():
                if info.get("script", {}):
                    for script_id, output in info["script"].items():
                        if script_id:
                            entries.append(
                                {
                                    "Protocol": "tcp",
                                    "Port": port,
                                    "id": script_id,
                                    "output": output,
                                }
                            )
                        else:
                            entries.append(
                                {
                                    "Protocol": "tcp",
                                    "Port": port,
                                    "id": "N/A",
                                    "output": "N/A",
                                }
                            )
        if udp:
            for port, info in udp.items():
                if info.get("script", {}):
                    for script_id, output in info["script"].items():
                        if script_id:
                            entries.append(
                                {
                                    "Protocol": "udp",
                                    "Port": port,
                                    "id": script_id,
                                    "output": output,
                                }
                            )
                        else:
                            entries.append(
                                {
                                    "Protocol": "udp",
                                    "Port": port,
                                    "id": "N/A",
                                    "output": "N/A",
                                }
                            )
        if host_script:
            for row in host_script:
                if row.get("id", ""):
                    entries.append(
                        {
                            "Protocol": "N/A",
                            "Port": "N/A",
                            "id": row["id"],
                            "output": row.get("output", ""),
                        }
                    )
        return entries

    def _tocsv(self, data, path):

        protocols = ["tcp", "udp"] #Protocols
        base, ext = os.path.splitext(path)
        hostsum = f"{base}_HostSummary{ext}"
        op_port= f"{base}_OpenPorts{ext}"
        svcsum = f"{base}_ServiceSummary{ext}"
        vuln_scripts = f"{base}_VulnScripts{ext}"

        try:
            with open(hostsum, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "IP Address",
                        "Hostname",
                        "MAC Address",
                        "Vendor",
                        "Status",
                        "OS Name",
                        "OS Accuracy",
                        "Last Boot",
                        "Vulnerability Script Count",
                    ]
                )
                for ip, host in data.get("scan", {}).items():

                    hostname = host.get("hostnames", [{}])[0].get("name", "None")
                    mac = host.get("addresses", {}).get("mac", "")
                    vendor = host.get("vendor", {}).get(mac, "Unknown")
                    status = host.get("status", {}).get("state", "")

                    os_matches = host.get('osmatch', [])
                    os_name = os_matches[0].get("name", "Unknown") if os_matches else "Unknown"
                    os_accur = os_matches[0].get("accuracy", "0") if os_matches else "0"

                    last_boot = host.get("uptime", {}).get("lastboot", "Unknown")
                    vuln_entries = self._vuln_script_entries(host)
                    vuln_count = sum(
                        1 for e in vuln_entries if e.get("id") not in (None, "", "N/A")
                    )

                    writer.writerow(
                        [
                            ip,
                            hostname,
                            mac,
                            vendor,
                            status,
                            os_name,
                            os_accur,
                            last_boot,
                            vuln_count,
                        ]
                    )
            function.error_msg('Success', f'File exported to: {hostsum}')

        except Exception as e:
            function.error_msg('Fail', f'Fail to export to: {hostsum}')
            function.logging.error(msg=f'{str(e)}')

        try:
            with open(op_port, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["IP Address", "Hostname", "Port", "Protocol", "State", "Service", "Product", "Version", "Extra Info", "CPE"])
                for protocol in protocols:
                    for ip, host in data.get("scan", {}).items():
                        hostname = host.get("hostnames", [{}])[0].get("name", "None")

                        if host.get(protocol, {}):
                            for port, info in host.get(protocol, {}).items():
                                writer.writerow([
                                    ip,
                                    hostname,
                                    port,
                                    protocol,
                                    info.get("state", "Unknown"),
                                    info.get("name", "Unknown"),
                                    info.get("product", "Unknown"),
                                    info.get("version", "Unknown"),
                                    info.get("extrainfo", "None"),
                                    info.get("cpe", "None")
                                ])
            function.error_msg('Success', f'File exported to: {op_port}')

        except Exception as e:
            function.error_msg('Fail', f'Fail to export to: {op_port}')
            function.logging.error(msg=f'{str(e)}')

        try:
            with open(svcsum, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)                
                writer.writerow(["Service", "Count"])
                stat = {}
                for protocol in protocols:
                    for ip, host in data.get("scan", {}).items():
                        if host.get(protocol, {}):
                            for port, info in host.get(protocol, {}).items():
                                service = info.get('name')
                                if service != "" and service is not None:
                                    stat[service] = stat.get(service, 0) + 1
                                else:
                                    stat[port] = stat.get(service, 0) + 1
                for name, count in stat.items():
                    writer.writerow([name, count])
            function.error_msg('Success', f'File exported to: {svcsum}')

        except Exception as e:
            function.error_msg('Fail', f'Fail to export to: {svcsum}')
            function.logging.error(msg=f'{str(e)}')

        try:
            with open(vuln_scripts, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "IP Address",
                        "Hostname",
                        "Protocol",
                        "Port",
                        "Script ID",
                        "Script Output",
                    ]
                )
                for ip, host in data.get("scan", {}).items():
                    hostname = host.get("hostnames", [{}])[0].get("name", "None")
                    for entry in self._vuln_script_entries(host):
                        sid = entry.get("id", "")
                        if not sid or sid == "N/A":
                            continue
                        writer.writerow(
                            [
                                ip,
                                hostname,
                                entry.get("Protocol", ""),
                                entry.get("Port", ""),
                                sid,
                                entry.get("output", ""),
                            ]
                        )
            function.error_msg("Success", f"File exported to: {vuln_scripts}")

        except Exception as e:
            function.error_msg("Fail", f"Fail to export to: {vuln_scripts}")
            function.logging.error(msg=f"{str(e)}")

    def _totxt(self, data, path):

        protocols = ["tcp", "udp"]

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("#" * 50 + "\n")
                f.write("NMAP SCAN RESULTS\n")
                f.write("#" * 50 + "\n\n")

                nmap = data.get("nmap", {})
                f.write(f"Command: {nmap.get('command_line', 'N/A')}\n")
                f.write(f"Scan Info: {nmap.get('scaninfo', 'N/A')}\n\n")

                stats = nmap.get("scanstats", {})
                f.write(f"Time: {stats.get('timestr', 'N/A')}\n")
                f.write(f"Elapsed: {stats.get('elapsed', 'N/A')} seconds\n")
                f.write(f"Online Hosts: {stats.get('uphosts', 'N/A')}\n")
                f.write(f"Offline Hosts: {stats.get('downhosts', 'N/A')}\n")
                f.write(f"Total Hosts: {stats.get('totalhosts', 'N/A')}\n\n")

                f.write("#" * 50 + "\n")
                f.write("HOST SUMMARY\n")
                f.write("#" * 50 + "\n\n")
                f.write(
                    "IP Address\tHostname\tMAC Address\tVendor\tStatus\t"
                    "OS Name\tOS Accuracy\tLast Boot\tVulnerability Script Count\n"
                )
                for ip, host in data.get("scan", {}).items():
                    hostname = host.get("hostnames", [{}])[0].get("name", "None")
                    mac = host.get("addresses", {}).get("mac", "")
                    vendor = host.get("vendor", {}).get(mac, "Unknown")
                    status = host.get("status", {}).get("state", "")
                    os_matches = host.get("osmatch", [])
                    os_name = os_matches[0].get("name", "Unknown") if os_matches else "Unknown"
                    os_accur = os_matches[0].get("accuracy", "0") if os_matches else "0"
                    last_boot = host.get("uptime", {}).get("lastboot", "Unknown")
                    vuln_entries = self._vuln_script_entries(host)
                    vuln_count = sum(
                        1 for e in vuln_entries if e.get("id") not in (None, "", "N/A")
                    )
                    f.write(
                        f"{ip}\t{hostname}\t{mac}\t{vendor}\t{status}\t"
                        f"{os_name}\t{os_accur}\t{last_boot}\t{vuln_count}\n"
                    )
                f.write("\n")

                f.write("#" * 50 + "\n")
                f.write("OPEN PORTS\n")
                f.write("#" * 50 + "\n\n")
                f.write(
                    "IP Address\tHostname\tPort\tProtocol\tState\tService\t"
                    "Product\tVersion\tExtra Info\tCPE\n"
                )
                for protocol in protocols:
                    for ip, host in data.get("scan", {}).items():
                        hostname = host.get("hostnames", [{}])[0].get("name", "None")
                        if host.get(protocol, {}):
                            for port, info in host.get(protocol, {}).items():
                                f.write(
                                    f"{ip}\t{hostname}\t{port}\t{protocol}\t"
                                    f"{info.get('state', 'Unknown')}\t"
                                    f"{info.get('name', 'Unknown')}\t"
                                    f"{info.get('product', 'Unknown')}\t"
                                    f"{info.get('version', 'Unknown')}\t"
                                    f"{info.get('extrainfo', 'None')}\t"
                                    f"{info.get('cpe', 'None')}\n"
                                )
                f.write("\n")

                f.write("#" * 50 + "\n")
                f.write("SERVICE SUMMARY\n")
                f.write("#" * 50 + "\n\n")
                f.write("Service\tCount\n")
                stat = {}
                for protocol in protocols:
                    for ip, host in data.get("scan", {}).items():
                        if host.get(protocol, {}):
                            for port, info in host.get(protocol, {}).items():
                                service = info.get("name")
                                if service != "" and service is not None:
                                    stat[service] = stat.get(service, 0) + 1
                                else:
                                    stat[port] = stat.get(service, 0) + 1
                for name, count in stat.items():
                    f.write(f"{name}\t{count}\n")
                f.write("\n")

                f.write("#" * 50 + "\n")
                f.write("VULNERABILITY SCRIPTS\n")
                f.write("#" * 50 + "\n\n")
                for ip, host in data.get("scan", {}).items():
                    hostname = host.get("hostnames", [{}])[0].get("name", "None")
                    for entry in self._vuln_script_entries(host):
                        sid = entry.get("id", "")
                        if not sid or sid == "N/A":
                            continue
                        f.write("-" * 50 + "\n")
                        f.write(f"IP Address: {ip}\n")
                        f.write(f"Hostname: {hostname}\n")
                        f.write(f"Protocol: {entry.get('Protocol', '')}\n")
                        f.write(f"Port: {entry.get('Port', '')}\n")
                        f.write(f"Script ID: {sid}\n")
                        f.write("Script Output:\n")
                        out = entry.get("output", "") or ""
                        for line in out.splitlines():
                            f.write(f"  {line}\n")
                        if not out:
                            f.write("  (no output)\n")
                        f.write("\n")

                f.write("#" * 50 + "\n")
                f.write("HOST(S) DETAILS\n")
                f.write("#" * 50 + "\n\n")
                for ip, host in data.get("scan", {}).items():
                    f.write(f"Host: {ip}\n")
                    f.write("-" * 80 + "\n")
                    f.write(
                        f"Hostnames: {', '.join(h['name'] for h in host.get('hostnames', []))}\n"
                    )
                    f.write(f"IPv4: {host.get('addresses', {}).get('ipv4', 'N/A')}\n")
                    mac = host.get("addresses", {}).get("mac", "N/A")
                    f.write(f"MAC: {mac}\n")
                    vend = host.get("vendor", {}).get(mac, "Unknown") if mac != "N/A" else "Unknown"
                    f.write(f"Vendor: {vend}\n")
                    f.write(f"State: {host.get('status', {}).get('state', 'N/A')}\n")
                    os_matches = host.get("osmatch", [])
                    if os_matches:
                        f.write(
                            f"OS: {os_matches[0].get('name', 'Unknown')} "
                            f"(accuracy {os_matches[0].get('accuracy', '0')})\n"
                        )
                    last_boot = host.get("uptime", {}).get("lastboot")
                    if last_boot:
                        f.write(f"Last boot: {last_boot}\n")
                    vuln_entries = self._vuln_script_entries(host)
                    vuln_n = sum(
                        1 for e in vuln_entries if e.get("id") not in (None, "", "N/A")
                    )
                    f.write(f"Vulnerability script count: {vuln_n}\n\n")

                    tcp = host.get("tcp", {})
                    if tcp:
                        f.write("TCP ports:\n")
                        for port, meta in tcp.items():
                            f.write(
                                f"  Port {port}: {meta.get('state', 'N/A')} | "
                                f"{meta.get('reason', 'N/A')} | {meta.get('name', 'N/A')} | "
                                f"{meta.get('product', 'N/A')} | {meta.get('version', 'N/A')} | "
                                f"{meta.get('extrainfo', 'N/A')} | {meta.get('conf', 'N/A')} | "
                                f"{meta.get('cpe', 'N/A')}\n"
                            )
                            if meta.get("script", {}):
                                f.write(f"  Vulnerability script results (port {port}):\n")
                                for title, result in meta.get("script", {}).items():
                                    f.write(f"    {title}: {result}\n")
                        f.write("\n")

                    udp = host.get("udp", {})
                    if udp:
                        f.write("UDP ports:\n")
                        for port, meta in udp.items():
                            f.write(
                                f"  Port {port}: {meta.get('state', 'N/A')} | "
                                f"{meta.get('reason', 'N/A')} | {meta.get('name', 'N/A')} | "
                                f"{meta.get('product', 'N/A')} | {meta.get('version', 'N/A')} | "
                                f"{meta.get('extrainfo', 'N/A')} | {meta.get('conf', 'N/A')} | "
                                f"{meta.get('cpe', 'N/A')}\n"
                            )
                            if meta.get("script", {}):
                                f.write(f"  Vulnerability script results (port {port}):\n")
                                for title, result in meta.get("script", {}).items():
                                    f.write(f"    {title}: {result}\n")
                        f.write("\n")

                    hostscript = host.get("hostscript", [])
                    if hostscript:
                        f.write("Host script results:\n")
                        for r in hostscript:
                            f.write(f"  ID: {r.get('id', 'N/A')}\n")
                            f.write(f"  Output: {r.get('output', '')}\n")
                        f.write("\n")

                    f.write("\n")

            function.error_msg("Success", f"File exported to: {path}")

        except Exception as e:
            function.error_msg("Fail", f"Fail to export to: {path}")
            function.logging.error(msg=f"{str(e)}")

    def _loadjson(self, content):

        rows = []
        nmap = content.get("nmap", {})
        stats = nmap.get("scanstats", {})

        rows.extend([
            ["Nmap command", nmap.get("command_line", "")],
            ["Scan info", nmap.get('scaninfo', "")],
            ["Time", stats.get("timestr", "")],
            ["Elapsed (s)", stats.get("elapsed", "")],
            ["Online hosts", stats.get("uphosts", "")],
            ["Offline hosts", stats.get("downhosts", "")],
            ["Total hosts", stats.get("totalhosts", "")],
        ])

        rows.append(["", ""])

        for ip, host in content.get("scan", {}).items():
            rows.append([f"Host {ip}", ""])
            rows.append(["Hostnames", ", ".join(h["name"] for h in host.get("hostnames", []))])
            rows.append(["IPv4", host.get("addresses", {}).get("ipv4", "")])
            rows.append(["MAC", host.get("addresses", {}).get("mac", "")])
            rows.append(["Vendor", ", ".join(host.get("vendor", {}).values())])
            rows.append(["State", host.get("status", {}).get("state", "")])
            rows.append(["Reason", host.get("status", {}).get("reason", "")])

            uptime = host.get("uptime", {})
            if uptime:
                rows.append(["Uptime (s)", uptime.get("seconds", "")])
                rows.append(["Last boot", uptime.get("lastboot", "")])

            tcp = host.get("tcp", {})
            if tcp:
                rows.append(["Ports", "state | name | product | version"])
                for port, meta in tcp.items():
                    rows.append([
                        f"  {port}",
                        f"{meta.get('state', '')} | {meta.get('name', '')} | "
                        f"{meta.get('product', '')} | {meta.get('version', '')}"
                    ])

            portused = host.get("portused", [])
            if portused:
                rows.append(["Port summary", json.dumps(portused, ensure_ascii=False)])

            osmatch = host.get("osmatch", [])
            if osmatch:
                rows.append(["OS matches", json.dumps(osmatch, ensure_ascii=False)])

            rows.append(["", ""])

        return rows

class setting(QtWidgets.QDialog):

    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self._main_window = main_window
        self.setStyleSheet("""background: #F5F9FF;""")
        self.setWindowTitle("Setting")
        self.layout()

    def layout(self):

        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.mainlayout.setContentsMargins(10, 10, 10, 10)
        self.mainlayout.setSpacing(10)

        self.displaylayout = QtWidgets.QHBoxLayout()
        self.displaylayout.setContentsMargins(0, 0, 0, 0)
        self.displaylayout.setSpacing(10)

        self.options()
        self.mainlayout.addLayout(self.displaylayout)

        btnlayout = QtWidgets.QHBoxLayout()
        btnlayout.addStretch()

        self.restart_btn = QtWidgets.QPushButton("Restart")
        self.restart_btn.setStyleSheet(ScannerStyle.resbtnstylesheet)
        self.restart_btn.enterEvent = lambda event: self.show_description("Restart to apply the changes.")
        self.restart_btn.leaveEvent = lambda event: self.init_description()
        self.restart_btn.setMinimumSize(75, 40)
        self.restart_btn.clicked.connect(lambda: self._restart())

        self.okbtn = QtWidgets.QPushButton("OK")
        self.okbtn.clicked.connect(self.accept)
        self.okbtn.setStyleSheet(ScannerStyle.btnestylesheet)
        self.okbtn.setMinimumSize(75, 40)
        
        self.closebtn = QtWidgets.QPushButton("Close")
        self.closebtn.clicked.connect(self.reject)
        self.closebtn.setStyleSheet(ScannerStyle.btncstylesheet)
        self.closebtn.setMinimumSize(75, 40)

        btnlayout.addWidget(self.restart_btn)
        btnlayout.addWidget(self.okbtn)
        btnlayout.addWidget(self.closebtn)
        self.mainlayout.addLayout(btnlayout)

    def options(self):
        
        self.options_group = QtWidgets.QButtonGroup(self)
        container = QtWidgets.QWidget(self)
        container.setMinimumWidth(300)
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(0)

        onboarding_btn = QtWidgets.QPushButton("Onboarding")
        onboarding_btn.setStyleSheet(ScannerStyle.setting)
        onboarding_btn.enterEvent = lambda event: self.show_description("You can see the onboarding guide.")
        onboarding_btn.leaveEvent = lambda event: self.init_description()
        onboarding_btn.clicked.connect(self._open_onboarding)
        self.options_group.addButton(onboarding_btn, 0)

        nmap_path_btn = QtWidgets.QPushButton("Select Nmap Path")
        nmap_path_btn.setStyleSheet(ScannerStyle.setting)
        nmap_path_btn.enterEvent = lambda event: self.show_description("You can re-select your Nmap.exe path.")
        nmap_path_btn.leaveEvent = lambda event: self.init_description()
        nmap_path_btn.clicked.connect(lambda: selectnmap(warning=None))
        self.options_group.addButton(nmap_path_btn, 1)

        nmap_script_btn = QtWidgets.QPushButton("Select Nmap Script Path")
        nmap_script_btn.setStyleSheet(ScannerStyle.setting)
        nmap_script_btn.enterEvent = lambda event: self.show_description("You can re-select your Nmap script path.")
        nmap_script_btn.leaveEvent = lambda event: self.init_description()
        nmap_script_btn.clicked.connect(lambda: selectscriptfolder(warning=None))
        self.options_group.addButton(nmap_script_btn, 2)

        API_btn = QtWidgets.QPushButton("Enter Vulners API Key")
        API_btn.setStyleSheet(ScannerStyle.setting)
        API_btn.enterEvent = lambda event: self.show_description("You can change your vulners database API key.")
        API_btn.leaveEvent = lambda event: self.init_description()
        API_btn.clicked.connect(lambda: enterapi(api_type='vulners_api'))
        self.options_group.addButton(API_btn, 3)

        API2_btn = QtWidgets.QPushButton("Enter OpenRoute API Key")
        API2_btn.setStyleSheet(ScannerStyle.setting)
        API2_btn.enterEvent = lambda event: self.show_description("You can enter your OpenRoute API key.")
        API2_btn.leaveEvent = lambda event: self.init_description()
        API2_btn.clicked.connect(lambda: enterapi(api_type='openroute_api'))
        self.options_group.addButton(API2_btn, 4)

        init_desc = QtWidgets.QWidget()
        init_desc.setStyleSheet("""font-size: 16px;""")
        init_desc.setMinimumSize(500, 200)
        init_desc_layout = QtWidgets.QVBoxLayout(init_desc)
        desc = QtWidgets.QGroupBox("Description")
        desc_layout = QtWidgets.QVBoxLayout(desc)
        desc_layout.setContentsMargins(10, 10, 10, 10)
        desc_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.desc_content = QtWidgets.QLabel("Hover on a button to see the description.")
        self.desc_content.setWordWrap(True)
        desc_layout.addWidget(self.desc_content)
        init_desc_layout.addWidget(desc)

        layout.addWidget(nmap_path_btn)
        layout.addWidget(nmap_script_btn)
        layout.addWidget(API_btn)
        layout.addWidget(API2_btn)
        layout.addWidget(onboarding_btn)
        self.displaylayout.addWidget(container)
        self.displaylayout.addWidget(init_desc)

    def show_description(self, description=""):   
        self.desc_content.setText(description)
    
    def init_description(self):
        self.desc_content.setText("Hover on a button to see the description.")

    def _open_onboarding(self):
        main = self._main_window
        if main is None and self.parent():
            main = self.parent().window()
        self.reject()
        if main is not None:
            QtCore.QTimer.singleShot(0, lambda: program_onboarding(main))

    def _restart(self):
        restart = QtWidgets.QMessageBox.question(self, "Restart Application", "Are you sure you want to restart the application?")
        if restart == QtWidgets.QMessageBox.StandardButton.Yes:
            function.restart()

