import re, os
from PyQt6 import QtWidgets, QtCore
from Widgets import ScannerStyle, function

class ScriptSelector(QtWidgets.QDialog):

    applied = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.selected_script = ""
        self.script_map = {}
        self.btns = []
        self.setMinimumSize(800, 600)
        self.setStyleSheet(
            """
            QDialog {
                background: #F5F9FF;
            }
            """
        )
        self.setWindowTitle("Script Selection")
        self.layout()
        
    
    def layout(self):

        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.mainlayout.setContentsMargins(10, 10, 10, 10)
        self.mainlayout.setSpacing(10)

        title = QtWidgets.QLabel("Script Selection")
        title.setStyleSheet(ScannerStyle.hislabelstylesheet)
        self.displaylayout = QtWidgets.QHBoxLayout()
        self.displaylayout.setContentsMargins(0, 0, 0, 0)
        self.displaylayout.setSpacing(10)

        self.loadscript_content()

        btnlayout = QtWidgets.QHBoxLayout()
        btnlayout.addStretch()

        self.applybtn = QtWidgets.QPushButton("Apply")
        self.applybtn.setMinimumSize(75, 40)
        self.applybtn.setStyleSheet(ScannerStyle.btnestylesheet)
        self.closebtn = QtWidgets.QPushButton("Close")
        self.closebtn.setMinimumSize(75, 40)
        self.closebtn.setStyleSheet(ScannerStyle.btncstylesheet)

        self.applybtn.clicked.connect(self.apply_selection)
        self.closebtn.clicked.connect(self.reject)

        btnlayout.addWidget(self.applybtn)
        btnlayout.addWidget(self.closebtn)

        self.mainlayout.addWidget(title)
        self.mainlayout.addLayout(self.displaylayout)
        self.mainlayout.addLayout(btnlayout)

    def loadscript_content(self):

        scriptgroup = QtWidgets.QGroupBox("Scripts")
        scriptlayout = QtWidgets.QVBoxLayout(scriptgroup)

        scrollarea = QtWidgets.QScrollArea()
        scrollarea.setWidgetResizable(True)
        scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_container = QtWidgets.QWidget()
        scroll_container.setStyleSheet("""
            QWidget {
                background: #F5F9FF;
                border: none;
            }
        """)
        scroll_layout = QtWidgets.QVBoxLayout(scroll_container)
        scroll_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)
        scroll_container.setLayout(scroll_layout)

        self.inputfield = QtWidgets.QLineEdit()
        self.inputfield.setPlaceholderText("Search for script")
        self.inputfield.setStyleSheet('border: 2px solid #6488EA; border-radius: 8px; padding-left: 5px;')
        self.inputfield.textChanged.connect(self._search)

        self.script_stack = QtWidgets.QStackedWidget()

        self.scriptbtn_group = QtWidgets.QButtonGroup(self)
        self.scriptbtn_group.setExclusive(True)

        from Widgets import ConfigLoader
        loader = ConfigLoader.getscript()
        listed_script = sorted(os.listdir(loader))

        for index , script in enumerate(listed_script):
            path = os.path.join(loader, script).replace('/', '\\')
            
            if not os.path.isfile(path):
                continue
            
            if not path.lower().endswith('.nse'):
                continue

            desc_dict, usage_dict, args_dict = self._parse_script(path)
            usage_lines = [v for _, v in sorted(usage_dict.items())]
            self.script_map[index] = usage_lines

            scriptbtn = QtWidgets.QRadioButton(script)
            scriptbtn.setStyleSheet(ScannerStyle.radiobtn)
            self.btns.append({
                                "btn" : scriptbtn,
                                "name" : script
                            })
            self.scriptbtn_group.addButton(scriptbtn, index )
            scroll_layout.addWidget(scriptbtn)

            content_widget = self.display_content(desc_dict, usage_dict, args_dict)
            self.script_stack.addWidget(content_widget)

            scriptbtn.toggled.connect(
                lambda checked, i=index : self.script_stack.setCurrentIndex(i) if checked else None
            )

        scrollarea.setWidget(scroll_container)
        scriptlayout.addWidget(scrollarea)
        scriptlayout.addWidget(self.inputfield)

        self.displaylayout.addWidget(scriptgroup, 1)
        self.displaylayout.addWidget(self.script_stack, 3)

        if self.scriptbtn_group.buttons():
            self.scriptbtn_group.buttons()[0].setChecked(True)

    def _parse_script(self, path):
        description = {}
        usage = {}
        args = {}

        count_args = 1
        count_usage = 1

        def lua(line):
            s = line.lstrip()
            if not s.startswith("--"):
                return None
            return s[2:].lstrip()

        def is_tag(body):
            return bool(body and re.match(r"@\w+", body))

        def collect_usage_block(start_i):
            lines_out = []
            j = start_i + 1
            while j < len(data):
                body = lua(data[j])
                if body is None:
                    break
                if is_tag(body):
                    break
                lines_out.append(body)
                j += 1
            return "\n".join(lines_out).strip(), j

        def parser_args(body):
            m = re.match(r"@args\s+(\S+)\s*(.*)", body, re.IGNORECASE)
            if not m:
                return None, None
            return m.group(1).strip(), m.group(2).strip()

        def collect_args_block(start_i):
            first = lua(data[start_i])
            if not first:
                return None, start_i + 1
            name, rest = parser_args(first)
            if not name:
                return None, start_i + 1
            parts = []
            if rest:
                parts.append(rest)
            j = start_i + 1
            while j < len(data):
                body = lua(data[j])
                if body is None:
                    break
                if is_tag(body):
                    break
                if body == "":
                    break
                parts.append(body)
                j += 1
            desc = "\n".join(parts).strip()
            full = f"{name}\n{desc}" if desc else name
            return full, j
        try:
            with open(path, "r", encoding="utf-8") as s:
                data = s.readlines()
        except PermissionError as e:
           function.logging.error(f"Permission error: {str(e)}")
           function.error_msg("Permission Error", "Please check the script folder and try again.")
           return None, None, None
        except Exception as e:
           function.logging.error(f"Error parsing script: {str(e)}")
           return None, None, None

        start_index = None
        end_index = None
        for i, line in enumerate(data):
            if "[[" in line and start_index is None:
                start_index = i + 1
            elif "]]" in line and start_index is not None:
                end_index = i
                break

        if start_index is not None and end_index is not None and end_index > start_index:
            description["description"] = data[start_index:end_index]
        else:
            description["description"] = ["No description available.\n"]

        i = 0
        while i < len(data):
            body = lua(data[i])
            if body:
                if re.match(r"@usage\b", body, re.IGNORECASE):
                    block, next_i = collect_usage_block(i)
                    if block:
                        usage[f"usage{count_usage}"] = block
                        count_usage += 1
                    i = next_i
                    continue
                if re.match(r"@args\b", body, re.IGNORECASE):
                    full, next_i = collect_args_block(i)
                    if full:
                        args[f"arg{count_args}"] = full
                        count_args += 1
                    i = next_i
                    continue
            i += 1

        return description, usage, args

    def apply_selection(self):

        checkedbtn_id = self.scriptbtn_group.checkedId()

        if checkedbtn_id < 0:
            function.error_msg("Empty Script Error", "Please select a script!")
            return
        
        usage = self.script_map.get(checkedbtn_id, [])
        if usage:
            self.selected_script = usage[0].strip("\n")
        else:
            self.selected_script = None
        
        self.applied.emit(self.selected_script)
        self.accept()

    def display_content(self, dict_desc, dict_usage, dict_args):

        try:
            if isinstance(dict_desc, dict) and isinstance(dict_usage, dict) and isinstance(dict_args, dict):

                maincontainer = QtWidgets.QWidget()
                mainlayout = QtWidgets.QVBoxLayout(maincontainer)

                desc = QtWidgets.QGroupBox("Description")
                desclayout = QtWidgets.QVBoxLayout(desc)

                usage = QtWidgets.QGroupBox("Usage")
                usagelayout = QtWidgets.QVBoxLayout(usage)

                arg = QtWidgets.QGroupBox("Arguments")
                arglayout = QtWidgets.QVBoxLayout(arg)

                content = QtWidgets.QPlainTextEdit()
                content.setReadOnly(True)
                description_text = "".join(dict_desc.get("description", ["No description available."]))
                content.setPlainText(description_text)

                content_usage = QtWidgets.QPlainTextEdit()
                content_usage.setReadOnly(True)
                usage_lines = [v for _, v in sorted(dict_usage.items())]
                content_usage.setPlainText("\n".join(usage_lines) if usage_lines else "No usage found.")

                content_arg = QtWidgets.QPlainTextEdit()
                content_arg.setReadOnly(True)
                arg_lines = [v for _, v in sorted(dict_args.items())]
                content_arg.setPlainText("\n".join(arg_lines) if arg_lines else "No arguments found.")

                desclayout.addWidget(content)
                usagelayout.addWidget(content_usage)
                arglayout.addWidget(content_arg)

                mainlayout.addWidget(desc)
                mainlayout.addWidget(usage)
                mainlayout.addWidget(arg)

                return maincontainer

            else:
                function.logging.error("Data type error!")
                return QtWidgets.QWidget()

        except Exception as e:
            function.logging.error(f"{str(e)}")
            return QtWidgets.QWidget()
        
    def _search(self):

        search_script = self.inputfield.text()
        search_script = search_script.lower().strip()

        for info in self.btns:

            btn = info["btn"]
            script = info["name"]

            if (search_script in script.lower()):
                btn.setVisible(True)
            else:
                btn.setVisible(False)


