import re
import threading

import pyperclip
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer, QObject
from PyQt5.QtGui import QColor, QKeyEvent, QContextMenuEvent, QFont
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu, QAbstractItemView

from src.Common import QTHelper, DateTimeHelper
from src.Common.Logger import *
from src.Common.QTHelper import ListForQLineEdit
from src.Common.UITheme import uiTheme
from src.Model.AppModel import appModel
from src.Layout.widgetTracerList import Ui_Form

from src.View.DialogScrollTo import DialogScrollTo
from src.View.DialogGlobalFilter import DialogGlobalFilter
from src.View.WidgetNotify import WidgetNotify
from src.View.DialogTraceDetail import DialogTraceDetail


class TracerLine:
    col_count = 6

    def __init__(self, index: int, timeStr: str, pid: str, tid: str,
                 level: LoggerLevel, levelStr: str, tag: str,
                 message: str, color: QColor):
        self.mIndex = index
        self.mTimeStr = timeStr
        self.mPID = pid
        self.mTID = tid
        self.mLevel = level
        self.mLevelStr = levelStr
        self.mTag = f"{tag}"
        self.mMessage = message
        self.mColor = color
        self.mVisual = True
        self.mMarked = False
        return

    def getSelectedCols(self, colsVisual: [bool]):
        if colsVisual is None:
            return self.getFullText()

        text = ""
        if colsVisual[0]:
            text += f"{self.mIndex:<7}"
        if colsVisual[1]:
            text += f"{self.mTimeStr:25.24s}"
        if colsVisual[2]:
            text += f"{self.mPID:7.6s}"
        if colsVisual[3]:
            text += f"{self.mTID:7.6s}"
        if colsVisual[4]:
            text += f"{self.mLevelStr:11.10s}"
        if colsVisual[5]:
            text += f"{self.mTag:21.20s}"
        text += f"{self.mMessage:.128s}"
        return text

    def getFullText(self):
        return f"{self.mIndex:<7}" \
               f"{self.mTimeStr:25.24s}" \
               f"{self.mPID:7.6s}" \
               f"{self.mTID:7.6s}" \
               f"{self.mLevelStr:11.10s}" \
               f"{self.mTag:21.20s}" \
               f"{self.mMessage}"


class WidgetTracerList(QWidget, Ui_Form):
    getLevelStr = {
        LoggerLevel.Verbose: "Verbos",
        LoggerLevel.Debug: "Debug",
        LoggerLevel.Info: "Info",
        LoggerLevel.Warning: "Warning",
        LoggerLevel.Error: "Error",
        LoggerLevel.Fatal: "Fatal",
        LoggerLevel.Silent: "Silent",
    }
    getLevelColor = {
        LoggerLevel.Verbose: QColor(Qt.black),
        LoggerLevel.Debug: QColor(Qt.black),
        LoggerLevel.Info: QColor(Qt.black),
        LoggerLevel.Warning: QColor(Qt.blue),
        LoggerLevel.Error: QColor(Qt.red),
        LoggerLevel.Fatal: QColor(Qt.red),
        LoggerLevel.Silent: QColor(Qt.red),
    }

    _mEventBeginLoad = QtCore.pyqtSignal(QObject, int)  # len
    _mEventEndLoad = QtCore.pyqtSignal(QObject)

    def __init__(self, parent, configName, addable=False):
        super(WidgetTracerList, self).__init__(parent)
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self._mAddable = addable
        self._mConfigName = configName
        self._mColsVisual = appModel.readConfig(self._mConfigName, "ColsVisual",
                                                [True, True, True, True, True, True])
        self._mUpdateTimer = QTimer()
        self._mLastReadLine = 0
        self._mLastFilterRow = 0
        self._mVisualCount = 0
        self._mAllTraceLines = []
        self._mTracesModelLock = threading.RLock()

        self._mFilterLogLevel = LoggerLevel.Verbose  # base filter
        self._mFilterLogInclude = ""
        self._mFilterLogExclude = ""
        self._mFilterMarkedOnly = False

        self._mAutoScrollToBottom = True
        self._mMarkedRows = []
        self._mDetailDlg = DialogTraceDetail(self)
        self._mScrollToDlg = DialogScrollTo(self)
        self._mGlobalFilterDlg = DialogGlobalFilter(self)
        self._mNotifyWidget = WidgetNotify(parent)
        self._mNotifyWidget.close()

        self._bindEvent()
        self.listTrace.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.listTrace.setUniformItemSizes(True)
        self.listTrace.setFont(QFont('Courier New', uiTheme.widgetTracerListFontSize))
        self.listTrace.horizontalScrollBar().setHidden(True)
        self.listTrace.horizontalScrollBar().setDisabled(True)

        self._mLoading = False
        self.pbLoading.setMinimum(0)
        self.pbLoading.setTextVisible(True)
        self.pbLoading.close()

        self.showFindToolbar(False)  # hide find dialog as default
        self.starTimer()
        self.show()
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self._mUpdateTimer.timeout.connect(self._onUpdateTimer)

        self._mEventBeginLoad.connect(self._onBeginLoad)
        self._mEventEndLoad.connect(self._onEndLoad)

        self.listTrace.installEventFilter(self)
        # self.listTrace.clicked.connect(self._onSelectLogChanged)
        self.listTrace.itemSelectionChanged.connect(self._onSelectLogChanged)
        self.listTrace.doubleClicked.connect(self._onDoubleClickLog)

        self.btFindNext.clicked.connect(self.nextFind)
        self.btFindPrev.clicked.connect(self.prevFind)
        self.btHideFindToolbar.clicked.connect(self._onHideFindToolbar)
        self.tbFindContent.textChanged.connect(self._onEditorTextChanged)
        self.tbFindContent.installEventFilter(self)
        return

    def _handleKeyRelease(self, source: QObject, key: int, modifiers: int, hasControl: bool, hasShift: bool):
        retValue = False
        if source == self.listTrace:
            if key == QtCore.Qt.Key_F:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + F: Pop Find dialog
                    self.showFindToolbar(True)
                    self.tbFindContent.setFocus()
            elif key == QtCore.Qt.Key_F3:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + F3: Find prev
                    self.prevFind()
                elif modifiers == Qt.NoModifier:
                    # F3: Find next
                    self.nextFind()
            elif key == QtCore.Qt.Key_B:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + B: Mark toggle
                    self.markToggle()
            elif key == QtCore.Qt.Key_F4:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + F4: Prev mark
                    self.prevMark()
                elif modifiers == Qt.NoModifier:
                    # F4: Next mark
                    self.nextMark()
            elif key == QtCore.Qt.Key_C:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + C: Copy all logs
                    self._copyLogs(self.listTrace.selectedItems())
                elif hasControl and hasShift:
                    # Ctrl + Shift + C: Copy all message
                    self._copyMessages(self.listTrace.selectedItems())
            elif key == QtCore.Qt.Key_G:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + G: Locate line
                    self.showLocateDialog()
                elif hasControl and hasShift:
                    # Ctrl + Shift + G: Global filter
                    self.showGlobalFilterDialog()
            elif key == QtCore.Qt.Key_H:
                strTips = ""
                strTips += "Ctrl + F: Pop Find dialog" + os.linesep
                strTips += "Ctrl + F3: Find prev" + os.linesep
                strTips += "F3: Find next" + os.linesep
                strTips += "Ctrl + B: Mark toggle" + os.linesep
                strTips += "Ctrl + F4: Prev mark" + os.linesep
                strTips += "F4: Next mark" + os.linesep
                strTips += "Ctrl + C: Copy all logs" + os.linesep
                strTips += "Ctrl + Shift + C: Copy all message" + os.linesep
                strTips += "Ctrl + G: Locate line" + os.linesep
                strTips += "Ctrl + Shift + G: Global filter" + os.linesep
                self._mNotifyWidget.notify(strTips, 2)
                '''
                    # Ctrl + F: Pop Find dialog
                    # Ctrl + F3: Find prev
                    # F3: Find next
                    # Ctrl + B: Mark toggle
                    # Ctrl + F4: Prev mark
                    # F4: Next mark
                    # Ctrl + C: Copy all logs
                    # Ctrl + Shift + C: Copy all message
                    # Ctrl + G: Locate line
                    # Ctrl + Shift + G: Global filter
                '''
        elif source == self.tbFindContent:
            if key == QtCore.Qt.Key_Return:
                self.nextFind()
            else:
                retValue = True
        else:
            retValue = True

        return retValue

    def eventFilter(self, source: QObject, event: QtCore.QEvent):
        # Logger.i(appModel.getAppTag(), f"{event}")
        if event.type() != QtCore.QEvent.KeyRelease:
            return super(WidgetTracerList, self).eventFilter(source, event)

        keyEvent = QKeyEvent(event)
        key = keyEvent.key()
        modifiers = keyEvent.modifiers()
        hasControl = (modifiers & Qt.ControlModifier) == Qt.ControlModifier
        hasShift = (modifiers & Qt.ShiftModifier) == Qt.ShiftModifier
        if self._handleKeyRelease(source, key, modifiers, hasControl, hasShift):
            return super(WidgetTracerList, self).eventFilter(source, event)
        else:
            return False

    def contextMenuEvent(self, event: QContextMenuEvent):
        selItems = self.listTrace.selectedItems()

        menu = QMenu()
        if len(selItems) > 0:
            copyMsg = menu.addAction(uiTheme.iconCopy, "Copy messages only")
            copyLogs = menu.addAction(uiTheme.iconCopy, "Copy logs")
            showDetail = menu.addAction(uiTheme.iconDetail, "Show detail info")
            menu.addSeparator()
            toggleMarked = menu.addAction(uiTheme.iconMark, "Toggle marked")
        else:
            copyMsg = None
            copyLogs = None
            showDetail = None
            toggleMarked = None
        if self._mFilterMarkedOnly:
            markedOnly = None
            noMarkedOnly = menu.addAction(uiTheme.iconCheck, "Marked only")
        else:
            markedOnly = menu.addAction("Marked only")
            noMarkedOnly = None
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is None:
            return
        elif action == copyMsg:
            self._copyMessages(selItems)
        elif action == copyLogs:
            self._copyLogs(selItems)
        elif action == toggleMarked:
            Logger.i(appModel.getAppTag(), f"begin markToggle with {len(selItems)}")
            for item in selItems:
                self.markToggle(item)
            Logger.i(appModel.getAppTag(), f"end markToggle")
        elif action == markedOnly:
            self.setFilterMarkedOnly(True)
        elif action == noMarkedOnly:
            self.setFilterMarkedOnly(False)
        elif action == showDetail:
            self._mDetailDlg.show()
        return

    def _copyLogs(self, items: [QListWidgetItem]):
        if len(items) <= 0:
            return
        dataToCopy = ""
        for item in items:
            trace: TracerLine = item.data(Qt.UserRole)
            dataToCopy += trace.getFullText()
            # dataToCopy += item.text()
            dataToCopy += os.linesep
        pyperclip.copy(dataToCopy)
        self._mNotifyWidget.notify(f"Copied {len(items)} logs to clipboard", 2)
        return

    def _copyMessages(self, items: [QListWidgetItem]):
        if len(items) <= 0:
            return
        dataToCopy = ""
        for item in items:
            trace: TracerLine = item.data(Qt.UserRole)
            dataToCopy += trace.mMessage
        pyperclip.copy(dataToCopy)
        self._mNotifyWidget.notify(f"Copied {len(items)} messages to clipboard", 2)
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        appModel.saveConfig(self._mConfigName, "ColsVisual", self._mColsVisual)
        return

    def clearLog(self, clearLines=True):
        Logger.i(appModel.getAppTag(), "")
        self._mTracesModelLock.acquire()
        self.listTrace.clear()
        self._mLastReadLine = 0
        self._mLastFilterRow = 0
        self._mVisualCount = 0
        if clearLines:
            self._mAllTraceLines = []
        self.lbStatus.clear()
        self._mTracesModelLock.release()
        return

    def _onDoubleClickLog(self, QModelIndex):
        row = QModelIndex.row()
        Logger.i(appModel.getAppTag(), f"at {row}")
        trace: TracerLine = self.listTrace.item(row).data(Qt.UserRole)

        timeStr = trace.mTimeStr
        pid = trace.mPID
        tid = trace.mTID
        levelStr = trace.mLevelStr
        tag = trace.mTag
        message = trace.mMessage
        self._mDetailDlg.setTrace(timeStr, pid, tid, levelStr, tag, message)
        self._mDetailDlg.show()
        return

    def _onSelectLogChanged(self):
        selItems = self.listTrace.selectedItems()
        if len(selItems) <= 0:
            self.setAutoScroll(True)
            return

        item = selItems[0]
        curRow = self.listTrace.row(item)
        # Logger.i(appModel.getAppTag(), f"at {curRow}")
        rowCount = self.listTrace.count()
        if curRow + 1 == rowCount:
            self.setAutoScroll(True)
        else:
            self.setAutoScroll(False)

        trace: TracerLine = item.data(Qt.UserRole)
        if trace is None:
            return
        timeStr = trace.mTimeStr
        pid = trace.mPID
        tid = trace.mTID
        levelStr = trace.mLevelStr
        tag = trace.mTag
        message = trace.mMessage
        for item in selItems[1:]:
            trace: TracerLine = item.data(Qt.UserRole)
            message += trace.mMessage
        self._mDetailDlg.setTrace(timeStr, pid, tid, levelStr, tag, message)
        return

    def isAutoScroll(self):
        return self._mAutoScrollToBottom

    def setAutoScroll(self, scroll):
        # Logger.i(appModel.getAppTag(), f"scroll={scroll}")
        self._mAutoScrollToBottom = scroll
        if self._mAutoScrollToBottom:
            self.listTrace.scrollToBottom()
        # self.emit()
        return

    def setColumnVisual(self, col, show):
        Logger.i(appModel.getAppTag(), f"{self}, col={col}, show={show}")
        return

    def isColumnVisual(self, col):
        Logger.i(appModel.getAppTag(), f"{self}, col={col}")
        return True

    def setFilter(self, logLevel=None, logInclude=None, logExclude=None):
        if logLevel is None and logInclude is None and logExclude is None:
            return

        self._mTracesModelLock.acquire()
        if logLevel is not None:
            self._mFilterLogLevel = logLevel
        if logInclude is not None:
            self._mFilterLogInclude = logInclude
        if logExclude is not None:
            self._mFilterLogExclude = logExclude
        self._onFilterTraces(True)
        self._mTracesModelLock.release()
        return

    def _onEditorTextChanged(self, newText):
        inputList = appModel.getRecentInputList(newText)
        Logger.i(appModel.getAppTag(), f"newText={newText}, inputList={inputList}")
        ListForQLineEdit.getInstance().showList(inputList, self.tbFindContent)
        return

    def showFindToolbar(self, show):
        Logger.i(appModel.getAppTag(), f"{self}")

        if show and not self.btHideFindToolbar.isHidden():
            self.tbFindContent.setText(pyperclip.paste())
            self.tbFindContent.selectAll()
        QTHelper.showLayout(self.findLayout, show)

        self.ckRegular.close()
        return

    def _onHideFindToolbar(self):
        self.showFindToolbar(False)
        return

    def prevFind(self, reverse: bool = False):
        findMsg = self.tbFindContent.text()
        findFlag = 0
        appModel.addRecentInput(findMsg)
        if self.ckWords.checkState() == Qt.Checked:
            findMsg = r"\b" + findMsg + r"\b"
        if self.ckCase.checkState() == Qt.Checked:
            findFlag = re.IGNORECASE
        if reverse:
            startFind = self.listTrace.count() - 1
            endFind = self.listTrace.currentRow()
        else:
            startFind = self.listTrace.currentRow() - 1
            endFind = 0
        hasFound = None
        for row in range(startFind, endFind, -1):
            item = self.listTrace.item(row)
            if item is None:
                continue
            if item.isHidden():
                continue
            trace: TracerLine = item.data(Qt.UserRole)
            if trace is None:
                continue
            hasFound = re.search(findMsg, trace.getFullText(), flags=findFlag)
            if hasFound is not None:
                Logger.i(appModel.getAppTag(), f"found: {row}")
                self.listTrace.scrollToItem(item)  # ensure visuable
                self.listTrace.setCurrentItem(item)
                break
        if hasFound is None:
            if not reverse and self.prevFind(True):
                self._mNotifyWidget.notify("Find from end.", 1)
                return True
            self._mNotifyWidget.notify("Cannot find content.", 1)
            return False
        return True

    def nextFind(self, reverse: bool = False):
        findMsg = self.tbFindContent.text()
        findFlag = 0
        appModel.addRecentInput(findMsg)
        if self.ckWords.checkState() == Qt.Checked:
            findMsg = r"\b" + findMsg + r"\b"
        if self.ckCase.checkState() == Qt.Checked:
            findFlag = re.IGNORECASE
        if reverse:
            startFind = 0
            endFind = self.listTrace.currentRow()
        else:
            startFind = self.listTrace.currentRow() + 1
            endFind = self.listTrace.count()
        hasFound = None
        for row in range(startFind, endFind):
            item = self.listTrace.item(row)
            if item is None:
                continue
            if item.isHidden():
                continue
            trace: TracerLine = item.data(Qt.UserRole)
            if trace is None:
                continue
            hasFound = re.search(findMsg, trace.getFullText(), flags=findFlag)
            if hasFound is not None:
                Logger.i(appModel.getAppTag(), f"found: {row}")
                self.listTrace.scrollToItem(item)  # ensure visuable
                self.listTrace.setCurrentItem(item)
                break
        if hasFound is None:
            if not reverse and self.nextFind(True):
                self._mNotifyWidget.notify("Find from begin.", 1)
                return True
            self._mNotifyWidget.notify("Cannot find content.", 1)
            return False
        return True

    def markToggle(self, item: QListWidgetItem = None):
        # Logger.i(appModel.getAppTag(), f"{self}")
        selItems = []
        if item is None:
            selItems = self.listTrace.selectedItems()
        else:
            selItems.append(item)
        for item in selItems:
            trace: TracerLine = item.data(Qt.UserRole)
            if trace.mMarked:
                trace.mMarked = False
                item.setBackground(uiTheme.colorNormalBackground)
            else:
                trace.mMarked = True
                item.setBackground(uiTheme.colorMarkedBackground)
        return

    def clearMark(self):
        self._mTracesModelLock.acquire()
        procTime = DateTimeHelper.ProcessTime()
        count = self.listTrace.count()
        for row in range(0, count):
            trace: TracerLine = self.listTrace.item(row).data(Qt.UserRole)
            trace.mMarked = False
        self._mTracesModelLock.release()
        Logger.i(appModel.getAppTag(),
                 f"end with {count} "
                 f"in {procTime.getMicroseconds()} seconds ")
        return

    def prevMark(self):
        startFind = self.listTrace.currentRow() - 1
        hasFound = False
        for row in range(startFind, 0, -1):
            item = self.listTrace.item(row)
            if item.isHidden():
                continue
            trace: TracerLine = item.data(Qt.UserRole)
            if trace is None:
                continue
            if trace.mMarked:
                Logger.i(appModel.getAppTag(), f"found: {row}")
                self.listTrace.scrollToItem(item)  # ensure visuable
                self.listTrace.setCurrentItem(item)
                hasFound = True
                break
        if not hasFound:
            self._mNotifyWidget.notify("Cannot find prev marked.", 1)
        return

    def nextMark(self):
        startFind = self.listTrace.currentRow() + 1
        hasFound = False
        for row in range(startFind, self.listTrace.count()):
            item = self.listTrace.item(row)
            if item.isHidden():
                continue
            trace: TracerLine = item.data(Qt.UserRole)
            if trace is None:
                continue
            if trace.mMarked:
                Logger.i(appModel.getAppTag(), f"found: {row}")
                self.listTrace.scrollToItem(item)  # ensure visuable
                self.listTrace.setCurrentItem(item)
                hasFound = True
                break
        if not hasFound:
            self._mNotifyWidget.notify("Cannot find next marked.", 1)
        return

    def setFilterMarkedOnly(self, markedOnly: bool):
        self._mFilterMarkedOnly = markedOnly
        self._onFilterTraces(True)
        return

    def showLocateDialog(self):
        # self._mScrollToDlg.setDefaultRow()
        if self.listTrace.count() == 0:
            return
        self._mScrollToDlg.setRange(0, self.listTrace.count())
        self._mScrollToDlg.show()
        result = self._mScrollToDlg.exec()
        if result != Const.EXIT_OK:
            return

        row = self._mScrollToDlg.getInputRow()
        self.setSelectRow(row)
        return

    def showGlobalFilterDialog(self):
        self._mGlobalFilterDlg.show()
        result = self._mGlobalFilterDlg.exec()
        if result != Const.EXIT_OK:
            return
        return

    def _onBeginLoad(self, sender: QObject, initCount):
        if sender == self:
            Logger.i(appModel.getAppTag(), f"{initCount}")
            self._mLoading = True
            self._onLoadProgress(0, initCount)
        else:
            Logger.w(appModel.getAppTag(), f"ignore.")
        return

    def _onEndLoad(self, sender: QObject):
        if sender == self:
            Logger.i(appModel.getAppTag(), f"")
            self._onLoadProgress(-1, 0)
            self._mLoading = False
        else:
            Logger.w(appModel.getAppTag(), f"ignore.")
        return

    def beginLoad(self, initCount):
        self._mEventBeginLoad.emit(self, initCount)
        return

    def endLoad(self):
        self._mEventEndLoad.emit(self)
        return

    def setSelectRow(self, row: int):
        if row < 0:
            return
        Logger.i(appModel.getAppTag(), f"setSelectRow: {row}")
        item = self.listTrace.item(row)
        if item is not None:
            self.listTrace.scrollToItem(item)  # ensure visuable
            self.listTrace.setCurrentItem(item)
        return

    def addTrace(self, timeStr: str, pid: str, tid: str, level: LoggerLevel, tag: str, message: str):
        color = self.getLevelColor.get(level)
        levelStr = self.getLevelStr.get(level)
        trace = TracerLine(len(self._mAllTraceLines) + 1,
                           timeStr, pid, tid, level, levelStr, tag,
                           message, color)
        self._mAllTraceLines.append(trace)
        return trace.mIndex

    def _onLoadProgress(self, value, total):
        if value == 0:
            self.pbLoading.setOrientation(Qt.Horizontal)
            self.pbLoading.setMaximum(total)
            self.pbLoading.show()
        elif value < 0:
            self.pbLoading.close()
            self.pbLoading.setMaximum(0)
        else:
            self.pbLoading.setValue(value)
            if value == self.pbLoading.maximum():
                self.pbLoading.close()
                self.pbLoading.setMaximum(0)
        return

    def starTimer(self):
        self._mUpdateTimer.start(100)
        return

    def stopTimer(self):
        self._mUpdateTimer.stop()
        return

    def _onUpdateTimer(self):
        if self._mLoading:
            # just update loading status:
            self._onLoadProgress(len(self._mAllTraceLines), 0)
        else:
            startLine = self._mLastReadLine
            endLine = len(self._mAllTraceLines)
            if startLine == endLine:
                return
            self.listTrace.setUpdatesEnabled(False)
            self._onAddLines(startLine, endLine)
            self._onFilterTraces()
            self.listTrace.setUpdatesEnabled(True)
            self.listTrace.update()
        return

    def _onAddLines(self, startLine, endLine):
        procTime = DateTimeHelper.ProcessTime()
        for line in range(startLine, endLine):
            trace = self._mAllTraceLines[line]
            item = QListWidgetItem(trace.getSelectedCols(self._mColsVisual))
            item.setData(Qt.UserRole, trace)
            item.setHidden(True)
            item.setBackground(uiTheme.colorNormalBackground)
            item.setForeground(trace.mColor)
            self.listTrace.addItem(item)
        self._mScrollToDlg.setRange(0, self.listTrace.count())
        if not self._mLoading and self.isAutoScroll():
            self.listTrace.scrollToBottom()
        self._mLastReadLine = endLine
        if procTime.getMicroseconds() > 0.1:
            Logger.i(appModel.getAppTag(),
                     f"end with {startLine}-{endLine}={endLine - startLine} "
                     f"in {procTime.getMicroseconds()} seconds ")
        return

    def _onFilterTraces(self, fromBegin=False):
        if fromBegin:
            self._mLastFilterRow = 0
            self._mVisualCount = 0
        startRow = self._mLastFilterRow
        endRow = self.listTrace.count()
        if startRow < endRow:
            # Logger.i(appModel.getAppTag(), f"begin with {self._mFilterLogInclude}")
            procTime = DateTimeHelper.ProcessTime()
            for row in range(startRow, endRow):
                item = self.listTrace.item(row)
                trace: TracerLine = item.data(Qt.UserRole)
                self._setLineVisual(item, trace)
                if trace.mVisual:
                    self._mVisualCount += 1
                    if item.isHidden():
                        item.setHidden(False)
                else:
                    if not item.isHidden():
                        item.setHidden(True)
            self._mLastFilterRow = endRow
            if procTime.getMicroseconds() > 0.1:
                Logger.i(appModel.getAppTag(),
                         f"end with {startRow}-{endRow}={endRow - startRow} "
                         f"in {procTime.getMicroseconds()} seconds ")

        statusText = f"{self._mVisualCount}/{len(self._mAllTraceLines)} - {endRow - startRow}"
        self.lbStatus.setText(statusText)
        return

    def _setLineVisual(self, item: QListWidgetItem, trace: TracerLine):
        if trace is None:
            return
        # always show marked item
        if trace.mMarked:
            trace.mVisual = trace.mMarked
            return
        # marked only?
        if self._mFilterMarkedOnly:
            trace.mVisual = trace.mMarked
            return
        # level or msg
        hasFound = re.search(self._mFilterLogInclude,
                             item.text(),
                             flags=re.IGNORECASE)
        if hasFound is None \
                or trace.mLevel < self._mFilterLogLevel:
            trace.mVisual = False
        else:
            trace.mVisual = True
        return

    def getColsVisual(self):
        return self._mColsVisual

    def setColsVisual(self, colsVisual: [bool]):
        if colsVisual is None:
            return
        for i in range(len(colsVisual), TracerLine.col_count):
            colsVisual.append(True)
        self._mColsVisual = colsVisual
        appModel.saveConfig(self._mConfigName, "ColsVisual", self._mColsVisual)
        if not self._mAddable:
            self.clearLog(False)
        return
