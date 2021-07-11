import os
import re
import threading

import pyperclip
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QObject, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QKeyEvent, QContextMenuEvent, QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QMenu

from src.Common import QTHelper, DateTimeHelper
from src.Common.Logger import Logger, LoggerLevel
from src.Layout.widgetTracerTabview import Ui_Form

from src.Common.QTHelper import ListForQLineEdit
from src.Common.UITheme import uiTheme
from src.Model.AppModel import appModel
from src.View.WidgetNotify import WidgetNotify
from src.View.DialogTraceDetail import DialogTraceDetail


class WidgetTracerTabview(QWidget, Ui_Form):
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
    col_data = 0
    col_time = 1
    col_pid = 2
    col_tid = 3
    col_level = 4
    col_tag = 5
    col_message = 6
    col_max = 7
    col_width_def = [0, 170, 60, 60, 70, 120, 240]
    col_labels = ['Data', 'Time', 'PID', 'TID', 'Level', 'Tag', 'Message']

    _mEventLoadProgress = QtCore.pyqtSignal(int, int)  # value, total
    _mEventUpdateRows = QtCore.pyqtSignal(int, int)  # startRow, endRow
    # timeStr: str, pid: str, tid: str, level: LoggerLevel, tag: str, message: str
    _mEventAddRow = QtCore.pyqtSignal(str, str, str, int, str, str)

    def __init__(self, parent, configName, hidePB=False):
        super(WidgetTracerTabview, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self._mConfigName = configName
        self._mAdded = 0
        self._mFilterLogLevel = LoggerLevel.Verbose  # base filter
        self._mFilterLogInclude = ""
        self._mFilterLogExclude = ""
        self._mFilterMarkedOnly = False
        self._mRegularFlag = re.IGNORECASE
        self._mAutoScrollToBottom = True
        self._mMarkedRows = []
        self._mDetailDlg = DialogTraceDetail(self)
        self._mNotifyWidget = WidgetNotify(parent)
        self._mNotifyWidget.close()
        self._mIconCheck = QIcon(QPixmap(":/icon/icons/check.svg"))
        self._mIconCopy = QIcon(QPixmap(":/icon/icons/copy.svg"))
        self._mIconMark = QIcon(QPixmap(":/icon/icons/mark.svg"))

        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self._bindEvent()
        self._mTracesModelLock = threading.RLock()
        self._mTracesModel = QStandardItemModel(0, self.col_max)
        self._mTracesModel.setHorizontalHeaderLabels(self.col_labels)
        self.tvTrace.setModel(self._mTracesModel)
        self.tvTrace.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tvTrace.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.tvTrace.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # set from config
        for col in range(0, self.col_max):
            if col != self.col_message:
                self.tvTrace.setColumnWidth(
                    col, appModel.readConfig(self._mConfigName, f"col_width_{col}", self.col_width_def[col]))
                if appModel.readConfig(self._mConfigName, f"col_hidden_{col}", False):
                    self.tvTrace.hideColumn(col)
        # always hide col_data
        self.tvTrace.hideColumn(self.col_data)
        header = self.tvTrace.horizontalHeader()
        # header.setSectionResizeMode(self.col_time, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(self.col_pid, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(self.col_tid, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(self.col_level, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(self.col_tag, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.col_message, QtWidgets.QHeaderView.Stretch)
        self.tvTrace.horizontalHeader().setStretchLastSection(True)
        self.tvTrace.setTextElideMode(Qt.ElideRight)
        self.tvTrace.setAutoScroll(True)
        self.tvTrace.installEventFilter(self)

        self.pbLoading.setMinimum(0)
        self.pbLoading.setTextVisible(True)
        if hidePB:
            self.pbLoading.close()
        self._mEventLoadProgress.connect(self._onLoadProgress)
        self._mEventUpdateRows.connect(self._onUpdateRows)
        self._mEventAddRow.connect(self._onAddRow)

        self.showFindToolbar(False)  # hide find dialog as default
        self.show()
        return

    def _onLoadProgress(self, value, total):
        if value == 0:
            self.pbLoading.setOrientation(Qt.Horizontal)
            self.pbLoading.setMaximum(total)
            self.pbLoading.show()
        else:
            self.pbLoading.setValue(value)
            if value == self.pbLoading.maximum():
                self.pbLoading.close()
        return

    def getTraceTableView(self):
        return self.tvTrace

    def eventFilter(self, source: QObject, event: QtCore.QEvent):
        # Logger.i(appModel.getAppTag(), f"{event}")
        if event.type() == QtCore.QEvent.KeyRelease:
            keyEvent = QKeyEvent(event)
            key = keyEvent.key()
            modifiers = keyEvent.modifiers()
            # hasControl = (modifiers & Qt.ControlModifier) == Qt.ControlModifier
            # hasShift = (modifiers & Qt.ShiftModifier) == Qt.ShiftModifier
            if key == QtCore.Qt.Key_F:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + F: Pop Find dialog
                    self.showFindToolbar(True)
                    return False
            elif key == QtCore.Qt.Key_F3:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + F3: Find prev
                    self.prevFind()
                    return False
                elif modifiers == Qt.NoModifier:
                    # F3: Find next
                    self.nextFind()
                    return False
            elif key == QtCore.Qt.Key_B:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + B: Mark toggle
                    self.markToggle()
                    return False
            elif key == QtCore.Qt.Key_F4:
                if modifiers == Qt.ControlModifier:
                    # Ctrl + F4: Prev mark
                    self.prevMark()
                    return False
                elif modifiers == Qt.NoModifier:
                    # F4: Next mark
                    self.nextMark()
                    return False
        return super(WidgetTracerTabview, self).eventFilter(source, event)

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        # save to config
        for col in range(0, self.col_max):
            if col != self.col_message:
                width = self.tvTrace.columnWidth(col)
                appModel.saveConfig(self._mConfigName, f"col_width_{col}", width)
                isHidden = self.tvTrace.isColumnHidden(col)
                appModel.saveConfig(self._mConfigName, f"col_hidden_{col}", isHidden)
        return

    def resizeEvent(self, QResizeEvent):
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self.tvTrace.activated.connect(self._onActivated)
        self.tvTrace.entered.connect(self._onEntered)
        self.tvTrace.pressed.connect(self._onPressed)
        self.tvTrace.clicked.connect(self._onSelectLogChanged)
        self.tvTrace.doubleClicked.connect(self._onDoubleClickLog)

        self.ckCase.stateChanged.connect(self._onCheckCase)
        self.btFindNext.clicked.connect(self.nextFind)
        self.btFindPrev.clicked.connect(self.prevFind)
        self.btHideFindToolbar.clicked.connect(self._onHideFindToolbar)

        self.tbFindContent.textChanged.connect(self._onEditorTextChanged)
        return

    def _onEditorTextChanged(self, newText):
        inputList = appModel.getRecentInputList(newText)
        Logger.i(appModel.getAppTag(), f"newText={newText}, inputList={inputList}")
        ListForQLineEdit.getInstance().showList(inputList, self.tbFindContent)
        return

    def _onActivated(self, index: QModelIndex):
        # Logger.i(appModel.getAppTag(), f"{QModelIndex.row()} - {self}")
        return

    def _onEntered(self, index: QModelIndex):
        # Logger.i(appModel.getAppTag(), f"{QModelIndex.row()} - {self}")
        return

    def _onPressed(self, index: QModelIndex):
        # Logger.i(appModel.getAppTag(), f"{QModelIndex.row()} - {self}")
        return

    def contextMenuEvent(self, event: QContextMenuEvent):
        selects = self.tvTrace.selectedIndexes()
        selRows = {}
        for item in selects:
            row = item.row()
            selRows[row] = True
            # if row in self._mMarkedRows:

        menu = QMenu()
        if len(selRows) > 0:
            copyMsg = menu.addAction(self._mIconCopy, "Copy messages only")
            copyLogs = menu.addAction(self._mIconCopy, "Copy logs")
            menu.addSeparator()
            toggleMarked = menu.addAction(self._mIconMark, "Toggle marked")
        else:
            copyMsg = None
            copyLogs = None
            toggleMarked = None
        menu.addSeparator()
        if self._mFilterMarkedOnly:
            markedOnly = None
            noMarkedOnly = menu.addAction(self._mIconCheck, "Marked only")
        else:
            markedOnly = menu.addAction("Marked only")
            noMarkedOnly = None
        action = menu.exec_(self.mapToGlobal(event.pos()))

        dataToCopy = ""
        if action is None:
            return
        elif action == copyMsg:
            for row in selRows:
                dataToCopy += self._mTracesModel.item(row, self.col_message).text()
            pyperclip.copy(dataToCopy)
            self._mNotifyWidget.notify("Copied messages to clipboard", 2)
        elif action == copyLogs:
            for row in selRows:
                dataToCopy += self._mTracesModel.item(row, self.col_data).data()
                dataToCopy += os.linesep
            pyperclip.copy(dataToCopy)
            self._mNotifyWidget.notify("Copied logs to clipboard", 2)
        elif action == toggleMarked:
            for row in selRows:
                self.markToggle(row)
        elif action == markedOnly:
            self.setFilterMarkedOnly(True)
        elif action == noMarkedOnly:
            self.setFilterMarkedOnly(False)
        return

    def setFilter(self, logLevel=None, logInclude=None, logExclude=None):
        if logLevel is None and logInclude is None and logExclude is None:
            return

        Logger.i(appModel.getAppTag(), "")

        if logLevel is not None:
            self._mFilterLogLevel = logLevel
        if logInclude is not None:
            self._mFilterLogInclude = logInclude
        if logExclude is not None:
            self._mFilterLogExclude = logExclude
        self._filterTraces()
        return

    def setFilterMarkedOnly(self, markedOnly: bool):
        self._mFilterMarkedOnly = markedOnly
        self._filterTraces()
        return

    def clearLog(self, clearLines=True):
        Logger.i(appModel.getAppTag(), f"clearLines={clearLines}")
        self._mTracesModelLock.acquire()
        self._mTracesModel.removeRows(0, self._mTracesModel.rowCount())
        self._mMarkedRows.clear()
        self.tvTrace.update()
        self._mTracesModelLock.release()
        return

    def setColumnVisual(self, col, show):
        Logger.i(appModel.getAppTag(), f"{self}, col={col}, show={show}")
        if show:
            self.tvTrace.showColumn(col)
        else:
            self.tvTrace.hideColumn(col)
        return

    def isColumnVisual(self, col):
        if self.tvTrace.isColumnHidden(col):
            return False
        else:
            return True

    def showFindToolbar(self, show):
        Logger.i(appModel.getAppTag(), f"{self}")

        if show and not self.btHideFindToolbar.isHidden():
            self.tbFindContent.setText(pyperclip.paste())
        QTHelper.showLayout(self.findLayout, show)

        self.ckRegular.close()
        return

    def _onHideFindToolbar(self):
        self.showFindToolbar(False)
        return

    def prevFind(self):
        findMsg = self.tbFindContent.text()
        appModel.addRecentInput(findMsg)
        if self.ckWords.checkState() == Qt.Checked:
            findMsg = r"\b" + findMsg + r"\b"
        startFind = self.tvTrace.currentIndex().row() - 1
        hasFound = None
        for row in range(startFind, 0, -1):
            if self.tvTrace.isRowHidden(row):
                continue
            dataItem = self._mTracesModel.item(row, self.col_data)
            if dataItem is None:
                continue
            msg = dataItem.data()
            hasFound = re.search(findMsg, msg, flags=self._mRegularFlag)
            if hasFound is not None:
                Logger.i(appModel.getAppTag(), f"found: {row}")
                index = self._mTracesModel.index(row, self.col_message)
                self.tvTrace.scrollTo(index)  # ensure visuable
                self.tvTrace.setCurrentIndex(index)
                break
        if hasFound is None:
            self._mNotifyWidget.notify("Cannot find content.", 1)
        return

    def nextFind(self):
        Logger.i(appModel.getAppTag(), "")
        findMsg = self.tbFindContent.text()
        appModel.addRecentInput(findMsg)
        startFind = self.tvTrace.currentIndex().row() + 1
        count = self._mTracesModel.rowCount()
        hasFound = None
        for row in range(startFind, count):
            if self.tvTrace.isRowHidden(row):
                continue
            dataItem = self._mTracesModel.item(row, self.col_data)
            if dataItem is None:
                continue

            msg = dataItem.data()
            hasFound = re.search(findMsg, msg, flags=self._mRegularFlag)
            if hasFound is not None:
                Logger.i(appModel.getAppTag(), f"found: {row}")
                index = self._mTracesModel.index(row, self.col_message)
                self.tvTrace.scrollTo(index)  # ensure visuable
                self.tvTrace.setCurrentIndex(index)
                break
        if hasFound is None:
            self._mNotifyWidget.notify("Cannot find content.", 1)
        return

    def markToggle(self, row=-1):
        Logger.i(appModel.getAppTag(), f"{self}")
        selRows = {}
        if row < 0:
            selects = self.tvTrace.selectedIndexes()
            for item in selects:
                row = item.row()
                selRows[row] = True
        else:
            selRows[row] = True

        for row in selRows:
            if row in self._mMarkedRows:
                self.removeMark(row)
            else:
                self.addMark(row)
        return

    def addMark(self, row=None):
        if row is None:
            return
        Logger.i(appModel.getAppTag(), f"{self}, row={row}")
        # find pos in _mMarkedRows
        pos = self._getMarkedPosByRow(row)
        self._mMarkedRows.insert(pos, row)
        for col in range(0, self._mTracesModel.columnCount()):
            self._mTracesModel.item(row, col).setBackground(uiTheme.colorMarkedBackground)

        return

    def removeMark(self, row=None):
        if row is None:
            return
        Logger.i(appModel.getAppTag(), f"{self}, row={row}")
        self._mMarkedRows.remove(row)
        for col in range(0, self._mTracesModel.columnCount()):
            self._mTracesModel.item(row, col).setBackground(uiTheme.colorNormalBackground)
        return

    def clearMark(self, row=None):
        Logger.i(appModel.getAppTag(), f"{self}, row={row}")
        self._mMarkedRows.clear()
        return

    def isAutoScroll(self):
        return self._mAutoScrollToBottom

    def setAutoScroll(self, scroll):
        Logger.i(appModel.getAppTag(), f"scroll={scroll}")
        self._mAutoScrollToBottom = scroll
        if self._mAutoScrollToBottom:
            self.tvTrace.scrollToBottom()
        # self.emit()
        return

    def prevMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        row = self.tvTrace.currentIndex().row()
        if row < 0 or row > len(self._mMarkedRows):
            return
        pos = self._getMarkedPosByRow(row)
        if self._mMarkedRows[pos] < row:
            row = self._mMarkedRows[pos]
        else:
            if pos > 0:
                row = self._mMarkedRows[pos - 1]
        index = self._mTracesModel.index(row, self.col_message)
        self.tvTrace.scrollTo(index)  # ensure visuable
        self.tvTrace.setCurrentIndex(index)
        return

    def nextMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        row = self.tvTrace.currentIndex().row()
        if row < 0 or row > len(self._mMarkedRows):
            return
        pos = self._getMarkedPosByRow(row)
        if self._mMarkedRows[pos] > row:
            row = self._mMarkedRows[pos]
        else:
            if pos < (len(self._mMarkedRows) - 1):
                row = self._mMarkedRows[pos + 1]
        index = self._mTracesModel.index(row, self.col_message)
        self.tvTrace.scrollTo(index)  # ensure visuable
        self.tvTrace.setCurrentIndex(index)
        return

    def _getMarkedPosByRow(self, row):
        # find pos in _mMarkedRows
        ret = 0
        for pos in self._mMarkedRows:
            if pos == row:
                return ret
            elif pos > row:
                if ret == 0:
                    return 0
                else:
                    return ret - 1
            ret += 1
        return ret

    def _filterTraces(self):
        Logger.i(appModel.getAppTag(), f"begin with {self._mFilterLogInclude}")
        procTime = DateTimeHelper.ProcessTime()
        self.tvTrace.setUpdatesEnabled(False)
        for row in range(0, self._mTracesModel.rowCount()):
            self._filterRow(row)
        self.tvTrace.setUpdatesEnabled(True)
        Logger.i(appModel.getAppTag(), f"end with {self._mFilterLogInclude} "
                                       f"in {procTime.getMicroseconds()} seconds ")
        return

    def _filterRow(self, row):
        dataItem = self._mTracesModel.item(row, self.col_data)
        levelItem = self._mTracesModel.item(row, self.col_level)
        if dataItem is None or levelItem is None:
            return
        msg = dataItem.data()
        level = levelItem.data()
        tableView = self.tvTrace
        # marked only?
        if self._mFilterMarkedOnly:
            if row not in self._mMarkedRows:
                tableView.hideRow(row)
                return
        # level or msg
        hasFound = re.search(self._mFilterLogInclude, msg, flags=re.IGNORECASE)
        if hasFound is None \
                or level < self._mFilterLogLevel:
            if not tableView.isRowHidden(row):
                tableView.hideRow(row)
        else:
            if tableView.isRowHidden(row):
                tableView.showRow(row)
        return

    def _onDoubleClickLog(self, index: QModelIndex):
        row = index.row()
        Logger.i(appModel.getAppTag(), f"at {row}")

        timeStr = self._mTracesModel.item(row, self.col_time).text()
        pid = self._mTracesModel.item(row, self.col_pid).text()
        tid = self._mTracesModel.item(row, self.col_tid).text()
        level = self._mTracesModel.item(row, self.col_level).text()
        tag = self._mTracesModel.item(row, self.col_tag).text()
        message = self._mTracesModel.item(row, self.col_message).text()
        self._mDetailDlg.setTrace(timeStr, pid, tid, level, tag, message)
        self._mDetailDlg.show()
        return

    def _onCheckCase(self, state):
        if state == Qt.Checked:
            self._mRegularFlag = 0
        else:
            self._mRegularFlag = re.IGNORECASE
        return

    def _onSelectLogChanged(self, index: QModelIndex):
        curIndex = index.row()
        Logger.i(appModel.getAppTag(), f"at {curIndex}")
        rowCount = self._mTracesModel.rowCount()
        if curIndex < 0 or curIndex + 1 == rowCount:
            self.setAutoScroll(True)
        else:
            self.setAutoScroll(False)
        return

    @staticmethod
    def _getColorItem(value, color, data=None):
        item = QStandardItem(value)
        item.setForeground(color)
        item.setBackground(uiTheme.colorNormalBackground)
        if data is not None:
            item.setData(data)
        return item

    def _onUpdateRows(self, startRow, endRow):
        # Logger.i(appModel.getAppTag(), f"begin with ({startRow} - {endRow})")
        # procTime = DateTimeHelper.ProcessTime()
        # self._mTracesModelLock.acquire()
        for row in range(startRow, endRow):
            self._filterRow(row)
        if self.isAutoScroll():
            self.tvTrace.scrollToBottom()
        # self._mTracesModelLock.release()
        # Logger.i(appModel.getAppTag(), f"end read {endRow-startRow} rows "
        #                                 f"in {procTime.getMicroseconds()} seconds ")
        return

    def beginSet(self, initCount):
        self._mTracesModelLock.acquire()
        self.tvTrace.setUpdatesEnabled(False)
        self.tvTrace.clicked.disconnect(self._onSelectLogChanged)
        self._mAdded = 0
        self._mTracesModel.setRowCount(initCount)
        self._mEventLoadProgress.emit(0, initCount)
        return

    def endSet(self):
        self.tvTrace.clicked.connect(self._onSelectLogChanged)
        self.tvTrace.setUpdatesEnabled(True)
        self._mEventLoadProgress.emit(self._mAdded, 0)
        self._mEventUpdateRows.emit(self._mTracesModel.rowCount() - self._mAdded,
                                    self._mTracesModel.rowCount())
        self._mAdded = 0
        # self.tvTrace.update()
        self._mTracesModelLock.release()
        return

    def setTrace(self, timeStr: str, pid: str, tid: str, level: LoggerLevel, tag: str, message: str):
        model = self._mTracesModel
        color = self.getLevelColor.get(level)
        levelStr = self.getLevelStr.get(level)
        fullText = f"{timeStr} {pid} {tid} {levelStr} {tag} {message}"
        model.setItem(self._mAdded, self.col_data, self._getColorItem("", color, fullText))
        model.setItem(self._mAdded, self.col_time, self._getColorItem(timeStr, color))
        model.setItem(self._mAdded, self.col_pid, self._getColorItem(pid, color))
        model.setItem(self._mAdded, self.col_tid, self._getColorItem(tid, color))
        model.setItem(self._mAdded, self.col_level, self._getColorItem(levelStr, color, level))
        model.setItem(self._mAdded, self.col_tag, self._getColorItem(tag, color))
        model.setItem(self._mAdded, self.col_message, self._getColorItem(message, color))

        self._mAdded += 1
        if self._mAdded % 100 == 0:
            self._mEventLoadProgress.emit(self._mAdded, 0)
        return

    def _onAddRow(self, timeStr: str, pid: str, tid: str, level: int, tag: str, message: str):
        model = self._mTracesModel
        level = LoggerLevel(level)

        color = self.getLevelColor.get(level)
        levelStr = self.getLevelStr.get(level)
        fullText = f"{timeStr} {pid} {tid} {levelStr} {tag} {message}"
        dataItem = self._getColorItem("", color, fullText)
        timeItem = self._getColorItem(timeStr, color)
        pidItem = self._getColorItem(pid, color)
        tidItem = self._getColorItem(tid, color)
        levelItem = self._getColorItem(levelStr, color, level)
        tagItem = self._getColorItem(tag, color)
        msgItem = self._getColorItem(message, color)
        model.appendRow([dataItem, timeItem, pidItem, tidItem, levelItem, tagItem, msgItem])
        return

    def beginAdd(self):
        if self._mAdded != 0:
            return

        self.tvTrace.setUpdatesEnabled(False)
        # self.tvTrace.clicked.disconnect(self._onSelectLogChanged)
        self._mAdded = 0
        return

    def endAdd(self):
        if self._mAdded < 200:
            return
        Logger.i(appModel.getAppTag(), f"_mAdded={self._mAdded}")
        # self.tvTrace.clicked.connect(self._onSelectLogChanged)
        self.tvTrace.setUpdatesEnabled(True)
        self._mEventUpdateRows.emit(self._mTracesModel.rowCount() - self._mAdded,
                                    self._mTracesModel.rowCount())
        self._mAdded = 0
        return

    def addTrace(self, timeStr: str, pid: str, tid: str, level: LoggerLevel, tag: str, message: str):
        self._mEventAddRow.emit(timeStr, pid, tid, level.value, tag, message)
        self._mAdded += 1
        return
