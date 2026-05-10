from fileinput import filename
from PyQt6 import QtWidgets, QtCore
import sys
from Widgets.MenuBar import Topmenu, fileexport
from Widgets.QuickFunction import QuickFunction
from Widgets.Scanner import Scan, Worker
from Widgets.CustomScanner import CustScan
from Widgets.History import History
from Widgets.HomePage import VulDashboard
from Widgets.Help import HelpDialog
from Widgets import ScannerStyle
from Widgets.CustomTitle import CustomTitleBar, enable_frameless_resize
from Widgets.ConfigLoader import config_loader
from Widgets.OnboardingTour import init_onboarding

class Main(QtWidgets.QWidget):

    def __init__(self, nmap_path, api_v, api_ai):
        super().__init__()
        self.setWindowTitle('Advanced Network Scanner')
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(1024, 768)
        self._frameless_resize = enable_frameless_resize(self)
        self.nmap_path = nmap_path
        self.api_v = api_v
        self.api_ai = api_ai
        self.main()

    def main(self):

        self.maincontent = QtWidgets.QVBoxLayout(self)
        self.maincontent.setContentsMargins(0, 0, 0, 0)
        self.maincontent.setSpacing(0)

        self.backgroundcontainer = QtWidgets.QWidget()
        self.backgroundlayout = QtWidgets.QGridLayout(self.backgroundcontainer)
        self.backgroundlayout.setContentsMargins(0, 0, 0, 0)
        self.backgroundlayout.setSpacing(0)
        
        self.titlebar = CustomTitleBar(self)

        self.topcontainer = QtWidgets.QWidget()
        self.toplayout = QtWidgets.QVBoxLayout(self.topcontainer)
        self.toplayout.setContentsMargins(0, 0, 0, 0)
        self.topcontainer.setStyleSheet(ScannerStyle.topstylesheet)
        self.topcontainer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.topcontainer.setFixedHeight(60)

        self.topwidget = Topmenu(main_window=self)
        self.toplayout.addStretch()
        self.toplayout.addWidget(self.topwidget, 1)
        self.topwidget.scanbtn.clicked.connect(lambda: self.stack.setCurrentWidget(self.ascanwidget))
        self.topwidget.helpbtn.clicked.connect(lambda: HelpDialog(self).show())
        self.topwidget.exportbtn.clicked.connect(self._currentexport)
        
        self.split = QtWidgets.QSplitter()
        self.split.setHandleWidth(2)
        self.split.setStyleSheet("""
                                QSplitter {
                                    background: #FFFFFF;
                                }
                                QSplitter::handle {
                                    background: #FFFFFF;
                                    margin: 2px; 
                                }
                                QSplitter::handle:pressed {
                                    background-color: #6488EA;
                                }
                                """) 
        self.middlecontainer = QtWidgets.QWidget()
        self.middlecontainer.setStyleSheet(ScannerStyle.hisstylesheet)
        self.middlelayout = QtWidgets.QVBoxLayout(self.middlecontainer)
        self.middlewidget = History(nmap_path=nmap_path, api_vulners=api_vulners, api_ai=api_ai)
        self.middlelayout.addWidget(self.middlewidget)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.setStyleSheet(ScannerStyle.stackstylesheet)
        self.homewidget = VulDashboard(self.api_v)
        self.qscanwidget = Scan(nmap_path=nmap_path, api_vulners=api_vulners, api_ai=api_ai, name="Quick Scan", placeholder="E.g. 192.168.1.1 / www.google.com / 192.168.1-254", command="-sS -T4 -p 0-1023", title=f"{filename}")
        self.qscanwidget.progress_signal.connect(self._updaterecord)
        self.cscanwidget = Scan(nmap_path=nmap_path, api_vulners=api_vulners, api_ai=api_ai, name="Comprehensive Scan", placeholder="E.g. 192.168.1.1 / www.google.com / 192.168.1-254", command="-Pn -sS -sV -O -p 0-65535", title=f"{filename}")
        self.cscanwidget._comprehensive()
        self.cscanwidget.progress_signal.connect(self.cscanwidget._update_comprehensive_result)
        self.cscanwidget.progress_signal.connect(self._updaterecord)
        self.vscanwidget = Scan(nmap_path=nmap_path, api_vulners=api_vulners, api_ai=api_ai, name="Vulnerability Scan", placeholder="E.g. 192.168.1.1 / www.google.com / 192.168.1-254", command="-sS -sV -vv --script vuln", title=f"{filename}")
        self.vscanwidget._vuln()
        self.vscanwidget.progress_signal.connect(self.vscanwidget._update_vuln_result)
        self.vscanwidget.progress_signal.connect(self.vscanwidget._update_vuln_sol)
        self.vscanwidget.progress_signal.connect(self._updaterecord)
        self.ascanwidget = CustScan(nmap_path=nmap_path, name="Custom Scan", placeholder="Please input an Nmap command.", title=f"{filename}")
        self.ascanwidget._custom()
        self.ascanwidget.progress_signal.connect(self.ascanwidget._update_script_result)
        self.ascanwidget.progress_signal.connect(self._updaterecord)
        self.stack.addWidget(self.homewidget)
        self.homewidget.setStyleSheet("border: none;")
        self.stack.addWidget(self.qscanwidget)
        self.qscanwidget.setStyleSheet("border: none;")
        self.stack.addWidget(self.cscanwidget)
        self.cscanwidget.setStyleSheet("border: none;")
        self.stack.addWidget(self.vscanwidget)
        self.vscanwidget.setStyleSheet("border: none;")
        self.stack.addWidget(self.ascanwidget)
        self.ascanwidget.setStyleSheet("border: none;")
        self.stack.setCurrentWidget(self.homewidget)

        self.split.addWidget(self.middlecontainer)
        self.split.addWidget(self.stack)
        self.split.setStretchFactor(0, 1)
        self.split.setStretchFactor(1, 1)

        self.leftcontainer = QtWidgets.QWidget()
        self.leftcontainer.setStyleSheet(ScannerStyle.leftstylesheet)
        self.leftlayout = QtWidgets.QVBoxLayout(self.leftcontainer)

        self.leftwidget = QuickFunction()
        self.leftwidget.setStyleSheet("border: none;")
        self.leftwidget.homebtn.clicked.connect(lambda: self.stack.setCurrentWidget(self.homewidget))
        self.leftwidget.hisbtn.clicked.connect(lambda: self.middlecontainer.hide() if self.middlecontainer.isVisible() else self.middlecontainer.show())
        self.leftwidget.qscanbtn.clicked.connect(lambda: self.stack.setCurrentWidget(self.qscanwidget))
        self.leftwidget.cscanbtn.clicked.connect(lambda: self.stack.setCurrentWidget(self.cscanwidget))
        self.leftwidget.vscanbtn.clicked.connect(lambda: self.stack.setCurrentWidget(self.vscanwidget))
        self.leftwidget.exit.clicked.connect(lambda: self.stack.setCurrentWidget(sys.exit()))
        self.leftlayout.addWidget(self.leftwidget)

        self.backgroundlayout.addWidget(self.leftcontainer, 0, 0, 2, 1)
        self.backgroundlayout.addWidget(self.topcontainer, 0, 1, 1, 1)
        self.backgroundlayout.addWidget(self.split, 1, 1)
        self.maincontent.addWidget(self.titlebar)
        self.maincontent.addWidget(self.backgroundcontainer)

        self._onboarding_tour = None
        QtCore.QTimer.singleShot(0, self._start_onboarding)

    def _start_onboarding(self):
        def _on_done():
            if self._onboarding_tour is not None:
                self._onboarding_tour.deleteLater()
                self._onboarding_tour = None
            from Widgets.ConfigLoader import onboarding_done
            onboarding_done()
        
        self._onboarding_tour = init_onboarding(self, on_complete=_on_done)

    def closeEvent(self, event):
        if self._frameless_resize is not None:
            self._frameless_resize.cleanup()
            self._frameless_resize = None
        super().closeEvent(event)

    def _currentexport(self):

        currentwidget = self.stack.currentWidget()
        filepath = None

        if isinstance(currentwidget, CustScan) and getattr(currentwidget, "filepath", None):
            filepath = currentwidget.filepath
        elif isinstance(currentwidget, Scan) and hasattr(currentwidget, "filepath") and currentwidget.filepath:
            filepath = currentwidget.filepath

        exportdialog = fileexport(self, filepath, self.middlewidget)
        exportdialog.exec()
        
    def _updaterecord(self):

        currentwidget = self.stack.currentWidget()
        has_path = (
            isinstance(currentwidget, CustScan)
            and getattr(currentwidget, "filepath", None)
        ) or (
            isinstance(currentwidget, Scan)
            and hasattr(currentwidget, "filepath")
            and currentwidget.filepath
        )
        if has_path:
            if self.middlewidget.bydate:
                self.middlewidget._orderbydate(self.middlewidget.hislist)
            else:
                self.middlewidget._orderbytype(self.middlewidget.hislist)

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    nmap_path, api_vulners, api_ai = config_loader()
    display = Main(nmap_path, api_vulners, api_ai)
    display.show()
    sys.exit(app.exec())