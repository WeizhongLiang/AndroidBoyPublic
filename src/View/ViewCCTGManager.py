from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QColor, QContextMenuEvent
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QTreeWidgetItem, QMenu

from src.Common import QTHelper, Const
from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Layout.viewCCTGManager import Ui_Form

from src.Common.UITheme import uiTheme
from src.Model.AppModel import appModel
from src.View.DialogCCTGTask import DialogCCTGTask
from src.View.WidgetCCTGOperation import WidgetCCTGOperation


class TreeItemRole(IntEnum):
    itemType = QtCore.Qt.UserRole + 1
    itemData = QtCore.Qt.UserRole + 2  # TreeItemInfo


class TreeItemType(IntEnum):
    version = 1
    apk = 2
    symbol = 3
    mapping = 4


class TreeCol(IntEnum):
    file = 0
    operation = 1
    count = 2


class TaskState(IntEnum):
    error = 0
    notExist = 1
    ready = 2
    running = 3
    stop = 4


def _setTreeItemColor(itemTree: QTreeWidgetItem, foreground: QColor, background: QColor):
    for col in range(0, TreeCol.count.value):
        itemTree.setForeground(col, foreground)
        itemTree.setBackground(col, background)
    return


class CCTGTask:
    def __init__(self, parent: QTreeWidgetItem, itemType: TreeItemType, name: str, url: str):
        itemTree = QTreeWidgetItem(parent)
        colIndex = TreeCol.file.value
        itemTree.setData(colIndex, TreeItemRole.itemType, itemType)
        itemTree.setData(colIndex, TreeItemRole.itemData, self)
        if itemType == TreeItemType.version:
            itemTree.setIcon(colIndex, uiTheme.iconTools)
        elif itemType == TreeItemType.apk:
            itemTree.setIcon(colIndex, uiTheme.iconAPKFile)
        elif itemType == TreeItemType.symbol:
            itemTree.setIcon(colIndex, uiTheme.iconSymbolFile)
        elif itemType == TreeItemType.mapping:
            itemTree.setIcon(colIndex, uiTheme.iconMappingFile)
        itemTree.setText(colIndex, name)
        _setTreeItemColor(itemTree, uiTheme.colorNormal, uiTheme.colorNormalBackground)

        self.mTreeItem = itemTree
        self.mURL = url
        self.mState = TaskState.notExist
        if itemType != TreeItemType.version:
            self.mData = WidgetCCTGOperation()
            itemTree.treeWidget().setItemWidget(itemTree, TreeCol.operation.value, self.mData)
            self._setTaskState(TaskState.notExist)
        else:
            self.mData = None
        return

    def _setTaskState(self, state: TaskState) -> TaskState:
        self.mState = state
        colIndex = TreeCol.operation.value
        if self.mState == TaskState.error:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateError)
        if self.mState == TaskState.notExist:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateNotExist)
        if self.mState == TaskState.ready:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateReady)
        if self.mState == TaskState.running:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateRunning)
        if self.mState == TaskState.stop:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateStop)
        return state


class ViewCCTGManager(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(ViewCCTGManager, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")

        self.setupUi(self)
        QTHelper.switchMacUI(self)
        self._bindEvent()

        self._treeTasks.setColumnCount(TreeCol.count.value)
        self._treeTasks.setHeaderLabels(["Version", "State"])
        colWidths = appModel.readConfig(self.__class__.__name__, "colWidths", [260, 100])
        for i in range(0, min(TreeCol.count.value - 1, len(colWidths))):
            self._treeTasks.setColumnWidth(i, colWidths[i])
        self._treeTasks.header().setStretchLastSection(True)
        # self.treeOutlook.header().hide()
        self._treeTasks.setSelectionMode(QAbstractItemView.SingleSelection)

        self.show()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self._btStart.clicked.connect(self._onStart)
        self._btStop.clicked.connect(self._onStop)
        self._btClear.clicked.connect(self._onClear)
        self.installEventFilter(self)
        return

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        return super(ViewCCTGManager, self).eventFilter(source, event)

    def _onStart(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        return

    def _onStop(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        return

    def _onClear(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        return

    def contextMenuEvent(self, event: QContextMenuEvent):
        selItems = self._treeTasks.selectedItems()

        menu = QMenu()
        actionAddTask = menu.addAction(uiTheme.iconCopy, "Add Task")
        if len(selItems) > 0:
            pass
        else:
            pass
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is None:
            return
        elif action == actionAddTask:
            self._onAddTask()
        return

    def _onAddTask(self):
        dlgTask = DialogCCTGTask(self, "Add download task")
        if Const.EXIT_OK == dlgTask.exec_():
            ret, version = dlgTask.getVersionName()
            if ret:
                versionItem = CCTGTask(self._treeTasks, TreeItemType.version, version, "")

                ret, name, url = dlgTask.getAPKURL()
                if ret:
                    CCTGTask(versionItem.mTreeItem, TreeItemType.apk, name, url)

                ret, name, url = dlgTask.getSymbolURL()
                if ret:
                    CCTGTask(versionItem.mTreeItem, TreeItemType.symbol, name, url)

                ret, name, url = dlgTask.getMappingURL()
                if ret:
                    CCTGTask(versionItem.mTreeItem, TreeItemType.mapping, name, url)
                self._treeTasks.expandAll()
        return
