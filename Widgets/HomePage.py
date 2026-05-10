from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QThread, pyqtSignal
from Widgets import ScannerStyle, function
import vulners, time, requests, calendar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
from bs4 import BeautifulSoup


class Worker(QThread):

    finished = pyqtSignal(object)

    def __init__(self, api, query="", limit = 10):
        super().__init__()
        self.api = api
        self.query = query
        self.limit = limit
    
    def run(self):
        try:
            vulners_api = vulners.VulnersApi(api_key=self.api)
            if self.query:
                result = vulners_api.search.search_bulletins_all(
                    self.query,
                    limit = self.limit,
                    fields=["published", "title", "description", "cvelist", "cvss", "type"]
                )
            else:
                result = vulners_api.search.search_bulletins_all(
                    "order:published",
                    limit = self.limit,
                    fields=["published", "title", "description", "cvelist", "cvss", "type"]
                )

            self.finished.emit(result)
        except Exception as e:
            function.logging.error(f"{e}")
            self.finished.emit(None)

class BS4_Worker(QThread):

    finished = pyqtSignal(object, list)
    
    def __init__(self, url, page, month, year):
        super().__init__()
        self.url = url
        self.page = str(page)
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"}
        self.month = str(month)
        self.year = str(year)
        self.data = []
        self.list_years = None
        self.MONTHS = {
                        "January": 1, "February": 2, "March": 3, "April": 4,
                        "May": 5, "June": 6, "July": 7, "August": 8,
                        "September": 9, "October": 10, "November": 11, "December": 12
                    }
        
    def run(self):
        try:
            
            found = False
            current_page = self.page
            while True:
                response = requests.get(self.url+current_page, headers = self.header)
                if response.status_code == 200:
                    response.encoding = "utf-8"
                    soup = BeautifulSoup(response.text, "html.parser")
                    total_page = soup.find("span", class_="total_page").get_text()
                    table = soup.find("div", class_="view-table")
                    date = table.find_all(class_="view-col-1")
                    if self.list_years is None:
                        self.list_years = []
                        archive_list = soup.find("div", class_="archive_list")
                        get_year = archive_list.find_all(class_="ex_li")
                        for each in get_year:
                            year = each.find("a").get_text()
                            self.list_years.append(year)
                        
                    if date:
                        for div in date:
                            parser_date = div.find("span").get_text().strip("\t")
                            parser_date = parser_date.split("-")
                            if parser_date[1] == self.month and parser_date[2] == self.year:
                                self.data.append({
                                    "date":  div.find("span").get_text().strip("\t"),
                                    "uri": div.find("a").get("href"),
                                    "title": div.find("a").get_text()
                                })
                                found = True
                                
                    if (int(self.MONTHS[self.month]) <= int(self.MONTHS[parser_date[1]]) and int(self.year) == int(parser_date[2])) or not found:
                        if int(current_page) <= int(total_page):
                            current_page = str(int(current_page)+1)
                            time.sleep(0.5)
                            continue
                        else:
                            function.logging.error(f'End of page: {current_page}/{total_page}. Cannot find the data in {self.month}/{self.year}')
                            break
                    else:
                        break
                else:
                    function.logging.error(f"HTTP error: {response.status_code}")

            self.finished.emit(self.data, self.list_years)

        except Exception as e:
            function.logging.error(f"Error fetching from website: {str(e)}.")
            self.finished.emit([], [])

class BS4_Search_Worker(QThread):

    finished = pyqtSignal(object, list)
    
    def __init__(self, url, page, frommon, fromyr, tomon, toyr):
        super().__init__()
        self.url = url
        self.page = page
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"}
        self.frommon, self.fromyr, self.tomon, self.toyr = int(frommon), int(fromyr), int(tomon), int(toyr)
        self.today = calendar.monthrange(self.toyr, self.tomon)[1]
        self.data = []
        self.list_years = []
        
    def run(self):

        try:
            from_date = "cert_fromdate="
            fromday = 1
            to_date = "cert_todate="
            current_page = str(self.page)

            while True:
                url = f"{self.url}{from_date}{fromday:02d}-{self.frommon:02d}-{self.fromyr}&{to_date}{self.today:02d}-{self.tomon:02d}-{self.toyr}&page={current_page}"
                response = requests.get(url, headers=self.header)
                if response.status_code == 200:
                    response.encoding = "utf-8"
                    soup = BeautifulSoup(response.text, "html.parser")
                    total_page = soup.find("span", class_="total_page").get_text()
                    table = soup.find("div", class_="view-table")
                    date = table.find_all(class_="view-col-1")

                    if date:
                        for div in date:
                            parser_date = div.find("span").get_text().strip("\t")
                            parser_date = parser_date.split("-")
                            self.data.append({
                                "date":  div.find("span").get_text().strip("\t"),
                                "uri": div.find("a").get("href"),
                                "title": div.find("a").get_text()
                            })

                        if int(current_page) < int(total_page):
                            current_page = str(int(current_page)+1)
                            time.sleep(0.5)
                            continue
                        else:
                            function.logging.error(f'End of page: {current_page}/{total_page}. Cannot find the data from {self.frommon}/{self.fromyr} to {self.tomon}/{self.toyr}.')
                            break
                    else:
                        break
                else:
                    function.logging.error(f"HTTP error: {response.status_code}")
            self.finished.emit(self.data, self.list_years)

        except Exception as e:
            function.logging.error(f"Error fetching from website: {str(e)}.")
            self.finished.emit([], [])
        
class VulDashboard(QtWidgets.QWidget):

    def __init__(self, api):
        super().__init__()
        self.api = api
        self.worker = None 
        self.bs4worker = None
        self.results = None
        self.graphlayout = None  
        self.year = None
        self.search_alerts_builder = None
        self.layout()
        self.query_selector()
        self._run()
        self.latest_worker = self._run_query(query="order:cvss.score cvss.score:[6 TO 10]", limit=10, connect_finish1=self._store_result, connect_finish2=self.latestvuln)
        self.win_worker = self._run_query(query="Windows 11 AND bulletinFamily:microsoft  type:mscve order:published ", limit=5, connect_finish1=self._windows_vuln)
        self.filter_list.currentTextChanged.connect(self._plot_graph_filter)
        self.filter_list_win.currentTextChanged.connect(self._windows_vuln_filter)
        self._run_bs4(*self._today())

    def _run(self):

        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.worker = Worker(self.api, limit=10)
        self.worker.finished.connect(self._loadresult)
        self.worker.start()
    
    def _run_query(self, query, limit, connect_finish1=None, connect_finish2=None):
       
        worker = Worker(self.api, query=query, limit=limit)
        if connect_finish1 is not None:
            worker.finished.connect(connect_finish1)
        if connect_finish2 is not None:
            worker.finished.connect(connect_finish2)
        worker.start()
        return worker
    
    def _run_bs4(self, month="February", year = 2026):

        if self.bs4worker and self.bs4worker.isRunning():
            self.bs4worker.quit()
            self.bs4worker.wait()

        url = "https://www.govcert.gov.hk/en/alerts.php?page="
        self.bs4worker = BS4_Worker(url, 1, month, year)
        self.bs4worker.finished.connect(self._bs4_result)
        self.bs4worker.finished.connect(lambda *_: setattr(self, "bs4worker", None))
        self.bs4worker.finished.connect(self.bs4worker.deleteLater)
        self.bs4worker.start()
    
    def _run_bs4_search(self):

        if self.bs4worker and self.bs4worker.isRunning():
            self.bs4worker.quit()
            self.bs4worker.wait()
        
        url = "https://www.govcert.gov.hk/en/alerts.php?"
        frommon, fromyr, tomon, toyr = str(self.cert_fromdate_mon.currentText()), str(self.cert_fromdate_yr.currentText()), str(self.cert_todate_mon.currentText()), str(self.cert_todate_yr.currentText())
        self.bs4worker = BS4_Search_Worker(url, 1, frommon, fromyr, tomon, toyr)
        self.bs4worker.finished.connect(self._bs4_result)
        self.bs4worker.finished.connect(lambda *_: setattr(self, "bs4worker", None))
        self.bs4worker.finished.connect(self.bs4worker.deleteLater)
        self.bs4worker.start()
        
    def _bs4_result(self, data, year):

        if not data:
            while self.hklayout.count() > 0:
                widget = self.hklayout.takeAt(0)
                if widget.widget():
                    widget.widget().deleteLater()
            msg = QtWidgets.QLabel("Error fetching from website")
            self.hklayout.addWidget(msg)
            return
        else:
            if self.year is None:
                self.year = year
            while self.hklayout.count() >= 1:
                widget = self.hklayout.takeAt(0)
                if widget.widget():
                    widget.widget().deleteLater()
            table = QtWidgets.QTableWidget()
            table.setStyleSheet(ScannerStyle.tablestyle)
            header = ["Date", "Title"]
            table.setColumnCount(len(header))
            table.setRowCount(len(data))
            table.setHorizontalHeaderLabels(header)
            for row, result in enumerate(data):
                table.setItem(row, 0, QtWidgets.QTableWidgetItem(result["date"]))
                table.setItem(row, 1, QtWidgets.QTableWidgetItem(result["title"]))

        def _open_url(row, col):

            url = "https://www.govcert.gov.hk/en/"
            if col == 1:
                if row < len(data) and "uri" in data[row]:
                    uri = data[row]["uri"]
                    link = QtCore.QUrl(url + uri)
                    QtGui.QDesktopServices.openUrl(link)

        table.cellClicked.connect(_open_url)

        table.horizontalHeader().setVisible(True)
        table.verticalHeader().setVisible(False)
        table.setCornerButtonEnabled(False)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setMinimumHeight(40)
        table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        table.setMinimumHeight(75)
        
        self.hklayout.addWidget(table)
        if self.search_alerts_builder is None:
            self.search_alerts_builder = self.hklayout.addWidget(self._search_alerts_builder())


    def _search_alerts_builder(self):

        if isinstance(self.year, list):

            years = ["YEAR"] + self.year
            months = ["MONTH", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
            self.cert_fromdate_yr = QtWidgets.QComboBox()
            self.cert_fromdate_mon= QtWidgets.QComboBox()
            self.cert_todate_yr = QtWidgets.QComboBox()
            self.cert_todate_mon = QtWidgets.QComboBox()

            self.cert_fromdate_yr.addItems(years)
            self.cert_todate_yr.addItems(years)
            self.cert_fromdate_mon.addItems(months)
            self.cert_todate_mon.addItems(months)
            self.cert_fromdate_yr.currentTextChanged.connect(self._disable_options_yr)
            self.cert_fromdate_mon.currentTextChanged.connect(self._disable_options_mon)

            self.cert_fromdate_yr.model().item(0).setEnabled(False)
            self.cert_fromdate_mon.model().item(0).setEnabled(False)
            self.cert_todate_yr.model().item(0).setEnabled(False)
            self.cert_todate_mon.model().item(0).setEnabled(False)

            fromLabel = QtWidgets.QLabel("From")
            toLabel = QtWidgets.QLabel("To")
            container = QtWidgets.QWidget()
            clrbtn = QtWidgets.QPushButton("Clear")
            clrbtn.setStyleSheet(ScannerStyle.btncstylesheet)
            clrbtn.clicked.connect(self._clear_all_date)
            searchbtn = QtWidgets.QPushButton("Search")
            searchbtn.clicked.connect(self._run_bs4_search)
            searchbtn.setStyleSheet(ScannerStyle.btnestylesheet)
            layout = QtWidgets.QHBoxLayout(container)
            layout.addWidget(fromLabel)
            layout.addWidget(self.cert_fromdate_mon)
            layout.addWidget(self.cert_fromdate_yr)
            layout.addWidget(toLabel)
            layout.addWidget(self.cert_todate_mon)
            layout.addWidget(self.cert_todate_yr)
            layout.addWidget(searchbtn)
            layout.addWidget(clrbtn)

            return container
    
    def _disable_options_yr(self):

        year = int(self.cert_fromdate_yr.currentText())

        model = self.cert_todate_yr.model()
        for i in range(self.cert_todate_yr.count()):
            txt = self.cert_todate_yr.itemText(i)
            item = model.item(i)
            if txt.isdigit():
                if int(txt) < year:
                    item.setEnabled(False)
                else:
                    item.setEnabled(True)
    
    def _disable_options_mon(self):

        month = int(self.cert_fromdate_mon.currentText())

        model = self.cert_todate_mon.model()
        for i in range(self.cert_todate_mon.count()):
            txt = self.cert_todate_mon.itemText(i)
            item = model.item(i)
            if txt.isdigit():
                if int(txt) < month:
                    item.setEnabled(False)
                else:
                    item.setEnabled(True)

    def _clear_all_date(self):

        self.cert_fromdate_yr.setCurrentIndex(0)
        self.cert_fromdate_mon.setCurrentIndex(0)
        self.cert_todate_yr.setCurrentIndex(0)
        self.cert_todate_mon.setCurrentIndex(0)

    def _today(self):

        today = datetime.today().strftime("%B-%Y")
        today = today.split("-")
        return today[0], today[1]

    def _store_result(self, results):
        self.results = results

    def _loadresult(self, results):

        if not results:
            msg = QtWidgets.QLabel("Error fetching from database")
            self.newslayout.addWidget(msg)
            function.logging.error("Error fetching from database")
        else:
            while self.newslayout.count():
                widget = self.newslayout.takeAt(0)
                if widget.widget():
                    widget.widget().deleteLater()
            table = QtWidgets.QTableWidget()
            table.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
            table.setStyleSheet(ScannerStyle.tablestyle)
            header = ["Type", "Title", "Published", "CVSS"]
            table.setColumnCount(len(header))
            table.setHorizontalHeaderLabels(header)
            table.setRowCount(len(results))
            self._news_table_results = list(results)

            def _cell(val):
                if val is None:
                    return "Unknown"
                return str(val)

            for row, result in enumerate(results):
                cvss = result.get("cvss") or {}

                score = cvss.get("score", "Unknown")
                if score < 4:
                    color = QtGui.QColor("#6FC276")
                elif score < 7:
                    color = QtGui.QColor("#FFF49B")
                elif score < 9:
                    color = QtGui.QColor("#ECAA1A")
                else:
                    color = QtGui.QColor("#FF2C2C")
                table.setItem(row, 0, QtWidgets.QTableWidgetItem(_cell(result.get("type"))))
                table.setItem(row, 1, QtWidgets.QTableWidgetItem(_cell(result.get("title"))))
                table.setItem(row, 2, QtWidgets.QTableWidgetItem(_cell(result.get("published"))))
                table.setItem(row, 3, QtWidgets.QTableWidgetItem(_cell(score)))
                table.item(row, 3).setBackground(color)

            table.horizontalHeader().setVisible(True)
            table.verticalHeader().setVisible(False)
            table.setCornerButtonEnabled(False)
            table.setAlternatingRowColors(True)
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setMinimumHeight(40)
            table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            table.resizeColumnsToContents()
            table.resizeRowsToContents()

            table.cellClicked.connect(self._on_clicked_row)
            self.newslayout.addWidget(table)

    def _on_clicked_row(self, row, col):
        if not getattr(self, "_news_table_results", None):
            return
        if row < 0 or row >= len(self._news_table_results):
            return
        detail = self._news_table_results[row].get("description", "Unknown")
        self._check_detail(detail)

    def _check_detail(self, content):

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Detail")
        dialog.setMinimumSize(800, 100)
        dialog.setStyleSheet("""
                                QWidget {
                                    background: #F5F9FF;
                                }
                            """)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        scrollarea = QtWidgets.QScrollArea()
        scrollarea.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        scrollarea.setStyleSheet(ScannerStyle.comscrollstylesheet)
        scrollarea.setWidgetResizable(True)
        label = QtWidgets.QLabel("Detail")
        label.setStyleSheet(ScannerStyle.hislabelstylesheet)
        content = QtWidgets.QPlainTextEdit(content)
        content.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        content.setReadOnly(True)
        content.setStyleSheet("font-size: 14px; font-weight: bold;")
        closebtn = QtWidgets.QPushButton("Close")
        closebtn.setStyleSheet(ScannerStyle.btncstylesheet)
        closebtn.clicked.connect(dialog.close)

        layout.addWidget(label)
        scrollarea.setWidget(content)
        layout.addWidget(scrollarea)
        layout.addWidget(closebtn)
        dialog.setLayout(layout)
        dialog.exec()

    def layout(self):

        self.layoutcontainer = QtWidgets.QGridLayout(self)
        self.layoutcontainer.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.searchcontainer = QtWidgets.QWidget()
        self.setStyleSheet("background:  #F5F9FF;")
        self.searchlayout = QtWidgets.QVBoxLayout(self.searchcontainer)
        self.search_label = QtWidgets.QLabel("Search From Database")
        self.search_label.setStyleSheet(ScannerStyle.hislabelstylesheet)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("You may type a query to search from the vulnerability database.")
        self.search.setStyleSheet('border: 2px solid #6488EA; border-radius: 8px; padding-left: 5px; background: #F4F9FF;')
        self.search.setFixedHeight(30)
        self.search.setMinimumWidth(90)
        self.search.returnPressed.connect(self._search_query)
        self.searchlayout.setSpacing(8)
        self.searchlayout.setContentsMargins(0, 0, 0, 0)
        self.searchlayout.addWidget(self.search_label)
        self.searchlayout.addWidget(self.search)

        self.newscontainer = QtWidgets.QWidget()
        self.newscontainer.setStyleSheet("""background: #F5F9FF;""")
        self.newslayout = QtWidgets.QVBoxLayout(self.newscontainer)
        self.newslayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.hkcontainer = QtWidgets.QWidget()
        self.hkcontainer.setStyleSheet("""background: #F5F9FF;""")
        self.hklayout = QtWidgets.QVBoxLayout(self.hkcontainer)
        self.hklayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        message_hk = QtWidgets.QLabel("Loading Data")
        self.hklayout.addWidget(message_hk)

        self.latestcontainer = QtWidgets.QWidget()
        self.latestcontainer.setStyleSheet("""background: #F5F9FF;""")
        self.latestlayout = QtWidgets.QVBoxLayout(self.latestcontainer)
        self.wincontainer = QtWidgets.QWidget()
        self.wincontainer.setStyleSheet("""background: #F5F9FF;""")
        self.winlayout = QtWidgets.QVBoxLayout(self.wincontainer)
        self.winlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.hometitle = QtWidgets.QLabel("Latest Vulnerabilities")
        self.hometitle.setStyleSheet(ScannerStyle.hislabelstylesheet)
        self.scrollarea_news = QtWidgets.QScrollArea()
        self.scrollarea_news.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.scrollarea_news.setStyleSheet(ScannerStyle.scrollstyle)
        self.scrollarea_news.setWidgetResizable(True)
        self.scrollarea_news.setWidget(self.newscontainer)

        self.hktitle = QtWidgets.QLabel("Hong Kong Security Alerts")
        self.hktitle.setStyleSheet(ScannerStyle.hislabelstylesheet)
        self.scrollarea_hk = QtWidgets.QScrollArea()
        self.scrollarea_hk.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.scrollarea_hk.setStyleSheet(ScannerStyle.scrollstyle)
        self.scrollarea_hk.setWidgetResizable(True)
        self.scrollarea_hk.setWidget(self.hkcontainer)

        self.filter_list = QtWidgets.QComboBox()
        self.filter_list.setStyleSheet(ScannerStyle.combo_all)
        self.filter_list.addItem("By Date", "date")
        self.filter_list.addItem("By Types", "type")
        self.filter_list.addItem("By CVSS", "score")

        self.filter_list_win = QtWidgets.QComboBox()
        self.filter_list_win.setStyleSheet(ScannerStyle.combo_all)
        self.filter_list_win.addItem("By Windows 11", "win11")
        self.filter_list_win.addItem("By Windows 10", "win10")
        self.filter_list_win.addItem("By Linux", "linux")

        self.latesttitle = QtWidgets.QLabel("Critical Vulnerabilities")
        self.latesttitle.setStyleSheet(ScannerStyle.hislabelstylesheet)
        self.latestcontent = QtWidgets.QLabel("Loading Data")
        self.wintitle = QtWidgets.QLabel("Latest vulnerabilities for Windows 11")
        self.wintitle.setStyleSheet(ScannerStyle.hislabelstylesheet)
        self.wincontent = QtWidgets.QLabel("Loading Data")
        self.latestlayout.addWidget(self.latesttitle)
        self.latestlayout.addWidget(self.latestcontent)
        self.latestlayout.addStretch()
        self.winlayout.addWidget(self.wintitle)
        self.winlayout.addWidget(self.filter_list_win)
        self.winlayout.addWidget(self.wincontent)

        _query_scroll = QtWidgets.QScrollArea()
        _query_scroll.setWidgetResizable(True)
        _query_scroll.setMinimumWidth(220)
        _query_scroll.setMinimumHeight(120)
        _query_scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        _query_scroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        _query_scroll.setStyleSheet(ScannerStyle.scrollstyle)
        _query_scroll.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        _query_scroll.setWidget(self.searchcontainer)

        _news = QtWidgets.QWidget()
        _news.setStyleSheet("""background: #F5F9FF;""")
        _news_layout = QtWidgets.QVBoxLayout(_news)
        _news_layout.setContentsMargins(0, 0, 0, 0)
        _news_layout.setSpacing(6)
        _news_layout.addWidget(self.hometitle)
        _news_layout.addWidget(self.scrollarea_news, 1)

        _hk = QtWidgets.QWidget()
        _hk.setStyleSheet("""background: #F5F9FF;""")
        _hk_layout = QtWidgets.QVBoxLayout(_hk)
        _hk_layout.setContentsMargins(0, 0, 0, 0)
        _hk_layout.setSpacing(6)
        _hk_layout.addWidget(self.hktitle)
        _hk_layout.addWidget(self.scrollarea_hk, 1)

        _latest_scroll = QtWidgets.QScrollArea()
        _latest_scroll.setWidgetResizable(True)
        _latest_scroll.setMinimumWidth(200)
        _latest_scroll.setStyleSheet(ScannerStyle.scrollstyle)
        _latest_scroll.setWidget(self.latestcontainer)

        _win_scroll = QtWidgets.QScrollArea()
        _win_scroll.setWidgetResizable(True)
        _win_scroll.setMinimumWidth(200)
        _win_scroll.setStyleSheet(ScannerStyle.scrollstyle)
        _win_scroll.setWidget(self.wincontainer)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(True)
        self.main_splitter.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.main_splitter.setHandleWidth(2)
        self.main_splitter.setStyleSheet("""
                                        QSplitter::handle {
                                            background: #FFFFFF;
                                            margin: 2px; 
                                        }

                                        QSplitter::handle:pressed {
                                            background: #6488EA;
                                        }
                                    """)
        self.main_splitter.addWidget(_query_scroll)
        self.main_splitter.addWidget(_news)
        self.main_splitter.addWidget(_hk)
        self.main_splitter.addWidget(_latest_scroll)
        self.main_splitter.addWidget(_win_scroll)
        for i in range(5):
            self.main_splitter.setStretchFactor(i, 1)
        self.main_splitter.setSizes([280, 220, 220, 260, 260])

        self.layoutcontainer.addWidget(self.main_splitter, 0, 0)
        self.layoutcontainer.setRowStretch(0, 1)
        self.layoutcontainer.setColumnStretch(0, 1)

    def query_selector(self):

        self.selectorcontainer = QtWidgets.QWidget()
        self.selectorlayout = QtWidgets.QGridLayout(self.selectorcontainer)
        self.selectorlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.family = QtWidgets.QComboBox()
        self.family.setStyleSheet(ScannerStyle.combo_all)
        self.family.addItem("Family", None)
        self.family.addItems(["Unix", "Blog", "Software", "Info", "Exploit", "NVD", "Bugbounty", "Tools", "Microsoft", "Scanner"])
        self.family.model().item(0).setEnabled(False)
        self.family.currentTextChanged.connect(self._query_builder)

        self.bulletintype = QtWidgets.QComboBox()
        self.bulletintype.setStyleSheet(ScannerStyle.combo_all)
        self.bulletintype.addItem("Bulletin Type", None)
        self.bulletintype.addItems(["adobe", "almalinux", "alphinelinux", "amazon", "amd",
                                    "android", "androidsecurity", "apple", "chrome", "cisa",
                                    "cisco", "cve", "cvelist", "exploitdb", "fedora",
                                    "github", "githubexploit", "gitlab", "googleprojectzero", "hp",
                                    "huawei", "ibm", "ics", "intel", "kaspersky",
                                    "lenovo", "malwarebytes", "metasploit", "mmpc", "mongodb",
                                    "mozilla", "mscve", "nmap", "nodejs", "nvd",
                                    "nvidia", "openssl", "redhat", "ubuntu", 
                                ])
        self.bulletintype.model().item(0).setEnabled(False)
        self.bulletintype.currentTextChanged.connect(self._query_builder)
        

        self.mincvss = QtWidgets.QComboBox()
        self.mincvss.setStyleSheet(ScannerStyle.combo_all)
        self.mincvss.addItem("Minimum CVSS Score", None)
        self.mincvss.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.mincvss.model().item(0).setEnabled(False)
        self.mincvss.currentTextChanged.connect(self._query_builder)
        

        self.date = QtWidgets.QComboBox()
        self.date.setStyleSheet(ScannerStyle.combo_all)
        self.date.addItem("Date", None)
        self.date.addItems(["Last 10 Days", "Last Month", "Last 6 Month", "Last Year"])
        self.date.model().item(0).setEnabled(False)
        self.date.currentTextChanged.connect(self._query_builder)
        
        self.order = QtWidgets.QComboBox()
        self.order.setStyleSheet(ScannerStyle.combo_all)
        self.order.addItem("Order By", None)
        self.order.addItems(["Date published", "CVSS Score"])
        self.order.setItemData(1, "published")
        self.order.setItemData(2, "cvss.score")
        self.order.model().item(0).setEnabled(False)
        self.order.currentTextChanged.connect(self._query_builder)

        self.limit_results = QtWidgets.QComboBox()
        self.limit_results.setStyleSheet(ScannerStyle.combo_all)
        self.limit_results.addItem("Results", None)
        self.limit_results.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "15", "20"])
        self.limit_results.model().item(0).setEnabled(False)
        self.limit_results.currentTextChanged.connect(self._query_builder)
        
        self.enterbtn = QtWidgets.QPushButton("Search")
        self.enterbtn.setStyleSheet(ScannerStyle.btnestylesheet)
        self.enterbtn.clicked.connect(self._search_query)
        self.clearbtn = QtWidgets.QPushButton("Clear")
        self.clearbtn.setStyleSheet(ScannerStyle.btncstylesheet)
        self.clearbtn.clicked.connect(self._clear_all_query)

        self.selectorlayout.addWidget(self.family, 1, 1)
        self.selectorlayout.addWidget(self.bulletintype, 1, 2)
        self.selectorlayout.addWidget(self.mincvss, 1, 3)
        self.selectorlayout.addWidget(self.date, 1, 4)
        self.selectorlayout.addWidget(self.order, 2, 1)
        self.selectorlayout.addWidget(self.limit_results, 2, 2)
        self.selectorlayout.addWidget(self.enterbtn, 3, 1, 1, 2)
        self.selectorlayout.addWidget(self.clearbtn, 3, 3, 1, 2)
        self.searchlayout.addWidget(self.selectorcontainer)
        self.searchlayout.addStretch(1)

    def _query_builder(self):

        query = []

        if self.family.currentIndex() > 0:
            query.append(f"type:{str(self.family.currentText())} AND")
        if self.bulletintype.currentIndex() > 0:
            query.append(f"bulletinFamily:{str(self.bulletintype.currentText())} AND")
        if self.order.currentIndex() > 0:
            query.append(f"order:{self.order.currentData()} AND")
        if self.mincvss.currentIndex() > 0:
            query.append(f"cvss.score:[{str(self.mincvss.currentText())} TO 10]")
        if self.date.currentIndex() > 0:
            query.append(f"{self.date.currentText().lower()}")
        

        query_string = ' '.join(query)
        if query_string.endswith('AND'):
            query_string = query_string[:-3].strip()

        self.search.setText(query_string)

    def _clear_all_query(self):

        self.search.clear()
        self.family.setCurrentIndex(0)
        self.bulletintype.setCurrentIndex(0)
        self.order.setCurrentIndex(0)
        self.mincvss.setCurrentIndex(0)
        self.date.setCurrentIndex(0)

    def _search_query(self):

        try:
            query = self.search.text().strip()
            if not query:
                return

            if hasattr(self, 'search_worker') and self.search_worker and self.search_worker.isRunning():
                self.search_worker.finished.disconnect()
                self.search_worker.terminate()
                self.search_worker.wait()

            if int(self.limit_results.currentText()) <= 0:
                function.error_msg("Error", "Please select the number of result you want to search!")
                return
            else:
                limit = int(self.limit_results.currentText()) 
            self.enterbtn.setEnabled(False)
            self.enterbtn.setText("Searching...")
            self.search_worker = Worker(self.api, query=query, limit=limit) if limit > 0 else Worker(self.api, query=query, limit=1)
            self.search_worker.finished.connect(self._show_search_results)
            self.search_worker.start()
        
        except ValueError:
            function.error_msg("Error", "Please select the number of result you want to search!")
            return
        
    def _show_search_results(self, results):

        self.enterbtn.setEnabled(True)
        self.enterbtn.setText("Search")

        query = self.search.text().strip()
        dialog = SearchResultWindow(query, results, parent=self)
        dialog.show()

    def latestvuln(self, results):
        
        if not results:
            self.latestcontent.setText("Error fetching vulnerability data from database!")
            function.logging.error("Error fetching from database")
            return
        while self.latestlayout.count() > 1:
            item = self.latestlayout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        count = 1

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.setHandleWidth(0)
        splitter.setChildrenCollapsible(False)

        top5scroll = QtWidgets.QScrollArea()
        top5scroll.setWidgetResizable(True)
        top5scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        top5scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        top5scroll.setStyleSheet("background: transparent;")
        top5container = QtWidgets.QWidget()
        top5layout = QtWidgets.QVBoxLayout(top5container)

        for result in results:
            vtype = result.get('type', '')
            title = result.get('title', 'Unknown')
            published = result.get('published', 'Unknown')
            cvss_info = result.get('cvss', {})
            cvss_val = cvss_info.get('score', 0) if isinstance(cvss_info, dict) else (cvss_info if isinstance(cvss_info, (int, float)) else 0)
            try:
                cvss_val = float(cvss_val)
            except (TypeError, ValueError):
                cvss_val = 0.0

            if count <= 5:
                score = QtWidgets.QLabel()
                score.setMaximumWidth(200)
                if cvss_val < 4:
                    color = "#6FC276"
                    score.setText("LOW")
                elif cvss_val < 7:
                    color = "#FFF49B"
                    score.setText("MEDIUM")
                elif cvss_val < 9:
                    color = "#ECAA1A"
                    score.setText("HIGH")
                else:
                    color = "#FF2C2C"
                    score.setText("CRITICAL")
                score.setStyleSheet(f"""
                    background: {color};
                    border-radius: 70px;
                    border: 1px solid {color};
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: bold;
                    margin: 2px 2px 2px 2px;
                    text-align: center;
                """)

                titlelabel = QtWidgets.QLabel(title)
                titlelabel.setWordWrap(True)
                publishedlabel = QtWidgets.QLabel(published)

                top5layout.addWidget(score)
                top5layout.addWidget(titlelabel)
                top5layout.addWidget(publishedlabel)
                count += 1

        top5layout.addStretch()
        top5scroll.setWidget(top5container)

        graphcontainer = QtWidgets.QWidget()
        graphcontainer.setMinimumHeight(200)
        graphlayout = QtWidgets.QVBoxLayout(graphcontainer)
        graph_canvas = self._plot_graph(self._format_date(self.results))
        graphlayout.addWidget(self.filter_list)
        graphlayout.addWidget(graph_canvas, 1)
        self.graphlayout = graphlayout

        splitter.addWidget(top5scroll)
        splitter.addWidget(graphcontainer)
        splitter.setSizes([1, 1])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        self.latestlayout.addWidget(splitter, 1)
        self.latestlayout.addStretch()
    
    def _windows_vuln(self, results):

        if not results:
            self.wincontent.show()
            self.wincontent.setText("Error fetching vulnerability data from database!")
            function.logging.error("Error fetching from database")
            return

        while self.winlayout.count() > 3:
            item = self.winlayout.takeAt(3)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

        self.wincontent.hide()
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        for result in results:
            title = result.get('title', 'Unknown')
            published = result.get('published', 'Unknown')
            descri = result.get('description', 'Unknown')
            cvss_info = result.get('cvss', {})
            cvss_val = cvss_info.get('score', 0) if isinstance(cvss_info, dict) else (cvss_info if isinstance(cvss_info, (int, float)) else 0)
            try:
                cvss_val = float(cvss_val)
            except (TypeError, ValueError):
                cvss_val = 0.0

            if cvss_val < 4:
                color = "#6FC276"
            elif cvss_val < 7:
                color = "#FFF49B"
            elif cvss_val < 9:
                color = "#F5CA7B"
            else:
                color = "#FF2C2C"

            section = function.collapse_section(title, start_open=False)
            section.setStyleSheet("""font-size: 16px;""")
            publishedlabel = QtWidgets.QLabel(published)
            cvsslabel = QtWidgets.QLabel(f'CVSS Score: {str(cvss_val)}')
            cvsslabel.setStyleSheet(f"background: {color}; color: #FFFFFF; margin: 2px 2px 2px 2px; text-align: center; border-radius: 70px;")
            cvsslabel.setMaximumWidth(250)
            desccontent = QtWidgets.QLabel(descri)
            desccontent.setWordWrap(True)
            desccontent.setMinimumHeight(50)
            desccontent.setContentsMargins(5, 5, 5, 5)
            desccontent.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
            section._add_widget(publishedlabel)
            section._add_widget(cvsslabel)
            section._add_widget(desccontent)
            layout.addWidget(section)
            layout.addStretch()
        
        self.winlayout.addWidget(container)

    def _windows_vuln_filter(self):

        if not getattr(self, 'winlayout', None):
            return

        if hasattr(self, 'win_worker') and self.win_worker and self.win_worker.isRunning():
            self.win_worker.finished.disconnect()
            self.win_worker.terminate()
            self.win_worker.wait()

        signal = self.filter_list_win.currentData() or ''

        if 'win10' in signal:
            self.wintitle.setText("Latest vulnerabilities for Windows 10")
            self.win_worker = self._run_query(query="Windows 10 AND bulletinFamily:microsoft  type:mscve order:published", limit=5, connect_finish1=self._windows_vuln)
        elif 'win11' in signal:
            self.wintitle.setText("Latest vulnerabilities for Windows 11")
            self.win_worker = self._run_query(query="Windows 11 AND bulletinFamily:microsoft  type:mscve order:published", limit=5, connect_finish1=self._windows_vuln)
        else:
            self.wintitle.setText("Latest vulnerabilities for Linux")
            self.win_worker = self._run_query(query="linux AND order:published", limit=5, connect_finish1=self._windows_vuln)

    def _plot_graph(self, data):
        
        try:

            if isinstance(data, dict) and data:

                labels = []
                values = []
                for label, value in data.items():
                    labels.append(str(label))
                    values.append(value)

                fig = Figure(figsize=(5, 4), tight_layout=True)
                canvas = FigureCanvas(fig)
                pies = fig.add_subplot(111)
                wedges, _ = pies.pie(
                    values,
                    radius=1.0,
                    startangle=90,
                    autopct=None,
                )
                legend_labels = [f"{l} ({v}, {v/sum(values)*100:.1f}%)" for l, v in zip(labels, values)]
                pies.legend(wedges, legend_labels, loc='upper left', bbox_to_anchor=(1.05, 0.5), fontsize=8)
                pies.set_title("Recent Critical Records", loc='center', pad=15, fontsize=12, fontweight='bold')
                fig.subplots_adjust(left=0.3, right=0.95, top=0.88, bottom=0.05)
                canvas.draw()
                return canvas
        except Exception as e:
            function.logging.error(f"{str(e)}")
        return QtWidgets.QLabel("Error occur when creating a chart!")
    
    def _plot_graph_filter(self):

        if not getattr(self, 'results', None) or not self.graphlayout:
            return
        signal = self.filter_list.currentData() or ''
        if 'date' in signal:
            data = self._format_date(self.results)
        elif 'type' in signal:
            data = self._format_type(self.results)
        else:
            data = self._format_cvss(self.results)
        new_canvas = self._plot_graph(data)
        if self.graphlayout.count() > 1:
            old_item = self.graphlayout.takeAt(1)
            if old_item and old_item.widget():
                old_item.widget().deleteLater()
        self.graphlayout.addWidget(new_canvas)
        
    def _format_date(self, data):

        dates = {'today': 0, 'last3day': 0, 'more': 0, 'Unknown': 0}
        today_dt = datetime.today()

        for item in data:
            pub = item.get('published', 'Unknown')
            if pub == 'Unknown':
                dates['Unknown'] += 1
                continue
            try:
                if isinstance(pub, str):
                    pub_dt = datetime.fromisoformat(pub.replace('Z', '+00:00').split('.')[0])
                else:
                    pub_dt = pub
                delta = (today_dt - pub_dt).days
                if delta >= 4:
                    dates['more'] += 1
                elif delta >= 1:
                    dates['last3day'] += 1
                else:
                    dates['today'] += 1
            except (ValueError, TypeError):
                dates['Unknown'] += 1

        for key in list(dates.keys()):
            if dates[key] == 0:
                del dates[key]
        return dates
    
    def _format_type(self, data):

        types = {}
        for item in data:
            t = item.get('type', 'Unknown') or 'Unknown'
            types[t] = types.get(t, 0) + 1
        return types

    def _format_cvss(self, data):

        cvs = {f'{i}.0': 0 for i in range(1, 11)}
        cvs['Unknown'] = 0
        for item in data:
            cvss_info = item.get('cvss')
            if cvss_info is None:
                cvs['Unknown'] += 1
                continue
            if isinstance(cvss_info, dict):
                score = cvss_info.get('score')
            else:
                score = cvss_info
            try:
                score = float(score)
                key = f'{min(10, max(1, int(round(score))))}.0'
                cvs[key] = cvs.get(key, 0) + 1
            except (TypeError, ValueError):
                cvs['Unknown'] += 1
        for key in list(cvs.keys()):
            if cvs[key] == 0:
                del cvs[key]
        return cvs
        
class SearchResultWindow(QtWidgets.QDialog):

    def __init__(self, query, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Results")
        self.setStyleSheet("""background: #F5F9FF;""")
        self.setMinimumSize(900, 650)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)

        mainlayout = QtWidgets.QVBoxLayout(self)
        mainlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainlayout.setContentsMargins(15, 15, 15, 15)
        mainlayout.setSpacing(5)

        header = QtWidgets.QLabel(f"Search Results")
        header.setStyleSheet(ScannerStyle.hislabelstylesheet)
        header.setFixedHeight(45)
        mainlayout.addWidget(header)

        querylabel = QtWidgets.QLabel(f"Query: {query}")
        querylabel.setStyleSheet(ScannerStyle.scannertitlestylesheet)
        querylabel.setWordWrap(True)
        mainlayout.addWidget(querylabel)

        if not results:
            errorlabel = QtWidgets.QLabel("No results found or an error occurred while fetching data.")
            errorlabel.setStyleSheet("font-size: 18px; font-weight: bold; color: #E74C3C; padding: 10px;")
            errorlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            mainlayout.addWidget(errorlabel)
        else:

            countlabel = QtWidgets.QLabel(f"Found {len(results)} result(s)")
            countlabel.setStyleSheet("font-size: 18px; color: #1A1A1A; font-weight: bold;padding: 10px;")
            mainlayout.addWidget(countlabel)

            scrollarea = QtWidgets.QScrollArea()
            scrollarea.setWidgetResizable(True)
            scrollarea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            scrollarea.setStyleSheet(ScannerStyle.scrollstyle)

            scrollcontent = QtWidgets.QWidget()
            scrollcontent.setStyleSheet("background: #F5F9FF;")
            scrolllayout = QtWidgets.QVBoxLayout(scrollcontent)
            scrolllayout.setContentsMargins(5, 5, 5, 5)
            scrolllayout.setSpacing(2)

            for result in results:
                card = self._create_result_card(result)
                scrolllayout.addWidget(card)

            scrolllayout.addStretch()
            scrollarea.setWidget(scrollcontent)
            mainlayout.addWidget(scrollarea, 1)

        closebtn = QtWidgets.QPushButton("Close")
        closebtn.setStyleSheet(ScannerStyle.btncstylesheet)
        closebtn.setFixedSize(120, 35)
        closebtn.clicked.connect(self.close)

        btnlayout = QtWidgets.QHBoxLayout()
        btnlayout.addStretch()
        btnlayout.addWidget(closebtn)
        mainlayout.addLayout(btnlayout)

    def _create_result_card(self, result):

        card = QtWidgets.QWidget()
        card.setStyleSheet('''
            QWidget {
                background: #FFFFFF;
                border-bottom: 5px solid #6488EA;
                border-radius: 8px;
                padding: 10px;
            }
        ''')

        cardlayout = QtWidgets.QVBoxLayout(card)
        cardlayout.setSpacing(4)
        cardlayout.setContentsMargins(12, 10, 12, 10)

        vtype = result.get('type', '')
        title = result.get('title', 'Unknown')
        published = result.get('published', 'Unknown')
        descri = result.get('description', 'Unknown')
        cvelist = result.get('cvelist', [])
        cvss = result.get('cvss', {})

        titlelabel = QtWidgets.QLabel(title)
        titlelabel.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A1A1A; background: #8FC9FF; border: 1px solid #6488EA; border-radius: 8px; padding: 5px;")
        titlelabel.setWordWrap(True)
        cardlayout.addWidget(titlelabel)

        if vtype:
            typelabel = QtWidgets.QLabel(f"Type: {vtype}")
            typelabel.setStyleSheet("font-weight: bold; color: #1A1A1A; font-size: 14px; border: none;")
            cardlayout.addWidget(typelabel)

        datelabel = QtWidgets.QLabel(f"Published: {published}")
        datelabel.setStyleSheet("font-size: 14px; color: #1A1A1A; border: none;")
        cardlayout.addWidget(datelabel)

        if cvss and isinstance(cvss, dict):
            cvssscore = cvss.get('score', 'N/A')
            try:
                score_val = float(cvssscore)
                if score_val <= 3.3:
                    color = "#6FC276"
                    severity = "LOW"
                elif score_val <= 6.3:
                    color = "#F1A310"
                    severity = "MEDIUM"
                else:
                    color = "#FF2C2C"
                    severity = "HIGH"
                scoretext = f"CVSS: {cvssscore} ({severity})"
            except (TypeError, ValueError):
                color = "#888"
                scoretext = f"CVSS: {cvssscore}"

            cvsslabel = QtWidgets.QLabel(scoretext)
            cvsslabel.setStyleSheet(f"font-size: 14px; color: {color}; font-weight: bold; border: none;")
            cardlayout.addWidget(cvsslabel)

        if cvelist:
            cvetext = ', '.join(cvelist[:5])
            if len(cvelist) > 5:
                cvetext += f" (+{len(cvelist) - 5} more)"
            cvelabel = QtWidgets.QLabel(f"CVEs: {cvetext}")
            cvelabel.setStyleSheet("font-size: 11px; color: #C0392B; border: none;")
            cvelabel.setWordWrap(True)
            cardlayout.addWidget(cvelabel)

        if descri and descri != 'Unknown':
            desclabel = QtWidgets.QPlainTextEdit(descri)
            desclabel.setReadOnly(True)
            desclabel.setMaximumHeight(80)
            desclabel.setStyleSheet(ScannerStyle.vulgridstylesheet)
            cardlayout.addWidget(desclabel)

        return card




