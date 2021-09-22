import re
import zipfile
from functools import partial

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QIcon, QMouseEvent, QEnterEvent
from PyQt5.QtWidgets import QDialog, QWidget, QPushButton, QTabBar

from src.Common import Const, QTHelper
from src.Common.Logger import Logger
from src.Layout.dialogNormalLogs import Ui_Dialog

from src.Common.UITheme import uiTheme
from src.Model.AppModel import appModel
from src.View.ViewDumpFile import ViewDumpFile
from src.View.ViewPicture import ViewPicture
from src.View.ViewWBXTraceFile import ViewWBXTraceFile


class DialogNormalLogs(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(DialogNormalLogs, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self.mLastHoverIndex = -1
        self.mTabBar = self.tabAttachments.tabBar()
        self.mTabBar.setMouseTracking(True)
        self.mTabBar.installEventFilter(self)
        self.mViewPath = {}
        self.tabAttachments.currentChanged.connect(self._onChangeTab)

        QTHelper.handleWndPos(self, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        self._removeAllTabViews()
        QTHelper.handleWndPos(self, False)

    def eventFilter(self, source: QObject, event: QtCore.QEvent):
        eventType = event.type()
        # Logger.i(appModel.getAppTag(), f"source = {source}, eventType = {eventType}")
        if source == self.mTabBar:
            if eventType == QtCore.QEvent.MouseButtonPress:
                mouse = QMouseEvent(event)
                tabIndex = self.mTabBar.tabAt(mouse.pos())
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

        return super(QDialog, self).eventFilter(source, event)

    def _onChangeTab(self, index):
        Logger.i(appModel.getAppTag(), f"cur sel= {index} - {self}")
        view = self.tabAttachments.widget(index)
        if view in self.mViewPath:
            self.setWindowTitle(self.mViewPath[view])
        else:
            self.setWindowTitle("")
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

    def addFileView(self, path):
        existIndex = self._findViewFromPath(path)
        if existIndex >= 0:
            self.tabAttachments.setCurrentIndex(existIndex)
            return

        import os
        pathSplit = path.split("?")
        specialSubFileName = ""
        if len(pathSplit) > 1:
            path = pathSplit[0]
            specialSubFileName = pathSplit[1]

        fileName = os.path.basename(path)
        if re.search(r".zip$", path, flags=re.IGNORECASE):
            if not zipfile.is_zipfile(path):
                return
            zipFile = zipfile.ZipFile(path)
            for subFileName in zipFile.namelist():
                if len(specialSubFileName) > 0 and specialSubFileName != subFileName:
                    continue
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

    def _findViewFromPath(self, viewPath: str) -> int:
        for index in range(0, self.tabAttachments.count()):
            view = self.tabAttachments.widget(index)
            if view in self.mViewPath:
                if self.mViewPath[view] == viewPath:
                    return index
        return -1

    def _addTabView(self, view: QWidget, icon: QIcon, title: str, viewPath: str):
        index = self.tabAttachments.count() - 1
        if index < 0:
            index = 0
        self.tabAttachments.insertTab(index, view, icon, title)
        self.tabAttachments.setCurrentWidget(view)
        btClose = QPushButton()
        btClose.setMinimumSize(QtCore.QSize(24, 24))
        btClose.setMaximumSize(QtCore.QSize(24, 24))
        btClose.setIcon(uiTheme.iconClose)
        btClose.setIconSize(QtCore.QSize(16, 16))
        btClose.clicked.connect(partial(self._onTabClose, view))
        self.mTabBar.setTabButton(index, QTabBar.RightSide, btClose)
        btClose.hide()
        if len(viewPath) > 0:
            viewPath = title
        viewPath = viewPath.replace(appModel.mAppPath, ".")
        self.mViewPath[view] = viewPath
        self.setWindowTitle(self.mViewPath[view])
        return view

    def _onTabClose(self, view: QWidget):
        index = self.tabAttachments.indexOf(view)
        Logger.i(appModel.getAppTag(), f"index = {index}")
        self._removeTabView(index)
        return

    def _removeTabView(self, index):
        if index < 0:
            return
        view = self.tabAttachments.widget(index)
        view.close()
        if view in self.mViewPath:
            del self.mViewPath[view]
        self.tabAttachments.removeTab(index)
        if index-1 < 0:
            self.tabAttachments.setCurrentIndex(index)
        else:
            self.tabAttachments.setCurrentIndex(index-1)
        return

    def _removeAllTabViews(self):
        for index in range(0, self.tabAttachments.count()):
            view = self.tabAttachments.widget(index)
            view.close()
            if view in self.mViewPath:
                del self.mViewPath[view]
        self.tabAttachments.clear()
        return
