from PyQt5.QtGui import QColor, QIcon, QPixmap, QMovie

from src.Common import SystemHelper


class UITheme:
    def __init__(self):
        self.styleTabWidget = "QTabWidget::tab-bar {left: 5px;}"
        self.styleTabBar = "QTabBar::tab{background-color: #FFFFFF; min-width: 4ex; " \
                           "border: 1px solid #FFFFFF; padding: 2px; margin-left: 4px;} " \
                           "QTabBar::tab:selected{background-color: rgb(155, 191, 250); color: #000000}"

        self.styleTextButton = "QPushButton{border: 1px solid #000000; margin: 4px; background-color: transparent;} " \
                               "QPushButton::hover{background-color : rgb(192, 192, 192);}"

        self.styleIconButton = "QPushButton{border: none; margin: 0; background-color: transparent;} " \
                               "QPushButton::hover{background-color : rgb(192, 192, 192);}"

        self.styleIconCheckButton = "QPushButton{border: none; margin: 0; background-color: transparent;} " \
                                    "QPushButton::hover{background-color : rgb(192, 192, 192);}" \
                                    "QPushButton::checked{background-color : rgb(192, 192, 192);}"

        self.colorIgnore = QColor("lightGray")
        self.colorNormal = QColor("black")
        self.colorWarning = QColor("blue")
        self.colorError = QColor("red")
        self.colorMarkedBackground = QColor("lightskyblue")
        self.colorNormalBackground = QColor("ivory")
        self.cmdTipsColor = QColor("green")
        self.cmdInputColor = QColor("blue")
        self.cmdOutputColor = QColor("black")
        self.cmdErrorColor = QColor("red")

        self.iconStateError = None
        self.iconStateNotExist = None
        self.iconStateReady = None
        self.iconStateRunning = None
        self.iconStateStop = None
        self.iconTools = None
        self.iconAPKFile = None
        self.iconSymbolFile = None
        self.iconMappingFile = None
        self.iconClose = None
        self.iconCheck = None
        self.iconCopy = None
        self.iconMark = None
        self.iconDetail = None
        self.iconFolder = None
        self.iconDate = None
        self.iconLogFile = None
        self.iconLogcat = None
        self.iconCommand = None
        self.iconZoomIn = None
        self.iconZoomOut = None
        self.iconRotateClockwise = None
        self.iconRotateAnticlockwise = None

        self.iconWebex = None

        self.iconOutlook = None
        self.iconOutlookAccount = None
        self.iconOutlookFolder = None
        self.iconOutlookEmail = None
        self.iconOutlookDate = None

        self.iconDump = None
        self.iconThread = None
        self.iconCallStack = None

        self.gifLoading = None
        self.gifLoading24 = None
        self.gifLoading40 = None

        self.widgetTracerListFontSize = 11
        if SystemHelper.isMac():
            self.widgetTracerListFontSize = 14

        self.stringAppTips = "Ctrl + H: help"
        return

    def initRC(self):
        self.iconStateError = QIcon(QPixmap(":/icon/icons/state_error.svg"))
        self.iconStateNotExist = QIcon(QPixmap(":/icon/icons/state_not_exist.svg"))
        self.iconStateReady = QIcon(QPixmap(":/icon/icons/state_ready.svg"))
        self.iconStateRunning = QIcon(QPixmap(":/icon/icons/state_running.svg"))
        self.iconStateStop = QIcon(QPixmap(":/icon/icons/state_stop.svg"))
        self.iconTools = QIcon(QPixmap(":/icon/icons/tools.svg"))
        self.iconAPKFile = QIcon(QPixmap(":/icon/icons/apk_file.svg"))
        self.iconSymbolFile = QIcon(QPixmap(":/icon/icons/symbol_file.svg"))
        self.iconMappingFile = QIcon(QPixmap(":/icon/icons/mapping_file.svg"))
        self.iconClose = QIcon(QPixmap(":/icon/icons/bt_close.svg"))
        self.iconCheck = QIcon(QPixmap(":/icon/icons/check.svg"))
        self.iconCopy = QIcon(QPixmap(":/icon/icons/copy.svg"))
        self.iconMark = QIcon(QPixmap(":/icon/icons/mark.svg"))
        self.iconDetail = QIcon(QPixmap(":/icon/icons/detail.svg"))
        self.iconFolder = QIcon(QPixmap(":/icon/icons/folder.svg"))
        self.iconDate = QIcon(QPixmap(":/icon/icons/date.svg"))
        self.iconLogFile = QIcon(QPixmap(":/icon/icons/log_file.svg"))
        self.iconLogcat = QIcon(QPixmap(":/icon/icons/logcat.svg"))
        self.iconCommand = QIcon(QPixmap(":/icon/icons/command.svg"))
        self.iconZoomIn = QIcon(QPixmap(":/icon/icons/zoom_in.svg"))
        self.iconZoomOut = QIcon(QPixmap(":/icon/icons/zoom_out.svg"))
        self.iconRotateClockwise = QIcon(QPixmap(":/icon/icons/rotate_clockwise.svg"))
        self.iconRotateAnticlockwise = QIcon(QPixmap(":/icon/icons/rotate_anticlockwise.svg"))

        self.iconWebex = QIcon(QPixmap(":/icon/icons/webex.svg"))

        self.iconOutlook = QIcon(QPixmap(":/icon/icons/outlook.svg"))
        self.iconOutlookAccount = QIcon(QPixmap(":/icon/icons/outlook_account.svg"))
        self.iconOutlookFolder = QIcon(QPixmap(":/icon/icons/outlook_folder.svg"))
        self.iconOutlookEmail = QIcon(QPixmap(":/icon/icons/outlook_email.svg"))
        self.iconOutlookDate = QIcon(QPixmap(":/icon/icons/outlook_date.svg"))

        self.iconDump = QIcon(QPixmap(":/icon/icons/dump.svg"))
        self.iconThread = QIcon(QPixmap(":/icon/icons/thread.svg"))
        self.iconCallStack = QIcon(QPixmap(":/icon/icons/call_stack.svg"))

        self.gifLoading = QMovie(":/gif/gifs/loading.gif")
        self.gifLoading24 = QMovie(":/gif/gifs/loading_24.gif")
        self.gifLoading40 = QMovie(":/gif/gifs/loading_40.gif")
        return


uiTheme = UITheme()
