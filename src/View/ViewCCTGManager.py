import os
import tarfile
import threading

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QEvent, pyqtSlot
from PyQt5.QtGui import QColor, QContextMenuEvent
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QMenu
from requests import Response, auth

from src.Common import QTHelper, Const, FileUtility, SystemHelper
from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Layout.viewCCTGManager import Ui_Form

from src.Common.UITheme import uiTheme
from src.Controller.CCTGDownloader import CCTGDownloader, RequestState
from src.Model.AppModel import appModel
from src.View.DialogCCTGTask import DialogCCTGTask
from src.View.DialogLogin import DialogLogin
from src.View.WidgetCCTGOperation import WidgetCCTGOperation, TaskState, OperationType


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


def _setTreeItemColor(itemTree: QTreeWidgetItem, foreground: QColor, background: QColor):
    for col in range(0, TreeCol.count.value):
        itemTree.setForeground(col, foreground)
        itemTree.setBackground(col, background)
    return


class CCTGTask(QObject):
    _sEventLoginCCTG = threading.Event()
    _sCCTGDownloader = []
    _sIsWaitingLogin = False
    _sLoginSuccess = False

    _mSignalLoginCCTG = QtCore.pyqtSignal(CCTGDownloader)
    _mSignalSetTaskState = QtCore.pyqtSignal(TaskState)
    _mSignalSetTaskProgress = QtCore.pyqtSignal(int, int)

    def __init__(self, parent: QWidget,
                 parentItem: QTreeWidgetItem, itemType: TreeItemType, name: str, url: str, saveFolder: str):
        super(CCTGTask, self).__init__(parent)
        itemTree = QTreeWidgetItem(parentItem)
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

        self._mParentView = parent
        self._mDownloadThread = threading.Thread(target=self._onDownloadThread)
        self._mSignalLoginCCTG.connect(self._onSignalLoginCCTG)
        self._mSignalSetTaskState.connect(self._onSignalSetTaskState)
        self._mSignalSetTaskProgress.connect(self._onSignalSetTaskProgress)
        self.mTreeItem = itemTree
        self.mURL = url
        self.mSaveFolder = saveFolder
        self.mSavePath = os.path.join(self.mSaveFolder, name)
        self.mState = TaskState.unknown
        if itemType != TreeItemType.version:
            self.mOperator = WidgetCCTGOperation(self._onEventOperation)
            itemTree.treeWidget().setItemWidget(itemTree, TreeCol.operation.value, self.mOperator)
            self._mSignalSetTaskState.emit(TaskState.notExist)
        else:
            self.mOperator = None

        self._mDownloader = CCTGDownloader(self._onRequestState, "", "cctgToken")
        return

    def _onDownloadThread(self):
        Logger.i(appModel.getAppTag(), f"begin")
        self._mDownloader.startDownload(self.mURL, self.mSavePath)
        Logger.i(appModel.getAppTag(), f"end")
        return

    def _onEventOperation(self, event: OperationType):
        Logger.i(appModel.getAppTag(), f"begin {event}")
        if event == OperationType.start:
            Logger.i(appModel.getAppTag(), f"start from {self.mURL}{os.linesep}to {self.mSavePath}")
            self.start()
        elif event == OperationType.stop:
            Logger.i(appModel.getAppTag(), f"stop from {self.mURL}{os.linesep}to {self.mSavePath}")
            self.stop()
        elif event == OperationType.delete:
            Logger.i(appModel.getAppTag(), f"clear from {self.mSavePath}")
            self.clear()
        elif event == OperationType.browser:
            Logger.i(appModel.getAppTag(), f"will browser {self.mSavePath}")
            if os.path.exists(self.mSavePath):
                SystemHelper.openAtExplorer(self.mSavePath)
            else:
                if os.path.exists(self.mSaveFolder):
                    SystemHelper.openAtExplorer(self.mSaveFolder)
                else:
                    Logger.e(appModel.getAppTag(), f"folder {self.mSaveFolder} not exist")
            if self.mOperator is not None:
                self.mOperator.setState(self.mState)
        Logger.i(appModel.getAppTag(), f"end {event}")
        return

    @pyqtSlot(CCTGDownloader)
    def _onSignalLoginCCTG(self, cctgCtrl: CCTGDownloader):
        Logger.i(appModel.getAppTag(),
                 f"_sIsWaitingLogin = {CCTGTask._sIsWaitingLogin}, size = {len(CCTGTask._sCCTGDownloader)}")
        # add into list
        CCTGTask._sCCTGDownloader.append(cctgCtrl)
        if not CCTGTask._sIsWaitingLogin:
            CCTGTask._sIsWaitingLogin = True
            CCTGTask._sCCTGDownloader.append(cctgCtrl)
            dlgLogin = DialogLogin(self._mParentView, "Login CCTG")
            if Const.EXIT_OK == dlgLogin.exec_():
                cctgUser = dlgLogin.getLoginInfo()
                for ctrl in CCTGTask._sCCTGDownloader:
                    ctrl.setAuth(auth.HTTPBasicAuth(cctgUser[0], cctgUser[1]))
                CCTGTask._sCCTGDownloader = []
                CCTGTask._sLoginSuccess = True
            else:
                CCTGTask._sLoginSuccess = False
            CCTGTask._sEventLoginCCTG.set()
        return

    @pyqtSlot(TaskState)
    def _onSignalSetTaskState(self, state: TaskState):
        if self.mState == state:
            return
        Logger.i(appModel.getAppTag(), f"state = {state}")
        self.mState = state
        colIndex = TreeCol.operation.value
        if self.mState == TaskState.error:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateError)
        if self.mState == TaskState.notExist:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateNotExist)
        if self.mState == TaskState.ready:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateReady)
            self._uncompress()
        if self.mState == TaskState.running:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateRunning)
        if self.mState == TaskState.stop:
            self.mTreeItem.setIcon(colIndex, uiTheme.iconStateStop)
        if self.mOperator is not None:
            self.mOperator.setState(state)
        return

    @pyqtSlot(int, int)
    def _onSignalSetTaskProgress(self, total: int, cur: int):
        if total >= 0:
            self.mOperator.setTotalProgress(total)
        if cur >= 0:
            self.mOperator.setCurProgress(cur)
        return

    def _onRequestState(self, cctgCtrl: CCTGDownloader, state: RequestState, response: Response) -> bool:
        if state == RequestState.succeed:
            Logger.i(appModel.getAppTag(), f"state={state}")
            self._mSignalSetTaskState.emit(TaskState.ready)
            return True
        elif state == RequestState.failed:
            Logger.e(appModel.getAppTag(), f"state={state}")
            self._mSignalSetTaskState.emit(TaskState.error)
            return False
        elif state == RequestState.needAuthorization:
            Logger.i(appModel.getAppTag(), f"state={state}")
            self._mSignalLoginCCTG.emit(cctgCtrl)
            CCTGTask._sEventLoginCCTG.wait()
            if not CCTGTask._sLoginSuccess:
                self._mSignalSetTaskState.emit(TaskState.error)
            return CCTGTask._sLoginSuccess
        elif state == RequestState.progress:
            self._mSignalSetTaskState.emit(TaskState.running)
            curProgress, totalLen = cctgCtrl.getCurrentProgress()
            if curProgress == 0:
                downloadUrl, localPath = cctgCtrl.getCurrentTask()
                if os.path.exists(localPath):
                    # check the size of localPath
                    if totalLen == os.path.getsize(localPath):
                        self._mSignalSetTaskProgress.emit(totalLen, totalLen)
                        self._mSignalSetTaskState.emit(TaskState.ready)
                        return False
                self._mSignalSetTaskProgress.emit(totalLen, -1)
            self._mSignalSetTaskProgress.emit(-1, curProgress)
        elif state == RequestState.httpCode:
            Logger.i(appModel.getAppTag(), f"response.status_code = {response.status_code}")
            if response.status_code == 404:
                self._mSignalSetTaskState.emit(TaskState.error)
                # will not download again
                # downloadUrl, localPath = cctgCtrl.getCurrentTask()
                # notExistVersions[version] = downloadUrl
                return False
        elif state == RequestState.cancel:
            self._mSignalSetTaskState.emit(TaskState.notExist)
            return False
        return self.mState != TaskState.stop

    def _uncompress(self):
        colIndex = TreeCol.file.value
        itemType: TreeItemType = self.mTreeItem.data(colIndex, TreeItemRole.itemType)
        if itemType == TreeItemType.symbol:
            # symbol file
            savePath = self.mSavePath
            uncompressFile = os.path.join(self.mSaveFolder, "arm64-v8a")
            if not os.path.exists(uncompressFile) and os.path.exists(savePath):
                # uncompress it
                if tarfile.is_tarfile(savePath):
                    compressedFile = tarfile.open(savePath)
                    for tarinfo in compressedFile:
                        compressedFile.extract(tarinfo, path=self.mSaveFolder)
        elif itemType == TreeItemType.mapping:
            # mapping file
            savePath = self.mSavePath
            uncompressFile = os.path.join(self.mSaveFolder, "mapping.txt")
            if not os.path.exists(uncompressFile) and os.path.exists(savePath):
                # uncompress it
                if tarfile.is_tarfile(savePath):
                    compressedFile = tarfile.open(savePath)
                    for tarinfo in compressedFile:
                        compressedFile.extract(tarinfo, path=self.mSaveFolder)
        return

    def isChecked(self):
        if self.mOperator is not None:
            return self.mOperator.isChecked()
        else:
            return False

    def isRunning(self):
        return self.mState == TaskState.running

    def start(self):
        if not self.isRunning():
            Logger.i(appModel.getAppTag(), f"start for {self.mSavePath}")
            self._onSignalSetTaskState(TaskState.running)
            self._mDownloadThread = threading.Thread(target=self._onDownloadThread)
            self._mDownloadThread.start()
        return

    def stop(self):
        if self.isRunning():
            Logger.i(appModel.getAppTag(), f"stop for {self.mSavePath}")
            self._mDownloader.stopDownload()
            if self._mDownloadThread.is_alive():
                self._mDownloadThread.join()
            # self._onEventSetTaskState(TaskState.running) will call at download call back
        return

    def clear(self):
        self.stop()  # stop first
        if os.path.exists(self.mSavePath):
            os.remove(self.mSavePath)
            self._onSignalSetTaskState(TaskState.notExist)
        if self.mOperator is not None:
            self.mOperator.setState(self.mState)
        return


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
        # self._treeTasks.setSelectionMode(QAbstractItemView.SingleSelection)

        self.show()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        items: [QTreeWidgetItem] = QTHelper.getAllTreeItems(self._treeTasks)
        for item in items:
            colIndex = TreeCol.file.value
            itemType = item.data(colIndex, TreeItemRole.itemType)
            if itemType != TreeItemType.version:
                cctgTask: CCTGTask = item.data(colIndex, TreeItemRole.itemData)
                if cctgTask is not None:
                    cctgTask.stop()
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
        items: [QTreeWidgetItem] = QTHelper.getAllTreeItems(self._treeTasks)
        for item in items:
            colIndex = TreeCol.file.value
            itemType = item.data(colIndex, TreeItemRole.itemType)
            if itemType != TreeItemType.version:
                cctgTask: CCTGTask = item.data(colIndex, TreeItemRole.itemData)
                if cctgTask is not None and cctgTask.isChecked():
                    cctgTask.start()
        return

    def _onStop(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        items: [QTreeWidgetItem] = QTHelper.getAllTreeItems(self._treeTasks)
        for item in items:
            colIndex = TreeCol.file.value
            itemType = item.data(colIndex, TreeItemRole.itemType)
            if itemType != TreeItemType.version:
                cctgTask: CCTGTask = item.data(colIndex, TreeItemRole.itemData)
                if cctgTask is not None and cctgTask.isChecked():
                    cctgTask.stop()
        return

    def _onClear(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        items: [QTreeWidgetItem] = QTHelper.getAllTreeItems(self._treeTasks)
        for item in items:
            colIndex = TreeCol.file.value
            itemType = item.data(colIndex, TreeItemRole.itemType)
            if itemType != TreeItemType.version:
                cctgTask: CCTGTask = item.data(colIndex, TreeItemRole.itemData)
                if cctgTask is not None and cctgTask.isChecked():
                    cctgTask.clear()
        return

    def contextMenuEvent(self, event: QContextMenuEvent):
        selItems = self._treeTasks.selectedItems()

        menu = QMenu()
        actionAddTask = menu.addAction(uiTheme.iconTools, "Add Download Task")
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
            if not ret:
                return

            saveFolder = os.path.join(appModel.getWebexSymbolsFolder(), version)
            FileUtility.makeFolder(saveFolder)
            versionItem = CCTGTask(self, self._treeTasks, TreeItemType.version, version, "", saveFolder)

            ret, name, url = dlgTask.getAPKURL()
            if ret:
                CCTGTask(self, versionItem.mTreeItem, TreeItemType.apk, name, url, saveFolder)

            ret, name, url = dlgTask.getSymbolURL()
            if ret:
                CCTGTask(self, versionItem.mTreeItem, TreeItemType.symbol, name, url, saveFolder)

            ret, name, url = dlgTask.getMappingURL()
            if ret:
                CCTGTask(self, versionItem.mTreeItem, TreeItemType.mapping, name, url, saveFolder)
            self._treeTasks.expandAll()
        return
