import csv
import datetime
import os
import sys
import tarfile
import threading
from typing import cast

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QColor, QContextMenuEvent
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QAbstractItemView, QTreeWidgetItemIterator, QMessageBox, QMenu, \
    QFileDialog
from requests import Response

from src.Common import QTHelper, Const, FileUtility, DateTimeHelper, SystemHelper
from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Layout.viewOutlookDetector import Ui_Form

from src.Common.QTHelper import ListForQLineEdit
from src.Common.UITheme import uiTheme
from src.Controller.CCTGDownloader import CCTGDownloader, RequestState
from src.Controller.OutlookCtrl import OutlookCtrl, EmailFilter, EmailItem, FolderItem, AccountItem
from src.Controller.TicketEmailAnalyzer import MailAnalyzer, AnalyzerAction
from src.Model.AppModel import appModel
from src.View.DialogLogin import DialogLogin
from src.View.DialogMailDetail import DialogMailDetail

COL_SENDER = 0
COL_VERSION = 1
COL_TIMEZONE = 2
COL_ANALYZER = 3
COL_SUMMARY = 4
COL_COUNT = 5


def _setTreeItemColor(itemTree: QTreeWidgetItem, foreground: QColor, background: QColor):
    for col in range(0, COL_COUNT):
        itemTree.setForeground(col, foreground)
        itemTree.setBackground(col, background)
    return


class TreeItemRole(IntEnum):
    itemType = QtCore.Qt.UserRole + 1
    itemData = QtCore.Qt.UserRole + 2  # TreeItemInfo


class TreeItemType(IntEnum):
    root = 0
    account = 1
    folder = 2
    email = 3
    date = 4


class TreeItemInfo:
    """
    outlookMail EmailItem
    TreeItemInfo.mTreeItem = QTreeWidgetItem
    TreeItemInfo.mData = EmailItem or str
    QTreeWidgetItem.itemData = TreeItemInfo.mTreeItem
    """

    def __init__(self, parent: QTreeWidgetItem, itemType: TreeItemType, itemData: any, name: str):
        itemTree = QTreeWidgetItem(parent)
        itemTree.setData(COL_SENDER, TreeItemRole.itemType, itemType)
        itemTree.setData(COL_SENDER, TreeItemRole.itemData, self)
        if itemType == TreeItemType.root:
            itemTree.setIcon(COL_SENDER, uiTheme.iconOutlook)
        elif itemType == TreeItemType.account:
            itemTree.setIcon(COL_SENDER, uiTheme.iconOutlookAccount)
        elif itemType == TreeItemType.folder:
            itemTree.setIcon(COL_SENDER, uiTheme.iconOutlookFolder)
        elif itemType == TreeItemType.email:
            itemTree.setIcon(COL_SENDER, uiTheme.iconOutlookEmail)
        elif itemType == TreeItemType.date:
            itemTree.setIcon(COL_SENDER, uiTheme.iconOutlookDate)
        itemTree.setText(COL_SENDER, name)
        _setTreeItemColor(itemTree, uiTheme.colorNormal, uiTheme.colorNormalBackground)

        self.mTreeItem = itemTree
        self.mData = itemData
        return


class ActionType(IntEnum):
    startLoading = 0
    showUI = 1
    readMailTotal = 2
    readMailProgress = 3
    analyzeTotal = 4
    analyzeProgress = 5
    analyzeUpdate = 6
    selectItem = 7
    requestLogin = 8
    symbolTotal = 9
    symbolProgress = 10
    downloadTotal = 11
    downloadProgress = 12


ActionColor = {
    AnalyzerAction.noDescription: uiTheme.colorIgnore,
    AnalyzerAction.error: uiTheme.colorWarning,
    AnalyzerAction.crashed: uiTheme.colorError,
}


class ViewOutlookDetector(QWidget, Ui_Form):
    sEventOutlookState = QtCore.pyqtSignal(ActionType, int, int, object)  # state: sEventOutlookState

    sLocalFolderBase = appModel.getAppAbsolutePath(appModel.mAssetsPath, ["OutlookDetector"], "")
    sSymbolFolderBase = appModel.getWebexSymbolsFolder()
    OutlookCtrl.sLocalFolderBase = sLocalFolderBase
    MailAnalyzer.sBaseSymbolFolder = sSymbolFolderBase

    def __init__(self, parent=None):
        super(ViewOutlookDetector, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)
        self.lbProg1.hide()
        self.lbProg2.hide()
        QTHelper.showLayout(self.layoutProg1, False)
        QTHelper.showLayout(self.layoutProg2, False)

        self._bindEvent()
        self.treeOutlook.setColumnCount(4)
        self.treeOutlook.setHeaderLabels(["Sender", "Version", "Timezone", "Analyzer", "Summary"])
        colWidths = appModel.readConfig(self.__class__.__name__, "colWidths", [330, 120, 100, 100])
        for i in range(0, min(COL_COUNT-1, len(colWidths))):
            self.treeOutlook.setColumnWidth(i, colWidths[i])
        self.treeOutlook.header().setStretchLastSection(True)
        # self.treeOutlook.header().hide()
        self.treeOutlook.setSelectionMode(QAbstractItemView.SingleSelection)

        self.lbLoading.setMovie(uiTheme.gifLoading24)
        self.lbLoading.hide()
        self._mFilterMails: {str, EmailItem} = {}
        filterFolderName = appModel.readConfig(self.__class__.__name__,
                                               "filterFolderName", "Tickets")
        filterToName = appModel.readConfig(self.__class__.__name__,
                                           "filterToName", "webex-android-support(mailer list)")
        filterDays = appModel.readConfig(self.__class__.__name__, "filterDays", 7)
        self._mEmailFilter = EmailFilter(folderArray=[filterFolderName], toArray=[filterToName])
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=filterDays)
        self.dateStart.setDate(week_ago)
        self.dateEnd.setDate(today)
        # self.dateStart.setDate(DateTimeHelper.getDateFromStr("2021-08-06 00:00:00", None))
        # self.dateEnd.setDate(DateTimeHelper.getDateFromStr("2021-09-09 23:59:30", None))
        self.ckFilterDate.setChecked(True)
        self._onCheckFilterData()
        self.mErrorDefinition = {}
        self.mNoticeMessage = {}

        self._mThreadRunning = 0
        self._mThreadOutlook = threading.Thread(target=self._onOutlookThread)
        self._mThreadSymbol = threading.Thread(target=self._onSymbolThread)
        self._mThreadTranslate = threading.Thread(target=self._onTranslateThread)
        self._mEventAnalyzeMail = threading.Event()
        self._mEventLoginCCTG = threading.Event()
        self._mCCTGUser = None
        self._mKeepDownloadFile = False

        self.show()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        colWidths = []
        for i in range(0, 4):
            colWidths.append(self.treeOutlook.columnWidth(i))
        appModel.saveConfig(self.__class__.__name__, "colWidths", colWidths)

        self._mThreadRunning = 0
        MailAnalyzer.sStopAnalyze = True
        if self._mThreadOutlook.is_alive():
            self._mThreadOutlook.join()
        if self._mThreadSymbol.is_alive():
            self._mThreadSymbol.join()
        MailAnalyzer.sStopAnalyze = False
        return

    def resizeEvent(self, QResizeEvent):
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")
        self.ckFilterDate.clicked.connect(self._onCheckFilterData)
        self.btQueryMails.clicked.connect(self._onQueryMails)
        self.btExportExcel.clicked.connect(self._onExportExcel)
        self.btImportExcel.clicked.connect(self._onImportExcel)
        self.sEventOutlookState.connect(self._onEventOutlookState)
        self.treeOutlook.itemSelectionChanged.connect(self._onSelectedItem)
        self.treeOutlook.doubleClicked.connect(self._onMailDetail)

        self.editFilter.textChanged.connect(self._onFilterTextChanged)
        return

    def _onFilterTextChanged(self, newText):
        inputList = appModel.getRecentInputList(newText)
        Logger.i(appModel.getAppTag(), f"newText={newText}, inputList={inputList}")
        ListForQLineEdit.getInstance().showList(inputList, self.editFilter)
        newText = newText.lower()

        foundCount = 0
        it = QTreeWidgetItemIterator(self.treeOutlook)
        while it.value():
            item = it.value()
            itemType = item.data(0, TreeItemRole.itemType.value)
            if itemType == TreeItemType.email:
                # treeItemInfo: TreeItemInfo = item.data(0, TreeItemRole.itemData.value)
                # emailItem: EmailItem = treeItemInfo.mData
                # analyzer: MailAnalyzer = emailItem.mAnalyzer
                for col in range(0, COL_COUNT):
                    if len(newText) > 0 and newText in item.text(col).lower():
                        item.setBackground(col, uiTheme.colorMarkedBackground)
                        foundCount += 1
                        if foundCount == 1:
                            self.treeOutlook.scrollToItem(item)
                    else:
                        item.setBackground(col, uiTheme.colorNormalBackground)
            it += 1

        return

    def _expandFolder(self, item: QTreeWidgetItem):
        while item:
            self.treeOutlook.expandItem(item)
            item = item.parent()
        return

    def _onOutlookThread(self):
        Logger.i(appModel.getAppTag(), "load begin")
        self.sEventOutlookState.emit(ActionType.startLoading, 0, 0, None)
        self._mThreadRunning += 1
        _mOutlookCtrl = OutlookCtrl(self._onReadOutlookItem)
        _mOutlookCtrl.initAccounts()
        self._mFilterMails = _mOutlookCtrl.readFilterItems(self._mEmailFilter)
        Logger.i(appModel.getAppTag(), "load end")
        totalCount = len(self._mFilterMails.items())
        self.sEventOutlookState.emit(ActionType.showUI, totalCount, 0, None)
        self._mEventAnalyzeMail.wait()

        Logger.i(appModel.getAppTag(), "analyze begin")
        curIndex = 0
        self.sEventOutlookState.emit(ActionType.analyzeTotal, totalCount, 0, None)
        for emailID, emailItem in self._mFilterMails.items():
            analyzer = MailAnalyzer(emailItem, self.mErrorDefinition, self.mNoticeMessage)
            self.sEventOutlookState.emit(ActionType.analyzeUpdate, 0, 0, analyzer)
            curIndex += 1
            self.sEventOutlookState.emit(ActionType.analyzeProgress, curIndex, totalCount, None)
            if self._mThreadRunning <= 0:
                break
        self._mThreadRunning -= 1
        Logger.i(appModel.getAppTag(), "analyze end")
        return

    def _onSymbolThread(self):
        Logger.i(appModel.getAppTag(), "download begin")
        notExistCfgFile = os.path.join(self.sSymbolFolderBase, "notExistVersions.json")
        notExistVersions = FileUtility.loadJsonFile(notExistCfgFile)
        # check how many symbols need to be download
        self._mThreadRunning += 1
        downloadVersions = []
        iterator = QTreeWidgetItemIterator(self.treeOutlook)
        while iterator.value():
            item = iterator.value()
            iterator += 1
            version = item.text(COL_VERSION)
            if len(version) == 0:
                continue
            if version in notExistVersions:
                Logger.w(appModel.getAppTag(), f"version={version} is invalid: {notExistVersions[version]}")
                continue
            if version not in downloadVersions:
                downloadVersions.append(version)

        Logger.i(appModel.getAppTag(), f"downloadVersions={len(downloadVersions)}")

        self._mKeepDownloadFile = False

        # download then
        def onRequestState(cctgCtrl: CCTGDownloader, state: RequestState, response: Response) -> bool:
            from requests import auth
            if state == RequestState.succeed:
                Logger.i(appModel.getAppTag(), f"state={state}")
                return self._mThreadRunning > 0
            elif state == RequestState.failed:
                Logger.e(appModel.getAppTag(), f"state={state}")
                return self._mThreadRunning > 0
            elif state == RequestState.needAuthorization:
                Logger.i(appModel.getAppTag(), f"state={state}")
                self._mCCTGUser = None
                self.sEventOutlookState.emit(ActionType.requestLogin, 0, 0, None)
                self._mEventLoginCCTG.wait()
                if self._mCCTGUser is None:
                    return False
                cctgCtrl.setAuth(auth.HTTPBasicAuth(self._mCCTGUser[0], self._mCCTGUser[1]))
            elif state == RequestState.progress:
                curProgress, totalLen = cctg.getCurrentProgress()
                if curProgress == 0:
                    downloadUrl, localPath = cctg.getCurrentTask()
                    if os.path.exists(localPath):
                        # check the size of localPath
                        if totalLen == os.path.getsize(localPath):
                            self.sEventOutlookState.emit(ActionType.downloadTotal, totalLen, 0, None)
                            self.sEventOutlookState.emit(ActionType.downloadProgress, totalLen, 0, None)
                            self._mKeepDownloadFile = True
                            return False

                    self.sEventOutlookState.emit(ActionType.downloadTotal, totalLen, 0, None)
                self.sEventOutlookState.emit(ActionType.downloadProgress, curProgress, 0, None)
                sys.stdout.write("\r[%d / %d] -> %.2f%%" % (curProgress, totalLen, curProgress * 100 / totalLen))
                sys.stdout.flush()
                if curProgress == totalLen:
                    sys.stdout.write(os.linesep)
                    sys.stdout.flush()
            elif state == RequestState.httpCode:
                Logger.i(appModel.getAppTag(), f"response.status_code = {response.status_code}")
                if response.status_code == 404:
                    # will not download again
                    downloadUrl, localPath = cctgCtrl.getCurrentTask()
                    notExistVersions[version] = downloadUrl
                    return False
            return self._mThreadRunning > 0

        count = len(downloadVersions)
        index = 0
        self.sEventOutlookState.emit(ActionType.symbolTotal, count, 0, None)
        cctg = CCTGDownloader(onRequestState, self.sSymbolFolderBase, "cctgToken")
        for version in downloadVersions:
            versionDir = appModel.getAppAbsolutePath(self.sSymbolFolderBase, [version], "")
            # symbol file
            savePath = os.path.join(versionDir, version + "_release.tar")
            uncompressFile = os.path.join(versionDir, "arm64-v8a")
            if not os.path.exists(uncompressFile) or not os.path.exists(savePath):
                # download it
                self._mKeepDownloadFile = False
                if not cctg.getMasterSymbol(version, True, savePath):
                    if os.path.exists(savePath) and not self._mKeepDownloadFile:
                        os.remove(savePath)
                        continue
                if not os.path.exists(uncompressFile) and os.path.exists(savePath):
                    # uncompress it
                    if tarfile.is_tarfile(savePath):
                        compressedFile = tarfile.open(savePath)
                        for tarinfo in compressedFile:
                            compressedFile.extract(tarinfo, path=versionDir)
            # mapping file
            savePath = os.path.join(versionDir, version + "_release_mapping.tar")
            uncompressFile = os.path.join(versionDir, "mapping.txt")
            if not os.path.exists(uncompressFile) or not os.path.exists(savePath):
                # download it
                self._mKeepDownloadFile = False
                if not cctg.getMasterMapping(version, True, savePath):
                    if os.path.exists(savePath) and not self._mKeepDownloadFile:
                        os.remove(savePath)
                        continue
                if not os.path.exists(uncompressFile) and os.path.exists(savePath):
                    # uncompress it
                    if tarfile.is_tarfile(savePath):
                        compressedFile = tarfile.open(savePath)
                        for tarinfo in compressedFile:
                            compressedFile.extract(tarinfo, path=versionDir)
            index += 1
            self.sEventOutlookState.emit(ActionType.symbolProgress, index, count, None)
        FileUtility.saveJsonFile(notExistCfgFile, notExistVersions)
        self._mThreadRunning -= 1
        Logger.i(appModel.getAppTag(), "download end")
        return

    def _onTranslateThread(self):
        Logger.i(appModel.getAppTag(), "translate thread begin")
        self._mThreadRunning += 1
        for emailID, emailItem in self._mFilterMails.items():
            if emailItem.mAnalyzer is not None:
                analyzer: MailAnalyzer = cast(MailAnalyzer, emailItem.mAnalyzer)
                analyzer.getTranslated(True)
            if self._mThreadRunning <= 0:
                break
        self._mThreadRunning -= 1
        Logger.i(appModel.getAppTag(), "translate thread end")
        return

    def _onReadOutlookItem(self, email: EmailItem, folder: FolderItem, account: AccountItem,
                           index: int, count: int) -> bool:
        if email is not None:
            if index == 1:
                self.sEventOutlookState.emit(ActionType.readMailTotal, count, 0, None)
            self.sEventOutlookState.emit(ActionType.readMailProgress, index, count, None)
            pass
        elif folder is not None:
            Logger.d(appModel.getAppTag(), f"reading folder: {folder.mName} - {index}/{count}")
            pass
        elif account is not None:
            Logger.d(appModel.getAppTag(), f"reading account: {account.mName} - {index}/{count}")
            pass
        return self._mThreadRunning > 0

    def _onEventOutlookState(self, state: int, param1: int, param2: int, paramObject: object):
        if state == ActionType.startLoading:
            Logger.i(appModel.getAppTag(), f"state={state}")
            self.btQueryMails.hide()
            self.lbLoading.show()
            uiTheme.gifLoading24.start()
            self.setDisabled(True)
        elif state == ActionType.showUI:
            Logger.i(appModel.getAppTag(), f"state={state}")
            self.btQueryMails.show()
            self.lbLoading.hide()
            uiTheme.gifLoading24.stop()
            self._showOutlookUI()
            self.setDisabled(False)
            self._mEventAnalyzeMail.set()
        elif state == ActionType.readMailTotal:
            Logger.i(appModel.getAppTag(), f"state={state}, param1={param1}, param2={param2}")
            if param1 <= 0:
                return
            self.prog1.setOrientation(Qt.Horizontal)
            self.prog1.setMaximum(param1)
            self.lbProg1.setText("Reading")
            QTHelper.showLayout(self.layoutProg1, True)
        elif state == ActionType.readMailProgress:
            self.prog1.setValue(param1)
            if param1 == self.prog1.maximum():
                Logger.i(appModel.getAppTag(), f"state={state}, param1={param1}, param2={param2}")
                QTHelper.showLayout(self.layoutProg1, False)
        elif state == ActionType.analyzeTotal:
            Logger.i(appModel.getAppTag(), f"state={state}, param1={param1}, param2={param2}")
            if param1 <= 0:
                return
            self.prog1.setOrientation(Qt.Horizontal)
            self.prog1.setMaximum(param1)
            self.lbProg1.setText("Analyzing")
            QTHelper.showLayout(self.layoutProg1, True)
        elif state == ActionType.analyzeProgress:
            self.prog1.setValue(param1)
            if param1 == self.prog1.maximum():
                Logger.i(appModel.getAppTag(), f"state={state}, param1={param1}, param2={param2}")
                QTHelper.showLayout(self.layoutProg1, False)
                self._mThreadSymbol = threading.Thread(target=self._onSymbolThread)
                self._mThreadSymbol.start()
                self._mThreadTranslate = threading.Thread(target=self._onTranslateThread)
                self._mThreadTranslate.start()
        elif state == ActionType.analyzeUpdate:
            if paramObject is not None:
                analyzer: MailAnalyzer = cast(MailAnalyzer, paramObject)
                self._updateOutlookUI(analyzer)
        elif state == ActionType.selectItem:
            if paramObject is not None:
                analyzer: MailAnalyzer = cast(MailAnalyzer, paramObject)
                emailItem: EmailItem = analyzer.mMailItem
                emailTree: TreeItemInfo = emailItem.mCustomerData
                self.treeOutlook.clearSelection()
                emailTree.mTreeItem.setSelected(True)
                self.treeOutlook.scrollToItem(emailTree.mTreeItem)
        elif state == ActionType.requestLogin:
            dlgLogin = DialogLogin(self, "Login CCTG")
            if Const.EXIT_OK == dlgLogin.exec_():
                self._mCCTGUser = dlgLogin.getLoginInfo()
            else:
                self._mCCTGUser = None
            self._mEventLoginCCTG.set()
        elif state == ActionType.symbolTotal:
            Logger.i(appModel.getAppTag(), f"state={state}, param1={param1}, param2={param2}")
            if param1 <= 0:
                return
            self.prog1.setOrientation(Qt.Horizontal)
            self.prog1.setMaximum(param1)
            self.lbProg1.setText("Symbol files")
            QTHelper.showLayout(self.layoutProg1, True)
        elif state == ActionType.symbolProgress:
            self.prog1.setValue(param1)
            if param1 == self.prog1.maximum():
                Logger.i(appModel.getAppTag(), f"state={state}, param1={param1}, param2={param2}")
                QTHelper.showLayout(self.layoutProg1, False)
                QTHelper.showLayout(self.layoutProg2, False)
        elif state == ActionType.downloadTotal:
            Logger.i(appModel.getAppTag(), f"state={state}, param1={param1}, param2={param2}")
            self.prog2.setOrientation(Qt.Horizontal)
            self.prog2.setMaximum(param1)
            self.lbProg2.setText("Downloading")
            QTHelper.showLayout(self.layoutProg2, True)
        elif state == ActionType.downloadProgress:
            self.prog2.setValue(param1)
        return

    def _showOutlookUI(self):
        curDateStr = ""
        dateTree = None
        itemCount = 0
        for emailID, emailItem in self._mFilterMails.items():
            # dateStr = emailItem.mReceivedTime.strftime('%Y-%m-%d')
            datetimeStr = DateTimeHelper.getTimestampString(
                emailItem.mReceivedTime.timestamp(), "%Y-%m-%d %H:%M:%S").split(" ")
            dateStr = datetimeStr[0]
            timeStr = datetimeStr[1]
            if curDateStr != dateStr:
                curDateStr = dateStr
                # if dateTree is not None:
                #    dateTree.mTreeItem.setText(COL_SENDER, f"{curDateStr}({itemCount})")
                dateTree = TreeItemInfo(self.treeOutlook, TreeItemType.date, curDateStr, curDateStr)
                itemCount = 0
            if dateTree is None:
                continue

            itemCount += 1
            emailTree = TreeItemInfo(dateTree.mTreeItem,
                                     TreeItemType.email,
                                     emailItem,
                                     timeStr + " " + emailItem.mSenderName)
            emailItem.mCustomerData = emailTree
        # if dateTree is not None:
        #     dateTree.mTreeItem.setText(COL_SENDER, f"{curDateStr}({itemCount})")
        self.treeOutlook.expandAll()
        return

    @staticmethod
    def _updateOutlookUI(analyzer: MailAnalyzer):
        emailItem: EmailItem = analyzer.mMailItem
        emailTree: TreeItemInfo = emailItem.mCustomerData
        analyzerResult: {} = analyzer.mAnalyzeResult
        if analyzerResult is None or emailTree is None:
            Logger.e(appModel.getAppTag(), f"analyzerResult is None for {emailItem.mSubject}")
            return

        if "BaseInfo" not in analyzerResult:
            return
        # emailTree.mTreeItem.setText(COL_SENDER, analyzerResult["BaseInfo"]["Sender"])
        emailTree.mTreeItem.setText(COL_VERSION, analyzerResult["BaseInfo"]["AppVersion"])
        emailTree.mTreeItem.setText(COL_TIMEZONE, analyzerResult["BaseInfo"]["AppTimezone"])

        action, description = analyzer.getDescription()
        emailTree.mTreeItem.setText(COL_SUMMARY, analyzer.getSummary())
        emailTree.mTreeItem.setText(COL_ANALYZER, description)
        emailTree.mTreeItem.setForeground(COL_ANALYZER, ActionColor.get(action))
        return

    def _onCheckFilterData(self):
        if self.ckFilterDate.isChecked():
            self.dateStart.setDisabled(False)
            self.dateEnd.setDisabled(False)
        else:
            self.dateStart.setDisabled(True)
            self.dateEnd.setDisabled(True)
        return

    def _onQueryMails(self):
        errorDefinition = FileUtility.loadJsonFile(os.path.join(appModel.mAssetsPath, "WBTErrorDefinition.json"))
        self.mErrorDefinition = errorDefinition["errorDefinition"]
        errorDefinition = FileUtility.loadJsonFile(os.path.join(appModel.mAssetsPath, "WBTNoticeMessage.json"))
        self.mNoticeMessage = errorDefinition["noticeMessage"]

        if self.ckFilterDate.isChecked():
            self._mEmailFilter.beginDate = self.dateStart.dateTime().toPyDateTime().timestamp()
            self._mEmailFilter.endDate = self.dateEnd.dateTime().addDays(1).addSecs(-1).toPyDateTime().timestamp()
        else:
            self._mEmailFilter.beginDate = 0
            self._mEmailFilter.endDate = 0
        appModel.saveConfig(self.__class__.__name__,
                            "filterFolderName", self._mEmailFilter.folders[0])
        appModel.saveConfig(self.__class__.__name__,
                            "filterToName", self._mEmailFilter.tos[0])
        self.treeOutlook.clear()
        self._mThreadOutlook = threading.Thread(target=self._onOutlookThread)
        self._mThreadOutlook.start()
        return

    def _onExportExcel(self):
        if len(self._mFilterMails.items()) <= 0:
            QMessageBox().question(self, '', "No data to export.", QMessageBox.Yes)
            return

        excelFiler = open('email_file.csv', mode='w', newline='', encoding='utf-8', errors="ignore")
        excelWriter = csv.writer(excelFiler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for emailID, emailItem in self._mFilterMails.items():
            treeItemInfo: TreeItemInfo = cast(TreeItemInfo, emailItem.mCustomerData)
            treeItem: QTreeWidgetItem = treeItemInfo.mTreeItem
            sender = treeItem.text(COL_SENDER)
            version = treeItem.text(COL_VERSION)
            timezone = treeItem.text(COL_TIMEZONE)
            analyzer: MailAnalyzer = cast(MailAnalyzer, emailItem.mAnalyzer)
            if "Summary" in analyzer.mAnalyzeResult:
                summary = analyzer.mAnalyzeResult["Summary"]
                excelWriter.writerow([sender, version, timezone,
                                      summary["Type"], summary["Description"], summary["Addition"]])
        excelFiler.close()

        qm = QMessageBox()
        ret = qm.question(self, '', "Do you want to show file in explorer?", qm.Yes | qm.No)
        if ret == qm.Yes:
            SystemHelper.openAtExplorer(excelFiler.name)
        return

    def _onImportExcel(self):
        if len(self._mFilterMails.items()) <= 0:
            QMessageBox().warning(self, '', "No data need to be imported.", QMessageBox.Yes)
            return

        title = "Select excel file"
        typeFilter = f"Excel Files (*.csv)"
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,
                                                caption=title,
                                                directory=appModel.mAppPath,
                                                filter=typeFilter,
                                                options=options)
        if len(files) <= 0:
            return
        selFile = files[0]
        Logger.i(appModel.getAppTag(), f"Selected file: {selFile}")
        excelFiler = open(selFile, mode='r', newline='', encoding='utf-8', errors="ignore")
        excelReader = csv.reader(excelFiler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        summaryArray = []
        for csvRow in excelReader:
            summaryArray.append({
                "Sender": csvRow[0],
                "Version": csvRow[1],
                "Timezone": csvRow[2],
                "Type": csvRow[3],
                "Description": csvRow[4],
                "Addition": csvRow[5]
            })
        excelFiler.close()

        importedCount = 0
        updatedCount = 0
        for emailID, emailItem in self._mFilterMails.items():
            treeItemInfo: TreeItemInfo = cast(TreeItemInfo, emailItem.mCustomerData)
            treeItem: QTreeWidgetItem = treeItemInfo.mTreeItem
            sender = treeItem.text(COL_SENDER)
            analyzer: MailAnalyzer = cast(MailAnalyzer, emailItem.mAnalyzer)
            for summary in summaryArray:
                if summary["Sender"] == sender:
                    analyzeSummary = {
                        "Type": summary["Type"],
                        "Description": summary["Description"],
                        "Addition": summary["Addition"]
                    }
                    if "Summary" not in analyzer.mAnalyzeResult:
                        analyzer.mAnalyzeResult["Summary"] = analyzeSummary
                        importedCount += 1
                    else:
                        curSummary = analyzer.mAnalyzeResult["Summary"]
                        if len(curSummary["Type"]) <= 0:
                            curSummary["Type"] = analyzeSummary["Type"]
                        if len(curSummary["Description"]) <= 0:
                            curSummary["Description"] = analyzeSummary["Description"]
                        if len(curSummary["Addition"]) <= 0:
                            curSummary["Addition"] = analyzeSummary["Addition"]
                        updatedCount += 1
                    analyzer.saveResult()
                    self._updateOutlookUI(analyzer)
                    break

        tipMessage = f"Imported {importedCount}, updated {updatedCount}," \
                     f" total {len(summaryArray)} records in excel file"
        QMessageBox().information(self, '', tipMessage, QMessageBox.Yes)
        return

    def _onMailDetail(self, index: QModelIndex):
        curItem = self.treeOutlook.itemFromIndex(index)
        itemType = curItem.data(0, TreeItemRole.itemType.value)
        if itemType != TreeItemType.email:
            return

        addIndex = 0
        selIndex = -1
        treeItems = []
        it = QTreeWidgetItemIterator(self.treeOutlook)
        while it.value():
            item = it.value()
            itemType = item.data(0, TreeItemRole.itemType.value)
            if itemType == TreeItemType.email:
                if item == curItem:
                    selIndex = addIndex
                treeItems.append(item.data(0, TreeItemRole.itemData.value))
                addIndex += 1
            it += 1

        DialogMailDetail(self, treeItems, selIndex).exec_()
        return

    def _onSelectedItem(self):
        return

    def contextMenuEvent(self, event: QContextMenuEvent):
        selItems = self.treeOutlook.selectedItems()

        menu = QMenu()
        if len(selItems) > 0:
            recheck = menu.addAction(uiTheme.iconCopy, "Recheck mail")
            openFolder = menu.addAction(uiTheme.iconFolder, "Open mail folder")
        else:
            recheck = None
            openFolder = None
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is None:
            return
        elif action == recheck:
            procTime = DateTimeHelper.ProcessTime()
            for item in selItems:
                itemType = item.data(0, TreeItemRole.itemType.value)
                if itemType == TreeItemType.email:
                    itemInfo: TreeItemInfo = item.data(0, TreeItemRole.itemData.value)
                    email: EmailItem = itemInfo.mData
                    analyzer = email.mAnalyzer
                    analyzer.analyzeMail(True)
            Logger.i(appModel.getAppTag(), f"end recheck, total {len(selItems)} "
                                           f"in {procTime.getMicroseconds()} seconds ")
        elif action == openFolder:
            for item in selItems:
                itemType = item.data(0, TreeItemRole.itemType.value)
                if itemType == TreeItemType.email:
                    itemInfo: TreeItemInfo = item.data(0, TreeItemRole.itemData.value)
                    email: EmailItem = itemInfo.mData
                    SystemHelper.openAtExplorer(email.mLocalFolder)
                    break
        return
