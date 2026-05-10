###########################################################
#Left widgit style
###########################################################
leftstylesheet = ("""
    QWidget{
        background: #F5F9FF;
        border: 5px solid #FFFFFF;
    }        
    """)

leftbtnstylesheet = ("""
    QPushButton{
        background: #F5F9FF;
        font-size: 16px;
        font: bold;
        text-align: left;
        padding-left: 10px;
        border: 0px solid #000000;
    }
    QPushButton:hover{
        background: #FFFFFF;
        color: #6488EA;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    } 
    QPushButton:checked{
        background: #6488EA;
        color: #FFFFFF;
        font-size: 16px;
        font: bold;
        text-align: left;
        padding-left: 10px;
        border: 0px solid #000000;
    }           
    """)

clickedbtn = ("""
    QPushButton{
        background: #FFFFFF;
        color: #6488EA;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
        font-size: 16px;
        font: bold;
        text-align: left;
        padding-left: 10px;
    }            
    """)

backbtnstylesheet = ("""
    QPushButton{
        background: #6488EA;
        font-size: 16px;
        font: bold;
        text-align: center;
        padding-left: 5px;
        border: 0px solid #000000;
        border-radius: none;
    }
    QPushButton:hover{
        background: #FFFFFF;
        border-bottom: 2px solid #6488EA;
    }            
    """)

leftlabelstyle = ("""
    font-size: 16px; 
    font: bold; 
    background: #6488EA; 
    color: #FFFFFF;
    text-align: left;
    padding-left: 5px;
    """)

exbtnstylesheet = ("""
    QPushButton{
        background: #FFDDE1;
        font-size: 16px;
        font: bold;
        text-align: left;
        padding-left: 10px;
        border: 0px solid #000000;
    }
    QPushButton:hover{
        background: #FF555C;  
        border-bottom: 2px solid #FF0008; 
        border-radius: 8px;
    }            
    """)
hiddenbtnstylesheet = ("""
    QPushButton{
        background: #6488EA;
        font-size: 16px;
        font: bold;
        text-align: center;
        border: 0px solid #000000;
        border-radius: none;
    }
    QPushButton:hover{
        background: #FFFFFF;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }            
    """)
hiddenexbtnstylesheet = ("""
    QPushButton{
        background: #FFDDE1;
        font-size: 16px;
        font: bold;
        text-align: center;
        border: 0px solid #000000;
        border-radius: none;
    }
    QPushButton:hover{
        background: #FF555C;  
        border-bottom: 2px solid #FF0008; 
        border-radius: 8px;
    }            
    """)
###########################################################
#Top widget style
###########################################################
topstylesheet = ("""
    background: #FFFFFF;
    border: 0px solid #000000;
    border-radius: 0px;
    """)

topbtnstylesheet = ("""
    QPushButton{
        background: #F4F9FF;
        color: #0048AE;
        font-size: 20px;
        font: bold;
        text-align: left;
        padding-left: 10px;
        border-bottom: 2px solid #0048AE;
        border-radius: 8px;
    }
    QPushButton:hover{
        background: #FFFFFF;
        color: #6488EA;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }            
    """)

exporttitle = ("""
    font-size: 16px; 
    font: bold; 
    background: transparent; 
    text-align: left;
    border-bottom: 2px solid #6488EA;
    border-radius: 8px;
    """)

setting = ("""
    QPushButton{
        background: #6488EA;
        color: #FFFFFF;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
        font: bold;
        font-size: 16px;
        text-align: center;
        }   
    QPushButton:hover{
    background: #FFFFFF;
    color: #6488EA;
    border-bottom: 2px solid #6488EA;
    border-radius: 8px;
    }           
    """)
###########################################################
#History style
###########################################################
hisstylesheet = ("""
    background: #F5F9FF;
    border: 5px solid #FFFFFF;
    border-radius: 8px;
    """)

hisbtnstylesheet = ("""
    QPushButton{
        background: #8FC9FF;
        color: #FFFFFF;
        font-size: 16px;
        font: bold;
        text-align: left;
        padding-left: 10px;
        border: 0px solid #000000;
        border-radius: 0px;
    }
    QPushButton:hover{
        background: #FFFFFF;
        color: #6488EA;
        border-bottom: 2px solid #8FC9FF;
        border-radius: 8px;
        }            
    """)

showbtnstylesheet = ("""
    QPushButton{
        background: #6488EA;
        color: #FFFFFF;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
        font: bold;
        font-size: 16px;
        text-align: center;
        }   
    QPushButton:hover{
    background: #FFFFFF;
    color: #6488EA;
    border-bottom: 2px solid #6488EA;
    border-radius: 8px;
    }           
    """)

datestylesheet = ("""
    font-size: 12px; 
    background: #F5F9FF; 
    text-align: left;
    border: 0px solid #000000;
    padding-left: 10px;
    """)

hislabelstylesheet = ("""
    font-size: 20px; 
    font: bold;
    background: #6488EA; 
    color: #FFFFFF;
    text-align: left;
    border: 1px solid #6488EA;
    border-radius: 8px;
    """)

hisscrollstylesheet = ("""
    QScrollArea{
        background: none; 
        border: none;
    }
    QScrollBar:vertical{
        background: #FFFFFF;
        width: 5px;
        margin: 0px;
        border: none;
    }
    QScrollBar::handle:vertical{
        background: #6488EA;
        border-radius: 6px;
        border: none;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical{
        height: 0px;
        border: none;
        background: none;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical{
        border: none;
        background: none;
    }
    """)

btngroupstylesheet = ("""
        border: 5px solid #8FC9FF;
        border-radius: 8px;      
    """)

###########################################################
#Scanner style
###########################################################
scannertitlestylesheet = ("""
    font-size: 25px; 
    font: bold; 
    background: transparent; 
    text-align: left;
    border-bottom: 2px solid #6488EA;
    border-radius: 8px;
    """)

scannernamestylesheet = ("""
    font-size: 25px; 
    font: bold; 
    color: #FFFFFF;
    background: #6488EA; 
    text-align: left;
    padding-left: 5px;
    border: 0px solid #000000;
    border-radius: 8px;
    """)

fieldstylesheet = ("""
    QLineEdit{
        background: #FFFFFF;
        font-size: 15px;
        font: bold;
        text-align: left;
        border: 2px solid #6488EA;
        border-radius: 8px;
    }         
""")

scanbtnstylesheet = ("""
    QPushButton{
        background: #6488EA;
        color: #FFFFFF;
        font-size: 15px;
        font: bold;
        text-align: center;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }
    QPushButton:hover{
        background: #FFFFFF;
        color: #6488EA;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }            
    """)

stopbtnstylesheet = ("""
    QPushButton{
        background: #FF555C;
        color: #FFFFFF;
        font-size: 15px;
        font: bold;
        text-align: center;
        border-bottom: 2px solid #FF555C;
        border-radius: 8px;
    }
    QPushButton:hover{
        background: #FFFFFF;
        color: #FF555C;
        border-bottom: 2px solid #FF555C;
        border-radius: 8px;
    }            
    """)

###########################################################
#Stat card style
cardstylesheet = ("""
    background: #FFFFFF;
    border: 2px solid #8FC9FF;
    border-radius: 9px;
    padding: 10px;
    min-width: 120px;
    """)  

cardtitlestylesheet = ("""
    background: #8FC9FF;
    font-size: 20px;
    font: bold;
    color: #FFFFFF;
    border: none;
    """)  

cardvaluestylesheet = ("""
    background: transparent;
    font-size: 16px;
    font: bold;
    color: #000000;
    border: none;              
    """)  
###########################################################
#Bar style
barstyle = ('''
    QProgressBar{
        background: #FFFFFF;
        border: 2px solid #888888;
        border-radius: 8px;
        height: 10px;
    }
    QProgressBar::chunk{
        background: #00FF00;
        border: 1px solid #00FF00;
        border-radius: 8px;
        width: 5px;
    }
''')
###########################################################
#Tree style
treestyle = ("""
    QTreeView {
        font-size: 20px;
        background: #FFFFFF;
        text-align: left;
    }
    QTreeView::item {
        text-align: left;
    }
    QTreeView::item:selected {
        background: #E3F2FD;
        color: #000000;
    }
    QTreeView::item:hover {
        background: #8FC9FF;
        border: 1px solid #8FC9FF;
    }
    QHeaderView::section {
        font-size: 18px;
        font: bold;
        background: #8FC9FF;
        text-align: left;
        padding-left: 10px;
        padding-top: 5px;
        border: 1px solid #FFFFFF;
        border-radius: 8px;
        color: #FFFFFF;
    }
    QTreeView QScrollBar:vertical {
        background: #FFFFFF;
        width: 5px;
        margin: 0px;
        border: none;
    }
    QTreeView QScrollBar::handle:vertical {
        background: #6488EA;
        border: none;
        min-height: 20px;
    }
    QTreeView  QScrollBar:horizontal {
        background: #FFFFFF;
        height: 5px;
        margin: 0px;
        border: none;
    }
    QTreeView  QScrollBar::handle:horizontal {
        background: #6488EA;
        border: none;
        min-width: 20px;
    }
    QTreeView  QScrollBar::add-line:vertical,
    QTreeView  QScrollBar::sub-line:vertical,
    QTreeView  QScrollBar::add-line:horizontal,
    QTreeView  QScrollBar::sub-line:horizontal {
        height: 0px;
        width: 0px;
        border: none;
        background: none;
    }
    QTreeView  QScrollBar::add-page:vertical,
    QTreeView  QScrollBar::sub-page:vertical,
    QTreeView  QScrollBar::add-page:horizontal,
    QTreeView  QScrollBar::sub-page:horizontal {
        border: none;
        background: none;
    }
""")

tablestyle = ("""
    QTableView {
        font-size: 16px;
        background: #FFFFFF;
        text-align: left;
        gridline-color: #E8E8E8;
        border: none;
    }
    QTableView::item {
        text-align: left;
        padding: 2px 6px;
    }
    QTableView::item:selected {
        background: #E3F2FD;
        color: #000000;
    }
    QTableView::item:hover {
        background: #8FC9FF;
    }
    QHeaderView {
        background-color: #8FC9FF;
        margin: 0px;
        padding: 0px;
        border: none;
    }
    QHeaderView::section {
        font-size: 16px;
        font: bold;
        background: #8FC9FF;
        text-align: left;
        padding: 4px 6px;
        border: none;
        border-right: 1px solid #E8E8E8;
        border-bottom: 1px solid #E8E8E8;
        color: #FFFFFF;
    }
    QHeaderView::section:first {
        border-left: none;
    }
    QTableCornerButton::section {
        background-color: #8FC9FF;
        border: none;
        min-width: 0px;
        min-height: 0px;
        max-width: 0px;
        max-height: 0px;
    }
    QScrollBar:vertical {
        background: #ECECEC;
        width: 20px;
        margin: 0px;
        border: none;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background: #6488EA;
        border: none;
        border-radius: 6px;
        min-height: 28px;
    }
    QScrollBar::handle:vertical:hover {
        background: #5578D4;
    }
    QScrollBar:horizontal {
        background: #ECECEC;
        height: 20px;
        margin: 0px;
        border: none;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal {
        background: #6488EA;
        border: none;
        border-radius: 6px;
        min-width: 28px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #5578D4;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        height: 0px;
        width: 0px;
        border: none;
        background: transparent;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        background: #ECECEC;
    }
""")

btncstylesheet = ("""
    QPushButton{
        background: #FF555C;
        color: #FFFFFF;
        font-size: 15px;
        font: bold;
        text-align: center;
        border-bottom: 2px solid #FF555C;
        border-radius: 8px;
    }
    QPushButton:hover{
        background: #FFFFFF;
        color: #FF555C;
        border-bottom: 2px solid #FF555C;
        border-radius: 8px;
    }            
    """)

btnestylesheet = ("""
    QPushButton{
        background: #6488EA;
        color: #FFFFFF;
        font-size: 15px;
        font: bold;
        text-align: center;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }
    QPushButton:hover{
        background: #FFFFFF;
        color: #6488EA;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }   
    QPushButton:disabled{
        background: rgba(100, 136, 234, 0.2);
        color: #FFFFFF;
        font-size: 15px;
        font: bold;
        text-align: center;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }
""")
###########################################################
#Tabs
tabstyle = ("""
    QTabWidget::pane {
        background: #FFFFFF;
    }
    QTabBar::tab {
        background: #FFFFFF;
        padding: 8px 16px;
        margin-right: 2px;
        font-size: 16px;
    }
    QTabBar::tab:selected {
        background: #6488EA;
        border-radius: 8px;
        font-weight: bold;
        color: #FFFFFF;
    }
    QTabBar::tab:hover {
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }
""")
###########################################################
#summary title
summarytitle = ('''
    font-size: 20px;
    font: bold;
    text-align: left;
    color: #000000;
    background: #8FC9FF;
    color: #FFFFFF;
''')

#summary container
containerstyle = ("""
    QWidget {
        background: #F5F9FF;
        border-radius: 8px;
        padding: 5px;
    }
""")
###########################################################
#scanner scrollarea
scrollstyle = ("""
    QScrollArea {
        font-size: 20px;
        font-weight: bold;
        background: #FFFFFF;
        text-align: left;
        border-radius: 8px;
    }
    QScrollBar:vertical {
        background: #FFFFFF;
        width: 5px;
        margin: 0px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background: #6488EA;
        border: none;
    }
    QScrollBar:horizontal {
        background: #FFFFFF;
        height: 5px;
        margin: 0px;
        border: none;
    }
    QScrollBar::handle:horizontal {
        background: #6488EA;
        border: none;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        height: 0px;
        border: none;
        background: none;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        border: none;
        background: none;
    }
""")

terminal = ("""
    /* Avoid DirectWrite failures on systems missing Courier/Courier New */
    font-family: "Cascadia Mono", "Consolas", "Segoe UI Mono", monospace;
    font-size: 16px;
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 15px;
    border-radius: 4px;
    line-height: 1.4;
""")
###########################################################
#Detail result
###########################################################
#Scrollarea
comscrollstylesheet = ("""
    QScrollArea{
        background: none; 
        border: none;
    }
    QScrollBar:vertical{
        background: #E8EEF4;
        width: 20px;
        margin: 0px;
        border: none;
        border-radius: 0px;
    }
    QScrollBar::handle:vertical{
        background: #6488EA;
        border: none;
        min-width: 16px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover{
        background: #0D6EFD;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical{
        height: 0px;
        border: none;
        background: none;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical{
        border: none;
        background: none;
    }
""")
###########################################################
#GUI
###########################################################

stackstylesheet = ("""
    QStackedWidget{
        background: #F5F9FF;
        border: 5px solid #FFFFFF;
        border-radius: 8px;
    }
    QStackedWidget > QWidget{
        border: none;
    }
    QStackedWidget > QTabWidget{
        border: none;
    }   
""")
###########################################################
#Vuln Result
###########################################################

vulntitlestylesheet = ("""
    font-size: 25px; 
    font: bold; 
    background: #F4F9FF; 
    text-align: left;
    border-bottom: 2px solid #6488EA;
    border-radius: 8px;
    """)
#Collaspe content
vulncontentstylesheet = ("""
    font-size: 14px; 
    font: bold; 
    background: transparent; 
    text-align: left;
    border: None;
    """)

vulgridstylesheet = ("""
    QWidget {
        background: #FFFFFF;
        border-bottom: 2px solid #6488EA;
        border-radius: 9px;
        padding: 10px; 
    }
                       
    QPlainTextEdit {
        font-size: 16px;
        border: 2px solid #6488EA;
        background: #F5F9FF;
        selection-background-color: #6488EA;
        selection-color: #FFFFFF;
        padding: 0px;
        margin: 0px;
    }
                     
    QPlainTextEdit QAbstractScrollArea::viewport {
        margin: 0px;
        padding: 0px;
        border: 0px;
    }
                     
    QPlainTextEdit QScrollBar:vertical {
        background: #E8EEF4;
        width: 20px !important; 
        min-width: 16px !important;
        border: none;
        margin: 0px;
        border-radius: 0px;
        padding: 0px;
    }
    
    QPlainTextEdit QScrollBar::handle:vertical {
        background: #6488EA;
        min-height: 20px;
        min-width: 16px !important;
        border-radius: 0px;
        border: none;
        padding: 0px;
    }
    
    QPlainTextEdit QScrollBar::handle:vertical:hover {
        background: #0D6EFD;
        min-width: 16px !important; 
    }
    
    QPlainTextEdit QScrollBar:horizontal {
        background: #E8EEF4;
        height: 20px !important; 
        min-height: 15px !important;
        border: none;
        margin: 0px;
        border-radius: 0px;
        padding: 0px;
    }
    
    QPlainTextEdit QScrollBar::handle:horizontal {
        background: #6488EA;
        min-width: 30px;
        min-height: 15px !important;
        border-radius: 0px;
        border: none;
        padding: 0px;
    }
    
    QPlainTextEdit QScrollBar::handle:horizontal:hover {
        background: #0D6EFD;
        min-height: 15px !important;
    }
    
    QPlainTextEdit QScrollBar::add-line:vertical,
    QPlainTextEdit QScrollBar::sub-line:vertical,
    QPlainTextEdit QScrollBar::add-line:horizontal,
    QPlainTextEdit QScrollBar::sub-line:horizontal {
        height: 0px;
        width: 0px;
        border: none;
        background: none;
    }
    
    QPlainTextEdit QScrollBar::add-page:vertical,
    QPlainTextEdit QScrollBar::sub-page:vertical,
    QPlainTextEdit QScrollBar::add-page:horizontal,
    QPlainTextEdit QScrollBar::sub-page:horizontal {
        background: none;
        border: none;
    }
""")

toolbtnstylesheet = ("""
    QToolButton{
        background: #6488EA;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }
    QToolButton:hover{
        background: #FFFFFF;
        color: #6488EA;
        border-bottom: 2px solid #6488EA;
        border-radius: 8px;
    }            
    """)
#######################################################################
help
#######################################################################
help_text = ("""
    QTextEdit{
        margin-left: 5px;
        margin-top: 5px;
    }
    QTextEdit QAbstractScrollArea::viewport {
        margin: 0px;
        padding: 0px;
        border: 0px;
    }
                     
    QTextEdit QScrollBar:vertical {
        background: #E8EEF4;
        width: 5px !important; 
        min-width: 16px !important;
        border: none;
        margin: 0px;
        border-radius: 0px;
        padding: 0px;
    }
    
    QTextEdit QScrollBar::handle:vertical {
        background: #6488EA;
        min-height: 20px;
        min-width: 16px !important;
        border-radius: 0px;
        border: none;
        padding: 0px;
    }
    
    QTextEdit QScrollBar::handle:vertical:hover {
        background: #0D6EFD;
        min-width: 16px !important; 
    }
    
    QTextEdit QScrollBar:horizontal {
        background: #E8EEF4;
        height: 5px !important; 
        min-height: 15px !important;
        border: none;
        margin: 0px;
        border-radius: 0px;
        padding: 0px;
    }
    
    QTextEdit QScrollBar::handle:horizontal {
        background: #6488EA;
        min-width: 30px;
        min-height: 15px !important;
        border-radius: 0px;
        border: none;
        padding: 0px;
    }
    
    QTextEdit QScrollBar::handle:horizontal:hover {
        background: #0D6EFD;
        min-height: 15px !important;
    }
    
    QTextEdit QScrollBar::add-line:vertical,
    QTextEdit QScrollBar::sub-line:vertical,
    QTextEdit QScrollBar::add-line:horizontal,
    QTextEdit QScrollBar::sub-line:horizontal {
        height: 0px;
        width: 0px;
        border: none;
        background: none;
    }
    
    QTextEdit QScrollBar::add-page:vertical,
    QTextEdit QScrollBar::sub-page:vertical,
    QTextEdit QScrollBar::add-page:horizontal,
    QTextEdit QScrollBar::sub-page:horizontal {
        background: none;
        border: none;
    }
    """)
#######################################################################
combo_all = ("""

    QComboBox QAbstractItemView{
        outline: none;
        background: #FFFFFF;
    }

    QComboBox QAbstractItemView::item:selected{
        color: #000000;
        background: rgba(184, 219, 255, 0.4);
        font: bold;
        font-size: 16px;
        border-left: 5px solid #6488EA;
    }
             
    QComboBox QScrollBar:vertical{
        background: #FFFFFF;
        width: 15px;
        margin: 0px;
        border: none;
    }
             
    QComboBox QScrollBar::handle:vertical{
        background: #6488EA;
        border-radius: 6px;
        border: none;
        min-height: 20px;
    }
             
    QComboBox QScrollBar::handle:vertical:hover {
        background: #a0a0a0;
    }
    
    QComboBox QScrollBar::add-line:vertical, 
    QComboBox QScrollBar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px;
    }
    
    QComboBox QScrollBar::add-page:vertical, 
    QComboBox QScrollBar::sub-page:vertical {
        background: none;
    } 
""")

radiobtn = ("""
    QRadioButton {
        border-radius: 8px;
        border: solid 5px #E3E9FB;
    }
    QRadioButton::checked {
        background: rgba(143, 201, 255, 0.2);
    }
    QRadioButton::indicator {
        border-radius: 8px;
        border: solid 5px #13348C;
    }
    
    QRadioButton::indicator:unchecked {
        border: solid 5px #13348C;
        background-color: #E3E9FB;
    }
    
    QRadioButton::indicator:checked {
        border: 2px solid #FFFFFF;
        background-color: #6488EA;
    }
""")

collapse_section = ("""
    QWidget {
        border: None; 
        background: transparent;
    }
    QRadioButton {
        border-radius: 8px;
        border: solid 5px #E3E9FB;
    }
    QRadioButton::checked {
        background: rgba(143, 201, 255, 0.2);
    }
    QRadioButton::indicator {
        border-radius: 8px;
        border: solid 5px #13348C;
    }
    
    QRadioButton::indicator:unchecked {
        border: solid 5px #13348C;
        background-color: #E3E9FB;
    }
    
    QRadioButton::indicator:checked {
        border: 2px solid #FFFFFF;
        background-color: #6488EA;
    }
""")

error_msg = ("""
    QMessageBox{
        background: #F5F9FF;
    }
    QMessageBox QLabel{
        color: #000000;
        background: transparent;
        font-size: 16px;
        font: bold;
        qproperty-alignment: AlignCenter;
    }
    QMessageBox QPushButton{
        background: #6488EA;
        color: #FFFFFF;
        font-size: 16px;
        font: bold;
        text-align: center;
        border-radius: 8px;
        min-width: 75px;
        min-height: 40px;
        margin-left: auto;
        margin-right: auto;
    }
    QMessageBox QPushButton:hover{
        background: #FFFFFF;
        color: #6488EA;
        border-radius: 8px;
    }
    """)
resbtnstylesheet = ("""
    QPushButton{
        background: #89C1A9;
        color: #FFFFFF;
        font-size: 15px;
        font: bold;
        text-align: center;
        border-bottom: 2px solid #89C1A9;
        border-radius: 8px;
    }
    QPushButton:hover{
        background: #FFFFFF;
        color: #89C1A9;
        border-bottom: 2px solid #89C1A9;
        border-radius: 8px;
    }   
""")
