import os
import re
import zipfile

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QDialog, QListWidgetItem
from src.Layout.dialogMailDetail import Ui_Dialog

from src.Common import QTHelper, SystemHelper, FileUtility, Const
from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Common.QTHelper import ListForQLineEdit
from src.Common.UITheme import uiTheme
from src.Controller.OutlookCtrl import EmailItem
from src.Controller.TicketEmailAnalyzer import DumpFileState
from src.Model.AppModel import appModel
from src.View.DialogNormalLogs import DialogNormalLogs
from src.View.ViewDumpFile import ViewDumpFile
from src.View.ViewPicture import ViewPicture
from src.View.ViewWBXTraceFile import ViewWBXTraceFile


class _ErrorTypeInList(IntEnum):
    normal = 0
    error = 1
    crashed = 2


_ErrorColor = {
    _ErrorTypeInList.normal: uiTheme.colorNormal,
    _ErrorTypeInList.error: uiTheme.colorWarning,
    _ErrorTypeInList.crashed: uiTheme.colorError,
}


class DialogMailDetail(QDialog, Ui_Dialog):
    def __init__(self, parent, treeItems: [], selIndex: int):
        from src.View.ViewOutlookDetector import ViewOutlookDetector, TreeItemInfo
        super(DialogMailDetail, self).__init__(parent)
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        QTHelper.handleWndPos(self, True)
        self._bindEvent()
        self.installEventFilter(self)
        self.cbType.installEventFilter(self)
        self.cbSummary.installEventFilter(self)
        self.cbAddition.installEventFilter(self)
        self._mNormalLogsDialog = DialogNormalLogs(self)

        # self.ltErrors.setWordWrap(True)

        self.mTreeItems = treeItems
        self.mIndex = selIndex
        self.mTreeItem: TreeItemInfo = self.mTreeItems[self.mIndex]
        self.mAnalyzer = None

        self.mSummaryHistory = FileUtility.loadJsonFile(
            os.path.join(ViewOutlookDetector.sLocalFolderBase, "SummaryHistory.json"))
        if "Type" in self.mSummaryHistory:
            self.cbType.addItems(self.mSummaryHistory["Type"].keys())
        if "Summary" in self.mSummaryHistory:
            self.cbSummary.addItems(self.mSummaryHistory["Summary"].keys())
        if "Addition" in self.mSummaryHistory:
            self.cbAddition.addItems(self.mSummaryHistory["Addition"].keys())
        self._showEmailDetail()
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self.btNextMail.clicked.connect(self._onNextMail)
        self.btPrevMail.clicked.connect(self._onPrevMail)
        self.btFolder.clicked.connect(self._onOpenMailFolder)
        self.ltErrors.doubleClicked.connect(self._onDoubleClickError)
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        self._saveSummary()
        QTHelper.handleWndPos(self, False)
        ListForQLineEdit.closeInstance()
        return

    def eventFilter(self, source: QObject, event: QtCore.QEvent):
        eventType = event.type()
        if eventType == QtCore.QEvent.KeyRelease:
            keyEvent = QKeyEvent(event)
            key = keyEvent.key()
            # Logger.i(appModel.getAppTag(), f"source = {source}, key = {key}")
            if key == QtCore.Qt.Key_Return:
                if source == self.cbType:
                    self.cbSummary.setFocus()
                elif source == self.cbSummary:
                    self.cbAddition.setFocus()
                elif source == self.cbAddition:
                    self._onNextMail()

        return super(DialogMailDetail, self).eventFilter(source, event)

    def _showEmailDetail(self):
        email: EmailItem = self.mTreeItem.mData
        if email is None:
            Logger.e(appModel.getAppTag(), "self.mTreeItem.mData is None")
            return
        self.mAnalyzer = email.mAnalyzer
        if self.mAnalyzer is None:
            Logger.e(appModel.getAppTag(), "email.mAnalyzer is None")
            return
        result = self.mAnalyzer.mAnalyzeResult

        if "BaseInfo" not in result:
            Logger.e(appModel.getAppTag(), "BaseInfo is not in analyzer.mAnalyzeResult")
            return

        self.setWindowTitle(result["BaseInfo"]["Subject"])
        self.editTitle.setText(result["BaseInfo"]["Subject"])
        self.editSender.setText(result["BaseInfo"]["Sender"])
        mailContent = result["BaseInfo"]["Body"]
        translated = self.mAnalyzer.getTranslated(False)
        if len(translated) > 0:
            mailContent += os.linesep + os.linesep + "------ translated ------" + os.linesep
            mailContent += translated
        self.editContent.setText(mailContent)

        # self.editAnalyze.setTextColor(_ErrorColor.get(retAction))
        # self.editAnalyze.setText(retString)
        self.ltErrors.clear()
        if "KeyError" in result:
            for errorKey, errorMsg in result["KeyError"].items():
                if len(errorMsg) == 0:
                    continue
                # nodes = errorMsg.split("@", 3)
                filePath = errorMsg["logFile"].split("?")
                item = QListWidgetItem(errorMsg["errName"] + "@" + filePath[1])
                item.setData(Qt.UserRole, [_ErrorTypeInList.error, errorMsg])
                item.setBackground(uiTheme.colorNormalBackground)
                item.setForeground(_ErrorColor.get(_ErrorTypeInList.error))
                self.ltErrors.addItem(item)

                errorKey = errorMsg["errType"]
                if self.cbType.findText(errorKey) < 0:
                    self.cbType.addItem(errorKey)
        if "NoticeMessage" in result:
            for errorKey, errorMsg in result["NoticeMessage"].items():
                if len(errorMsg) == 0:
                    continue
                # nodes = errorMsg.split("@", 3)
                filePath = errorMsg["logFile"].split("?")
                item = QListWidgetItem(errorMsg["errName"] + "@" + filePath[1])
                item.setData(Qt.UserRole, [_ErrorTypeInList.error, errorMsg])
                item.setBackground(uiTheme.colorNormalBackground)
                item.setForeground(_ErrorColor.get(_ErrorTypeInList.error))
                self.ltErrors.addItem(item)

                errorKey = errorMsg["errType"]
                if self.cbType.findText(errorKey) < 0:
                    self.cbType.addItem(errorKey)
        if "DumpFile" in result:
            dumpState = result["DumpFile"]["state"]
            if DumpFileState.crashed.value == dumpState:
                if "firstException" in result["DumpFile"]:
                    firstException = result["DumpFile"]["firstException"]
                    if len(firstException):
                        dumpState += "@" + firstException
                        item = QListWidgetItem(dumpState + "@" + firstException)
                        item.setData(Qt.UserRole, [_ErrorTypeInList.crashed, result["DumpFile"]["path"]])
                        item.setBackground(uiTheme.colorNormalBackground)
                        item.setForeground(_ErrorColor.get(_ErrorTypeInList.crashed))
                        self.ltErrors.addItem(item)
        if "Attachment" in result:
            for path in result["Attachment"]:
                if zipfile.is_zipfile(path):
                    zipFile = zipfile.ZipFile(path)
                    for subFile in zipFile.filelist:
                        pathData = path + "?" + subFile.filename
                        item = QListWidgetItem(subFile.filename +
                                               "   [" + FileUtility.fileSizeFmt(subFile.file_size) + "]")
                        item.setData(Qt.UserRole, [_ErrorTypeInList.normal, pathData])
                        item.setBackground(uiTheme.colorNormalBackground)
                        item.setForeground(_ErrorColor.get(_ErrorTypeInList.normal))
                        self.ltErrors.addItem(item)
                else:
                    fileName = os.path.basename(path)
                    item = QListWidgetItem(fileName)
                    item.setData(Qt.UserRole, [_ErrorTypeInList.normal, path])
                    item.setBackground(uiTheme.colorNormalBackground)
                    item.setForeground(_ErrorColor.get(_ErrorTypeInList.normal))
                    self.ltErrors.addItem(item)

        self.ltErrors.sortItems()

        if "Summary" in result:
            self.cbType.setCurrentText(result["Summary"]["Type"])
            self.cbSummary.setCurrentText(result["Summary"]["Description"])
            self.cbAddition.setCurrentText(result["Summary"]["Addition"])
        else:
            self.cbType.setCurrentText("")
            self.cbSummary.setCurrentText("")
            self.cbAddition.setCurrentText("")

        self._onAttachmentThread()
        self.cbType.setFocus()
        return

    def _onAttachmentThread(self):
        self.tabAttachments.clear()
        result = self.mAnalyzer.mAnalyzeResult
        if "Attachment" in result:
            for attachment in result["Attachment"]:
                self._openAttachment(attachment)
        return

    def _saveSummary(self):
        from src.View.ViewOutlookDetector import ViewOutlookDetector, ActionType
        if self.mAnalyzer is None:
            Logger.e(appModel.getAppTag(), "email.mAnalyzer is None")
            return
        newType = self.cbType.currentText()
        newSummary = self.cbSummary.currentText()
        newAddition = self.cbAddition.currentText()
        result = self.mAnalyzer.mAnalyzeResult
        if result["Summary"]["Type"] != newType\
                or result["Summary"]["Description"] != newSummary\
                or result["Summary"]["Addition"] != newAddition:
            result["Summary"]["Type"] = newType
            result["Summary"]["Description"] = newSummary
            result["Summary"]["Addition"] = newAddition
            self.mAnalyzer.saveResult()
            outlookDetector = self.parent()
            outlookDetector.sEventOutlookState.emit(ActionType.analyzeUpdate, 0, 0, self.mAnalyzer)

            if "Type" not in self.mSummaryHistory:
                self.mSummaryHistory["Type"] = {}
            if "Summary" not in self.mSummaryHistory:
                self.mSummaryHistory["Summary"] = {}
            if "Addition" not in self.mSummaryHistory:
                self.mSummaryHistory["Addition"] = {}
            self.mSummaryHistory["Type"][newType] = ""
            self.mSummaryHistory["Summary"][newSummary] = ""
            self.mSummaryHistory["Addition"][newAddition] = ""
            FileUtility.saveJsonFile(
                os.path.join(ViewOutlookDetector.sLocalFolderBase, "SummaryHistory.json"),
                self.mSummaryHistory)

            if self.cbType.findText(newType) < 0:
                self.cbType.addItem(newType)
            if self.cbSummary.findText(newSummary) < 0:
                self.cbSummary.addItem(newSummary)
            if self.cbAddition.findText(newAddition) < 0:
                self.cbAddition.addItem(newAddition)

        return

    def _onNextMail(self):
        Logger.i(appModel.getAppTag(), "begin")
        from src.View.ViewOutlookDetector import ActionType
        if self.mIndex >= len(self.mTreeItems) - 1:
            return
        self._saveSummary()
        self.mIndex += 1
        self.mTreeItem = self.mTreeItems[self.mIndex]
        self._showEmailDetail()
        outlookDetector = self.parent()
        outlookDetector.sEventOutlookState.emit(ActionType.selectItem, 0, 0, self.mAnalyzer)
        Logger.i(appModel.getAppTag(), "end")
        return

    def _onPrevMail(self):
        Logger.i(appModel.getAppTag(), "begin")
        from src.View.ViewOutlookDetector import ActionType
        if self.mIndex <= 0:
            return
        self._saveSummary()
        self.mIndex -= 1
        self.mTreeItem = self.mTreeItems[self.mIndex]
        self._showEmailDetail()
        outlookDetector = self.parent()
        outlookDetector.sEventOutlookState.emit(ActionType.selectItem, 0, 0, self.mAnalyzer)
        Logger.i(appModel.getAppTag(), "end")
        return

    def _onOpenMailFolder(self):
        if self.mTreeItem is None or self.mTreeItem.mData is None:
            return
        email: EmailItem = self.mTreeItem.mData
        SystemHelper.openAtExplorer(email.mLocalFolder)
        return

    def _onDoubleClickError(self, QModelIndex):
        row = QModelIndex.row()
        errorInfo: [] = self.ltErrors.item(row).data(Qt.UserRole)
        Logger.i(appModel.getAppTag(), f"at {row} {errorInfo[0]} - {errorInfo[1]}")
        if errorInfo[0] == _ErrorTypeInList.error:
            # locate file line
            fileName = errorInfo[1]["logFile"].split("?")[1]
            logIndex = errorInfo[1]["logIndex"]
            for i in range(0, self.tabAttachments.count()):
                tabTitle = self.tabAttachments.tabText(i)
                if fileName == tabTitle:
                    view = self.tabAttachments.widget(i)
                    self.tabAttachments.setCurrentWidget(view)
                    view.scrollToItemByLogIndex(logIndex)
                    break
            # scrollToPreSelectItem
        elif errorInfo[0] == _ErrorTypeInList.normal:
            # locate file line
            path = errorInfo[1]
            self._mNormalLogsDialog.addFileView(path)
            self._mNormalLogsDialog.show()
        return

    def _openAttachment(self, path):
        if self.mAnalyzer is None:
            Logger.e(appModel.getAppTag(), "email.mAnalyzer is None")
            return
        result = self.mAnalyzer.mAnalyzeResult

        wbtFiles = {}
        for row in range(0, self.ltErrors.count()):
            item = self.ltErrors.item(row)
            errorInfo: [] = item.data(Qt.UserRole)
            if _ErrorTypeInList.error == errorInfo[0]:
                logFile = errorInfo[1]["logFile"].split("?")[1]
                logIndex = int(errorInfo[1]["logIndex"])
                beginIndex = logIndex - 200
                endIndex = logIndex + 200
                if logFile not in wbtFiles:
                    wbtFiles[logFile] = {"beginIndex": 2147483647, "endIndex": 0, "preSelect": logIndex}
                if wbtFiles[logFile]["beginIndex"] > beginIndex:
                    wbtFiles[logFile]["beginIndex"] = beginIndex
                if wbtFiles[logFile]["endIndex"] < endIndex:
                    wbtFiles[logFile]["endIndex"] = endIndex

        fileName = os.path.basename(path)
        if re.search(r".zip$", path, flags=re.IGNORECASE):
            if not zipfile.is_zipfile(path):
                return
            zipFile = zipfile.ZipFile(path)
            for subFileName in zipFile.namelist():
                title = subFileName
                tabCount = self.tabAttachments.count()
                if re.search(r".wbt$", subFileName, flags=re.IGNORECASE):
                    if subFileName in wbtFiles:
                        Logger.i(appModel.getAppTag(), f"will open: {subFileName} in {fileName}")
                        fileData = zipFile.read(subFileName)
                        view = ViewWBXTraceFile(self)
                        view.setTraceRange(
                            wbtFiles[subFileName]["beginIndex"],
                            wbtFiles[subFileName]["endIndex"]
                        )
                        view.openTraceData(fileData, view.DATA_WBT)
                    else:
                        continue

                elif re.search(r".dmp$", subFileName, flags=re.IGNORECASE):
                    Logger.i(appModel.getAppTag(), f"will open: {subFileName} in {fileName}")
                    fileData = zipFile.read(subFileName)
                    view = ViewDumpFile(self)
                    view.openDumpData(fileData, title, True)
                    view.setSymbolFolder(result["DumpFile"]["symbolPath"])
                elif re.search(fr"{Const.imageFileRegular}$",
                               subFileName, flags=re.IGNORECASE):
                    fileData = zipFile.read(subFileName)
                    view = ViewPicture(self)
                    view.openPictureData(fileData)
                else:
                    continue
                self.tabAttachments.setCurrentIndex(
                    self.tabAttachments.insertTab(tabCount, view, title))
        else:
            title = fileName
            if re.search(r".wbt$", path, flags=re.IGNORECASE):
                view = ViewWBXTraceFile(self)
                view.openTraceFile(path, view.DATA_WBT)
            elif re.search(r".lgf$", path, flags=re.IGNORECASE):
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
            tabCount = self.tabAttachments.count()
            self.tabAttachments.setCurrentIndex(
                self.tabAttachments.insertTab(tabCount, view, title))
        return
