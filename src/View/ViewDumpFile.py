import os

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QFileDialog

from src.Common import QTHelper
from src.Common.DumpFileHelper import DumpFileHelper, StackInfo, ThreadInfo
from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Common.QTHelper import ListForQLineEdit
from src.Layout.viewDumpFile import Ui_Form
from src.Model.AppModel import appModel


class ActionType(IntEnum):
    readDump = 0
    showToUI = 1


class TreeItemRole(IntEnum):
    itemType = QtCore.Qt.UserRole + 1
    itemData = QtCore.Qt.UserRole + 2


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

        self._mState = ActionType.readDump
        self._mDumpFileHelper = DumpFileHelper(ViewDumpFile._onStackInfoUpdated, "", "")
        self._mSymbolFolder = ""
        self.setSymbolFolder(appModel.readConfig(self.__class__.__name__, "symbolFolder", ""))
        # appModel.getAppAbsolutePath(["Assets", "Dump", "symbol-pureRelease-41.06.0.376", "arm64-v8a"])

        self._bindEvent()

        self.treeDump.setColumnCount(1)
        self.treeDump.setHeaderLabels(["threads"])
        self.treeDump.header().hide()
        self._mRootName = ""

        self.show()
        return

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
    def setThreadTreeItem(threadItem: QTreeWidgetItem, thread: ThreadInfo):
        itemText = thread.mText
        threadItem.setText(0, itemText)
        threadItem.setData(0, TreeItemRole.itemType, TreeItemType.thread)
        threadItem.setData(0, TreeItemRole.itemData, thread)
        thread.mCustomerData = threadItem
        return

    @staticmethod
    def setStackTreeItem(stackItem: QTreeWidgetItem, stack: StackInfo):
        stack.mCustomerData = stackItem
        ViewDumpFile._onStackInfoUpdated(stack)
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        return

    def resizeEvent(self, QResizeEvent):
        return

    def setSymbolFolder(self, folder: str):
        self._mSymbolFolder = folder
        self.editSymbolFolder.setText(self._mSymbolFolder)
        appModel.saveConfig(self.__class__.__name__, "symbolFolder", self._mSymbolFolder)
        self._mDumpFileHelper.setSymbolFolder(self._mSymbolFolder)
        return

    def openDumpFile(self, path: str, crashedOnly: bool = False):
        Logger.i(appModel.getAppTag(), "")

        self._mRootName = os.path.basename(path)
        if self._mDumpFileHelper.openDumpFile(path, crashedOnly):
            self._showThreadsToUI(self._mDumpFileHelper.getThreads())
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
        rootItem = QTreeWidgetItem(self.treeDump)
        rootItem.setData(0, TreeItemRole.itemType, TreeItemType.file)
        rootItem.setData(0, TreeItemRole.itemData, threads)
        rootItem.setText(0, self._mRootName)
        for thread in threads:
            threadItem = QTreeWidgetItem()
            self.setThreadTreeItem(threadItem, thread)
            for stack in thread.mStacks:
                stackItem = QTreeWidgetItem()
                self.setStackTreeItem(stackItem, stack)
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
            stack: ViewDumpFile.StackInfo = item.data(0, TreeItemRole.itemData)
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
