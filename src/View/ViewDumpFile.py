import os

import pyperclip
from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, QObject
from PyQt5.QtGui import QKeyEvent, QPalette
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QFileDialog, QAbstractItemView, QMessageBox

from src.Common import QTHelper
from src.Common.DumpFileHelper import DumpFileHelper, StackInfo, ThreadInfo
from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Common.QTHelper import ListForQLineEdit
from src.Layout.viewDumpFile import Ui_Form

from src.Common.UITheme import uiTheme
from src.Model.AppModel import appModel


class ActionType(IntEnum):
    readDump = 0
    showToUI = 1


class TreeItemRole(IntEnum):
    itemType = QtCore.Qt.UserRole + 1
    itemData = QtCore.Qt.UserRole + 2
    itemIndex = QtCore.Qt.UserRole + 3


class TreeItemType(IntEnum):
    file = 0
    thread = 1
    stack = 2


class ViewDumpFile(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(ViewDumpFile, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self.treeDump.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.editSymbolFolder.setReadOnly(False)
        self._mState = ActionType.readDump
        self._mDumpFileHelper = DumpFileHelper(ViewDumpFile._onStackInfoUpdated, "", "")
        self._mSymbolFolder = ""
        self.setSymbolFolder(appModel.readConfig(self.__class__.__name__, "symbolFolder", ""))
        # appModel.getAppAbsolutePath(["Assets", "Dump", "symbol-pureRelease-41.06.0.376", "arm64-v8a"])

        self.treeDump.installEventFilter(self)
        self.editSymbolFolder.installEventFilter(self)
        self._bindEvent()

        self.treeDump.setColumnCount(1)
        self.treeDump.setHeaderLabels(["threads"])
        self.treeDump.header().hide()
        self._mRootName = ""

        self.show()
        return

    def _handleKeyRelease(self, source: QObject, key: int):
        retValue = False
        if source == self.treeDump:
            if key == QtCore.Qt.Key_C:
                selText = ""
                selection = self.treeDump.selectedItems()
                selection.sort(key=lambda rowItem: rowItem.data(0, TreeItemRole.itemIndex))

                for item in selection:
                    itemType = item.data(0, TreeItemRole.itemType)
                    if itemType == TreeItemType.stack:
                        stack: StackInfo = item.data(0, TreeItemRole.itemData)
                        selText += stack.getFullText() + os.linesep
                    elif itemType == TreeItemType.thread:
                        thread: ThreadInfo = item.data(0, TreeItemRole.itemData)
                        selText += thread.mText + os.linesep
                pyperclip.copy(selText)

                retValue = True

        return retValue

    def eventFilter(self, source: QObject, event: QtCore.QEvent):
        # Logger.i(appModel.getAppTag(), f"{event}")
        eventType = event.type()

        if source == self.editSymbolFolder:
            if eventType == QtCore.QEvent.FocusOut:
                self.setSymbolFolder(self.editSymbolFolder.text())
        elif source == self.treeDump:
            if eventType != QtCore.QEvent.KeyRelease:
                return super(ViewDumpFile, self).eventFilter(source, event)

            keyEvent = QKeyEvent(event)
            key = keyEvent.key()
            # modifiers = keyEvent.modifiers()
            # hasControl = (modifiers & Qt.ControlModifier) == Qt.ControlModifier
            # hasShift = (modifiers & Qt.ShiftModifier) == Qt.ShiftModifier
            if self._handleKeyRelease(source, key):
                return super(ViewDumpFile, self).eventFilter(source, event)
            else:
                return False
        return super(ViewDumpFile, self).eventFilter(source, event)

    @staticmethod
    def _onStackInfoUpdated(stack: StackInfo):
        if stack is None or stack.mCustomerData is None:
            return
        stackItem: QTreeWidgetItem = stack.mCustomerData
        stackItem.setText(0, stack.getFullText())
        stackItem.setData(0, TreeItemRole.itemType, TreeItemType.stack)
        stackItem.setData(0, TreeItemRole.itemData, stack)
        return

    @staticmethod
    def setThreadTreeItem(threadItem: QTreeWidgetItem, thread: ThreadInfo, itemIndex: int):
        itemText = thread.mText
        threadItem.setText(0, itemText)
        threadItem.setData(0, TreeItemRole.itemType, TreeItemType.thread)
        threadItem.setData(0, TreeItemRole.itemData, thread)
        threadItem.setData(0, TreeItemRole.itemIndex, itemIndex)
        thread.mCustomerData = threadItem
        return

    @staticmethod
    def setStackTreeItem(stackItem: QTreeWidgetItem, stack: StackInfo, itemIndex: int):
        stack.mCustomerData = stackItem
        ViewDumpFile._onStackInfoUpdated(stack)
        stackItem.setData(0, TreeItemRole.itemIndex, itemIndex)
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        ListForQLineEdit.closeInstance()
        return

    def resizeEvent(self, QResizeEvent):
        return

    def setSymbolFolder(self, folder: str) -> bool:
        pal = QPalette()
        if not os.path.exists(folder):
            pal.setColor(QPalette.Text, uiTheme.colorError)
            self.editSymbolFolder.setPalette(pal)
            return False
        else:
            pal.setColor(QPalette.Text, uiTheme.colorNormal)
            self.editSymbolFolder.setPalette(pal)
        self._mSymbolFolder = folder
        self.editSymbolFolder.setText(self._mSymbolFolder)
        appModel.saveConfig(self.__class__.__name__, "symbolFolder", self._mSymbolFolder)
        self._mDumpFileHelper.setSymbolFolder(self._mSymbolFolder)
        return True

    def openDumpFile(self, path: str, crashedOnly: bool = False):
        Logger.i(appModel.getAppTag(), "")

        self._mRootName = os.path.basename(path)
        if self._mDumpFileHelper.openDumpFile(path, crashedOnly):
            self._showThreadsToUI(self._mDumpFileHelper.getThreads())
        else:
            qm = QMessageBox()
            qm.question(self, f"Open {path} failed", self._mDumpFileHelper.getOpenError(), qm.Yes)

        return

    def openDumpData(self, data, title: str, crashedOnly: bool = False):
        Logger.i(appModel.getAppTag(), "")

        self._mRootName = title
        if self._mDumpFileHelper.openDumpData(data, crashedOnly):
            self._showThreadsToUI(self._mDumpFileHelper.getThreads())
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self.treeDump.clicked.connect(self._onSelectedItem)
        # self.treeDump.entered.connect(self._onSelectedItem)
        self.btSetSymbolFolder.clicked.connect(self._onSetSymbolFolder)
        self.btMark.clicked.connect(self._onMark)
        self.btPrevMark.clicked.connect(self._onPrevMark)
        self.btNextMark.clicked.connect(self._onNextMark)
        self.btFilter.clicked.connect(self._onFilterDump)

        self.editFilter.textChanged.connect(self._onEditorTextChanged)
        return

    def _showThreadsToUI(self, threads: [ThreadInfo]):
        Logger.i(appModel.getAppTag(), f"begin")
        self.treeDump.clear()
        itemIndex = 0
        rootItem = QTreeWidgetItem(self.treeDump)
        rootItem.setData(0, TreeItemRole.itemType, TreeItemType.file)
        rootItem.setData(0, TreeItemRole.itemData, threads)
        rootItem.setData(0, TreeItemRole.itemIndex, itemIndex)
        rootItem.setText(0, self._mRootName)
        itemIndex += 1
        for thread in threads:
            threadItem = QTreeWidgetItem()
            self.setThreadTreeItem(threadItem, thread, itemIndex)
            itemIndex += 1
            for stack in thread.mStacks:
                stackItem = QTreeWidgetItem()
                self.setStackTreeItem(stackItem, stack, itemIndex)
                itemIndex += 1
                threadItem.addChild(stackItem)
            rootItem.addChild(threadItem)
            if thread.isCrashed():
                self.treeDump.expandItem(threadItem)
        self.treeDump.expandItem(rootItem)
        self.editFileInfo.setText(self._mDumpFileHelper.getFileInfo())
        Logger.i(appModel.getAppTag(), f"end")
        return

    def _onEditorTextChanged(self, newText):
        inputList = appModel.getRecentInputList(newText)
        Logger.i(appModel.getAppTag(), f"newText={newText}, inputList={inputList}")
        ListForQLineEdit.getInstance().showList(inputList, self.editFilter)
        return

    def _onSelectedItem(self, index: QModelIndex):
        item = self.treeDump.itemFromIndex(index)
        itemType = item.data(0, TreeItemRole.itemType)
        # itemRow = index.row()
        # Logger.d(appModel.getAppTag(), f"itemRow={itemRow}, itemType={itemType}, text={item.text(0)}")
        if itemType == TreeItemType.stack:
            stack: StackInfo = item.data(0, TreeItemRole.itemData)
            infoText = stack.getFullText() + os.linesep + stack.mInfo
            self.editStackInfo.setText(infoText)
        return

    def _onSetSymbolFolder(self):
        startDir = appModel.readConfig(self.__class__.__name__, "startSelectDir", "")
        folder = QFileDialog.getExistingDirectory(self, directory=startDir)
        appModel.saveConfig(self.__class__.__name__, "startSelectDir", folder)
        self.setSymbolFolder(folder)
        return

    def _onMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        # self._mTracerWidget.markToggle()
        return

    def _onPrevMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        # self._mTracerWidget.prevMark()
        return

    def _onNextMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        # self._mTracerWidget.nextMark()
        return

    def _onFilterDump(self):
        filterMsg = self.editFilter.text()
        appModel.addRecentInput(filterMsg)
        Logger.i(appModel.getAppTag(), f"filter {filterMsg} begin")
        # self._mTracerWidget.setFilter(logInclude=filterMsg)
        Logger.i(appModel.getAppTag(), f"filter {filterMsg} end")
        return
