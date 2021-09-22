import sys
from functools import partial

import psutil
import re
import zipfile

import pyperclip
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, Qt, QTimer, QMimeData, QByteArray
from PyQt5.QtGui import QMouseEvent, QPalette, QDragEnterEvent, QContextMenuEvent, QCursor, QIcon, QEnterEvent, \
    QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMenu, QTabBar, QPushButton, QLineEdit

from src.Common import QTHelper, SystemHelper
from src.Common.Logger import *
from src.Common.SystemHelper import SelfProcessInfo
from src.Common.UITheme import uiTheme
from src.Model.AppModel import appModel

from src.Layout.androidBoy import Ui_Form

from src.View.ViewCCTGManager import ViewCCTGManager
from src.View.ViewLogcat import ViewLogcat
from src.View.ViewADBCommands import ViewADBCommands
from src.View.ViewOutlookDetector import ViewOutlookDetector
from src.View.ViewPicture import ViewPicture
from src.View.ViewWBXTraceFile import ViewWBXTraceFile
from src.View.ViewDumpFile import ViewDumpFile
from src.View.ViewTraceParser import ViewTraceParser
from src.View.ViewJsonFormat import ViewJsonFormat


class AndroidBoy(QWidget, Ui_Form):
    def __init__(self):
        import os
        self.app = QApplication(sys.argv)
        self.app.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.Ceil)
        super(AndroidBoy, self).__init__(None)
        Logger.i(appModel.getAppTag(), "Start application")
        # self._handlePalette()
        self.setupUi(self)
        QTHelper.switchMacUI(self)
        uiTheme.initRC()

        self.mTabBar = self.tabMain.tabBar()
        self.mTabBar.setMouseTracking(True)
        self.mViewPath = {}
        self.mEditTabName = QLineEdit(self.mTabBar)
        self.mEditTabName.hide()

        self._mStatusTimer = QTimer()
        self._mDropFiles = []

        viewLogo = ViewPicture(self)
        viewLogo.openPictureFile(os.path.join(appModel.mLayoutPath, "pngs", "android_boy.png"))
        viewLogo.setScaleRation(0.5)
        self.tabMain.addTab(viewLogo, "+")
        self.mLastHoverIndex = -1

        if appModel.readConfig(self.__class__.__name__, "enableCCTGManagerView", False):
            self._addTabView(ViewCCTGManager(self), uiTheme.iconWebex, "CCTGManager", "")
        if appModel.readConfig(self.__class__.__name__, "enableLogcatView", False):
            self._addTabView(ViewLogcat(self), uiTheme.iconLogcat, "LogcatView", "")
        if appModel.readConfig(self.__class__.__name__, "enableADBCommandsView", False):
            self._addTabView(ViewADBCommands(self), uiTheme.iconCommand, "ADB Commands", "")
        if appModel.readConfig(self.__class__.__name__, "enableOutlookDetector", False):
            self._addTabView(ViewOutlookDetector(self), uiTheme.iconOutlook, "OutlookDetector", "")

        self.tabMain.currentChanged.connect(self._onChangeTab)
        self.mTabBar.installEventFilter(self)
        self.mEditTabName.installEventFilter(self)
        QTHelper.handleWndPos(self, True)
        self._bindEvent()

        QTHelper.showLayout(self.TestButtonsLayout, False)
        self._mStatusTimer.start(2000)
        self.show()

        self.app.exec_()
        Logger.i(appModel.getAppTag(), "Exit application")
        sys.exit()

    def _onChangeTab(self, index):
        Logger.i(appModel.getAppTag(), f"cur sel= {index} - {self}")
        view = self.tabMain.widget(index)
        if view in self.mViewPath:
            self.setWindowTitle(appModel.getAppName() + " - " + self.mViewPath[view])
        else:
            self.setWindowTitle(appModel.getAppName())
        return

    def _setHoverItem(self, index):
        if self.mLastHoverIndex == index:
            return
        if self.mLastHoverIndex >= 0:
            button = self.mTabBar.tabButton(self.mLastHoverIndex, QTabBar.RightSide)
            if button is not None:
                button.hide()
        self.mLastHoverIndex = index
        if self.mLastHoverIndex >= 0:
            button = self.mTabBar.tabButton(self.mLastHoverIndex, QTabBar.RightSide)
            if button is not None:
                button.show()
        return

    def _openSelectTraceFileDialog(self):
        import os
        title = "Select trace file"
        startDir = appModel.readConfig(self.__class__.__name__, "startSelectDir", "")
        typeFilter = f"All Files ({Const.logFileSuffix} {Const.zipFileSuffix} {Const.imageFileSuffix})"
        typeFilter += f";;Log Files ({Const.logFileSuffix})"
        typeFilter += f";;Zip Files ({Const.zipFileSuffix})"
        typeFilter += f";;Image Files ({Const.imageFileSuffix})"
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,
                                                caption=title,
                                                directory=startDir,
                                                filter=typeFilter,
                                                options=options)
        for selFile in files:
            fileDir = os.path.dirname(selFile)
            appModel.saveConfig(self.__class__.__name__, "startSelectDir", fileDir)
            Logger.i(appModel.getAppTag(), f"will open: {selFile}")
            self.addFileView(selFile)
        return

    def eventFilter(self, source: QObject, event: QtCore.QEvent):
        eventType = event.type()
        # Logger.i(appModel.getAppTag(), f"source = {source}, eventType = {eventType}")
        if source == self.mTabBar:
            if eventType == QtCore.QEvent.MouseButtonPress:
                mouse = QMouseEvent(event)
                tabIndex = self.mTabBar.tabAt(mouse.pos())
                if tabIndex == self.tabMain.count() - 1:
                    self._MenuForAdd(
                        QContextMenuEvent(QContextMenuEvent.Mouse, QCursor().pos()))
                    return True

                if mouse.button() == QtCore.Qt.MiddleButton:
                    self._removeTabView(tabIndex)
            elif eventType == QtCore.QEvent.Enter:
                enter = QEnterEvent(event)
                index = self.mTabBar.tabAt(enter.pos())
                self._setHoverItem(index)
            elif eventType == QtCore.QEvent.MouseMove:
                mouse = QMouseEvent(event)
                index = self.mTabBar.tabAt(mouse.pos())
                self._setHoverItem(index)
                return True
            elif eventType == QtCore.QEvent.Leave:
                self._setHoverItem(-1)
        elif source == self.mEditTabName:
            if eventType == QtCore.QEvent.FocusOut:
                self.mEditTabName.hide()
            elif eventType == QtCore.QEvent.KeyRelease:
                keyEvent = QKeyEvent(event)
                key = keyEvent.key()
                if key == QtCore.Qt.Key_Escape:
                    self.mEditTabName.hide()

        return super(AndroidBoy, self).eventFilter(source, event)

    def _MenuForAdd(self, event: QContextMenuEvent):
        menu = QMenu()
        actionOutlook = menu.addAction(uiTheme.iconOutlook, "Outlook detector")
        actionLogFile = menu.addAction(uiTheme.iconLogFile, "Log file")
        actionClipboard = menu.addAction(uiTheme.iconLogFile, "Log From Clipboard")
        actionADBLogcat = menu.addAction(uiTheme.iconLogcat, "ADB Logcat")
        actionADBCommand = menu.addAction(uiTheme.iconCommand, "ADB Command")
        actionTracerParser = menu.addAction(uiTheme.iconLogFile, "Trace Parser")
        actionCCTGDownloader = menu.addAction(uiTheme.iconWebex, "CCTGDownloader")

        menuFolder = menu.addMenu(uiTheme.iconFolder, "Folders")
        actionAssetsFolder = menuFolder.addAction(uiTheme.iconFolder, "Assets Folder")
        actionLogsFolder = menuFolder.addAction(uiTheme.iconFolder, "Log Folder")
        actionOutlookFolder = menuFolder.addAction(uiTheme.iconFolder, "Outlook Detector Folder")
        actionSymbolsFolder = menuFolder.addAction(uiTheme.iconFolder, "Symbols Folder")
        action = menu.exec_(event.pos())

        view = None
        if action is None:
            return
        elif action == actionOutlook:
            view = self._getViewByType(ViewOutlookDetector.__name__)
            if view is None:
                self._addTabView(ViewOutlookDetector(self), uiTheme.iconOutlook, "OutlookDetector", "")
        elif action == actionLogFile:
            self._openSelectTraceFileDialog()
        elif action == actionClipboard:
            view = ViewWBXTraceFile(self)
            view.openTraceData(pyperclip.paste(), view.DATA_LGF)
            self._addTabView(view, uiTheme.iconLogcat, "Clipboard", "")
        elif action == actionADBLogcat:
            view = self._getViewByType(ViewLogcat.__name__)
            if view is None:
                self._addTabView(ViewLogcat(self), uiTheme.iconLogcat, "LogcatView", "")
        elif action == actionADBCommand:
            view = self._getViewByType(ViewADBCommands.__name__)
            if view is None:
                self._addTabView(ViewADBCommands(self), uiTheme.iconCommand, "ADB Commands", "")
        elif action == actionTracerParser:
            view = self._getViewByType(ViewTraceParser.__name__)
            if view is None:
                self._addTabView(ViewTraceParser(self), uiTheme.iconLogcat, "Trace Parser", "")
        elif action == actionCCTGDownloader:
            view = self._getViewByType(ViewCCTGManager.__name__)
            if view is None:
                self._addTabView(ViewCCTGManager(self), uiTheme.iconWebex, "CCTGManager", "")
        elif action == actionAssetsFolder:
            SystemHelper.openAtExplorer(appModel.mAssetsPath)
            return
        elif action == actionLogsFolder:
            SystemHelper.openAtExplorer(appModel.getDefaultLogFolder())
            return
        elif action == actionOutlookFolder:
            SystemHelper.openAtExplorer(ViewOutlookDetector.sLocalFolderBase)
            return
        elif action == actionSymbolsFolder:
            SystemHelper.openAtExplorer(ViewOutlookDetector.sSymbolFolderBase)
            return
        if view is not None:
            self.tabMain.setCurrentWidget(view)
        return

    def _handlePalette(self):
        pal = self.palette()
        pal.setColor(QPalette.Background, Qt.white)
        # self.setAutoFillBackground(True)
        self.setPalette(pal)
        return

    def _bindEvent(self):
        self.mTabBar.tabBarDoubleClicked.connect(self._onTabDoubleClicked)
        self.mEditTabName.returnPressed.connect(self._onChangeTabItemName)
        self._mStatusTimer.timeout.connect(self._onStatusTimer)
        self._onStatusTimer()
        return

    def _onChangeTabItemName(self):
        self.mTabBar.setTabText(self.mTabBar.currentIndex(), self.mEditTabName.text())
        self.mEditTabName.hide()
        return

    def _onTabClose(self, view: QWidget):
        index = self.tabMain.indexOf(view)
        Logger.i(appModel.getAppTag(), f"index = {index}")
        self._removeTabView(index)
        return

    def _onTabDoubleClicked(self, index: int):
        if index == self.tabMain.count() - 1:
            return
        itemRect = self.mTabBar.tabRect(index)
        itemRect.adjust(28, 4, -28, -4)
        self.mEditTabName.setGeometry(itemRect)
        self.mEditTabName.setText(self.mTabBar.tabText(index))
        self.mEditTabName.selectAll()
        self.mEditTabName.show()
        self.mEditTabName.setFocus()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        appModel.saveConfig(self.__class__.__name__,
                            "enableCCTGManagerView", self._getViewByType(ViewCCTGManager.__name__) is not None)
        appModel.saveConfig(self.__class__.__name__,
                            "enableLogcatView", self._getViewByType(ViewLogcat.__name__) is not None)
        appModel.saveConfig(self.__class__.__name__,
                            "enableADBCommandsView", self._getViewByType(ViewADBCommands.__name__) is not None)
        appModel.saveConfig(self.__class__.__name__,
                            "enableOutlookDetector", self._getViewByType(ViewOutlookDetector.__name__) is not None)

        self._removeAllTabViews()
        QTHelper.handleWndPos(self, False)

        appModel.storeConfig()
        super(AndroidBoy, self).closeEvent(event)
        return

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime: QMimeData = event.mimeData()
        if not mime.hasUrls():
            fmts = mime.formats()
            if len(fmts) == 0:
                Logger.i(appModel.getAppTag(), f"No format data.")
                event.accept()
            else:
                for fmt in mime.formats():
                    content: QByteArray = mime.data(fmt)
                    Logger.i(appModel.getAppTag(), f"  {fmt} data len = {len(content)}")
                event.ignore()
            return
        for url in mime.urls():
            path = url.toLocalFile()
            if re.search(fr"{Const.allSupportRegular}$", path, flags=re.IGNORECASE):
                self._mDropFiles.append(path)
                Logger.i(appModel.getAppTag(), f"accept={path}")
            else:
                Logger.w(appModel.getAppTag(), f"ignore:{path}")
        if len(self._mDropFiles) > 0:
            event.accept()
        else:
            event.ignore()
        return

    def dragMoveEvent(self, event: QDragEnterEvent):
        # Logger.i(appModel.getAppTag(), "")
        return

    def dropEvent(self, event: QDragEnterEvent):
        mime: QMimeData = event.mimeData()
        for url in mime.urls():
            path = url.toLocalFile()
            if re.search(fr"{Const.allSupportRegular}$", path, flags=re.IGNORECASE):
                Logger.i(appModel.getAppTag(), f"will open: {path}")
                self.addFileView(path)
        self._mDropFiles = []
        return

    def addFileView(self, path):
        import os
        fileName = os.path.basename(path)
        if re.search(r".zip$", path, flags=re.IGNORECASE):
            if not zipfile.is_zipfile(path):
                return
            zipFile = zipfile.ZipFile(path)
            for subFileName in zipFile.namelist():
                title = subFileName
                if re.search(r".wbt$", subFileName, flags=re.IGNORECASE):
                    Logger.i(appModel.getAppTag(), f"will open: {subFileName} in {fileName}")
                    fileData = zipFile.read(subFileName)
                    view = ViewWBXTraceFile(self)
                    view.openTraceData(fileData, view.DATA_WBT)
                elif re.search(r".lgf|.txt$", subFileName, flags=re.IGNORECASE):
                    Logger.i(appModel.getAppTag(), f"will open: {subFileName} in {fileName}")
                    fileData = zipFile.read(subFileName).decode("utf-8", "ignore")  # string only
                    view = ViewWBXTraceFile(self)
                    view.openTraceData(fileData, view.DATA_LGF)
                elif re.search(r".dmp$", subFileName, flags=re.IGNORECASE):
                    Logger.i(appModel.getAppTag(), f"will open: {subFileName} in {fileName}")
                    fileData = zipFile.read(subFileName)
                    view = ViewDumpFile(self)
                    view.openDumpData(fileData, title)
                elif re.search(fr"{Const.imageFileRegular}$",
                               subFileName, flags=re.IGNORECASE):
                    fileData = zipFile.read(subFileName)
                    view = ViewPicture(self)
                    view.openPictureData(fileData)
                else:
                    continue
                self._addTabView(view, uiTheme.iconLogFile, title, path + "?" + subFileName)
        else:
            title = fileName
            if re.search(r".wbt$", path, flags=re.IGNORECASE):
                view = ViewWBXTraceFile(self)
                view.openTraceFile(path, view.DATA_WBT)
            elif re.search(r".lgf|.txt$", path, flags=re.IGNORECASE):
                view = ViewWBXTraceFile(self)
                view.openTraceFile(path, view.DATA_LGF)
            elif re.search(r".dmp$", path, flags=re.IGNORECASE):
                view = ViewDumpFile(self)
                view.openDumpFile(path)
            elif re.search(fr"{Const.imageFileRegular}$",
                           path, flags=re.IGNORECASE):
                view = ViewPicture(self)
                view.openPictureFile(path)
            else:
                Logger.e(appModel.getAppTag(), f"unknown file type: {path}")
                return
            self._addTabView(view, uiTheme.iconLogFile, title, path)
        return

    def _addTabView(self, view: QWidget, icon: QIcon, title: str, viewPath: str):
        index = self.tabMain.count() - 1
        if index < 0:
            index = 0
        self.tabMain.insertTab(index, view, icon, title)
        self.tabMain.setCurrentWidget(view)
        btClose = QPushButton()
        btClose.setMinimumSize(QtCore.QSize(24, 24))
        btClose.setMaximumSize(QtCore.QSize(24, 24))
        btClose.setIcon(uiTheme.iconClose)
        btClose.setIconSize(QtCore.QSize(16, 16))
        btClose.clicked.connect(partial(self._onTabClose, view))
        self.mTabBar.setTabButton(index, QTabBar.RightSide, btClose)
        btClose.hide()
        if len(viewPath) == 0:
            viewPath = title
        viewPath = viewPath.replace(appModel.mAppPath, ".")
        self.mViewPath[view] = viewPath
        self.setWindowTitle(appModel.getAppName() + " - " + self.mViewPath[view])
        return view

    def _removeTabView(self, index):
        if index < 0:
            return
        if index == self.tabMain.count() - 1:
            return
        view = self.tabMain.widget(index)
        view.close()
        if view in self.mViewPath:
            del self.mViewPath[view]
        self.tabMain.removeTab(index)
        if index-1 < 0:
            self.tabMain.setCurrentIndex(index)
        else:
            self.tabMain.setCurrentIndex(index-1)
        return

    def _removeAllTabViews(self):
        for index in range(0, self.tabMain.count()):
            view = self.tabMain.widget(index)
            view.close()
            if view in self.mViewPath:
                del self.mViewPath[view]
        self.tabMain.clear()
        return

    def _getViewByType(self, typeName: str):
        for index in range(0, self.tabMain.count()):
            view = self.tabMain.widget(index)
            if view.__class__.__name__ == typeName:
                return view
        return None

    def _onStatusTimer(self):
        # cpu_usage = 0
        cpu_usage = SelfProcessInfo.getSelfCPU()

        mem_available = psutil.virtual_memory().available
        mem_available = round(mem_available / 1024 / 1024, 2)

        mem_process = SelfProcessInfo.getSelfMemory()

        statusText = f"CPU:{cpu_usage:.2f}%" \
                     f"  Memory:{mem_process} MB" \
                     f"  Available:{mem_available} MB"
        self.lbStatus.setText(f"{statusText:60s}" + uiTheme.stringAppTips)
        return
