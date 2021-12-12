import json
import os
import re
import zipfile
import src.Controller.WBXTraceAnalyzer as WBXAnalyzer
from enum import Enum
from typing import Tuple

from src.Common import FileUtility
from src.Common.DumpFileHelper import DumpFileHelper
from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Common.WBXTracerHelper import WBXTraceItemV3, WBXTracerFile
from src.Thirdparty.google_trans_new.google_trans_new import google_translator
from src.Controller import OutlookCtrl
from src.Model.AppModel import appModel


class DumpFileState(Enum):
    noDump = "noDump"
    crashed = "crashed"
    noCrash = "noCrash"


class AnalyzerAction(IntEnum):
    noDescription = 0
    error = 1
    crashed = 2


class MailAnalyzer:
    sBaseSymbolFolder = ""
    sStopAnalyze = False
    sVersionNumber = 10001

    def __init__(self, mailItem: OutlookCtrl.EmailItem, errorDefinition: {}, noticeMessage: {}):
        self.mMailItem = mailItem
        self.mDumpFile = DumpFileHelper(None, "", "")
        self.mCustomerData = None
        self.mAnalyzeResult = {}
        self.mErrorDefinition = errorDefinition
        self.mNoticeMessage = noticeMessage
        self.analyzeMail(False)
        return

    def analyzeMail(self, recheck: bool = False):
        senderName = self.mMailItem.mSenderName
        Logger.d(appModel.getAppTag(), f"mail={senderName}")
        emailFolder = self.mMailItem.mLocalFolder
        if recheck:
            self.mAnalyzeResult = {}
        else:
            self._readResult(emailFolder)
            curVersion = 0
            if "Version" in self.mAnalyzeResult:
                curVersion = self.mAnalyzeResult["Version"]
            if curVersion < MailAnalyzer.sVersionNumber:
                self.mAnalyzeResult = {"Version": MailAnalyzer.sVersionNumber}
                Logger.w(appModel.getAppTag(), f"recheck for version: {curVersion} < {MailAnalyzer.sVersionNumber}")
        if "BaseInfo" not in self.mAnalyzeResult:
            self._saveBaseInfo(self.mMailItem)
        if "Attachment" not in self.mAnalyzeResult:
            self._saveAttachment(self.mMailItem)
        if "Summary" not in self.mAnalyzeResult:
            self.mAnalyzeResult["Summary"] = {
                "Type": "",
                "Description": "",
                "Addition": ""
            }
        # self._translateBody()
        self._handleDumpFile()
        self._handleKeyError()
        self._handleNoticeMessage()
        self._handleTimezone()

        # set pointer
        self.mMailItem.mAnalyzer = self
        self._saveResult(emailFolder)
        return

    def saveResult(self):
        emailFolder = self.mMailItem.mLocalFolder
        self._saveResult(emailFolder)
        return

    def getTranslated(self, waitTranslate: bool):
        if self._translateBody(waitTranslate):
            self.saveResult()
            return self.mAnalyzeResult["Translate"]["translated"]
        else:
            return ""

    def _readResult(self, emailFolder: str):
        resultPath = appModel.getAppAbsolutePath(None, [emailFolder], "analyze.json")
        self.mAnalyzeResult = FileUtility.loadJsonFile(resultPath)
        return

    def _saveResult(self, emailFolder: str):
        resultPath = appModel.getAppAbsolutePath(None, [emailFolder], "analyze.json")
        FileUtility.saveJsonFile(resultPath, self.mAnalyzeResult)
        return

    def _saveBaseInfo(self, emailItem: OutlookCtrl.EmailItem) -> bool:
        if self.mMailItem.mSubject is None:
            self.mMailItem.mSubject = "Unknown"
        version = re.search(r"\d+\.\d+\.\d+\.\d+", self.mMailItem.mSubject)
        if version is not None:
            version = version.group(0)
        else:
            version = ""

        self.mAnalyzeResult["BaseInfo"] = {}
        self.mAnalyzeResult["BaseInfo"]["Folder"] = emailItem.mFolder.mName
        self.mAnalyzeResult["BaseInfo"]["ID"] = emailItem.mID
        self.mAnalyzeResult["BaseInfo"]["Subject"] = emailItem.mSubject
        self.mAnalyzeResult["BaseInfo"]["Body"] = emailItem.mBody
        self.mAnalyzeResult["BaseInfo"]["ReceivedTime"] = emailItem.mReceivedTime.timestamp()
        self.mAnalyzeResult["BaseInfo"]["Sender"] = f"{emailItem.mSenderName} ({emailItem.mSenderEmail})"
        self.mAnalyzeResult["BaseInfo"]["Receiver"] = emailItem.mReceiveName
        self.mAnalyzeResult["BaseInfo"]["To"] = emailItem.mToName
        self.mAnalyzeResult["BaseInfo"]["AppVersion"] = version
        return True

    def _saveAttachment(self, emailItem: OutlookCtrl.EmailItem) -> bool:
        # Attachments
        attachmentList = []
        for attachment in emailItem.mAttachments:
            attachmentList.append(attachment)
        self.mAnalyzeResult["Attachment"] = attachmentList
        return True

    def _translateBody(self, waitTranslate: bool) -> bool:
        # translate via google
        if "Translate" not in self.mAnalyzeResult:
            self.mAnalyzeResult["Translate"] = {}
            if not waitTranslate:
                return False
        if "translated" in self.mAnalyzeResult["Translate"]\
                and len(self.mAnalyzeResult["Translate"]["translated"]) > 0:
            return True
        try:
            translator = google_translator()
            translatedBody = translator.translate(self.mMailItem.mBody, lang_tgt="zh-cn")
            self.mAnalyzeResult["Translate"]["translated"] = translatedBody
            self.mAnalyzeResult["Translate"]["state"] = True
        except Exception as e:
            Logger.e(appModel.getAppTag(), f"translate body failed: {e}")
            return False

        return True

    def _getSymbolLocalPath(self) -> Tuple[bool, str]:
        version = self.mAnalyzeResult["BaseInfo"]["AppVersion"]
        symbolPath = os.path.join(self.sBaseSymbolFolder, version)
        symbolPath = os.path.join(symbolPath, "arm64-v8a")
        if os.path.exists(symbolPath):
            return True, symbolPath
        else:
            return False, symbolPath

    def _updateDumpFileInfo(self, filePath: str) -> bool:
        hasEle, symbolPath = FileUtility.getDictValue(self.mAnalyzeResult, ["DumpFile"], "symbolPath", "")
        if len(symbolPath) > 0:
            return True

        symbolExist, symbolPath = self._getSymbolLocalPath()
        if symbolExist:
            self.mDumpFile.setSymbolFolder(symbolPath)

        crashedThread = self.mDumpFile.getCrashedThread()
        self.mAnalyzeResult["DumpFile"]["path"] = filePath
        self.mAnalyzeResult["DumpFile"]["symbolPath"] = symbolPath
        self.mAnalyzeResult["DumpFile"]["firstException"] = ""
        if crashedThread is None:
            self.mAnalyzeResult["DumpFile"]["state"] = DumpFileState.noCrash.value
        else:
            self.mAnalyzeResult["DumpFile"]["state"] = DumpFileState.crashed.value
            if len(crashedThread.mStacks) > 0 \
                    and len(crashedThread.mStacks[0].mSymbol) > 0:
                self.mAnalyzeResult["DumpFile"]["firstException"] = crashedThread.mStacks[0].mSymbol[0]
        return True

    def _handleDumpFile(self) -> bool:
        if "DumpFile" in self.mAnalyzeResult:
            # only check if symbols file is ready
            return self._updateDumpFileInfo(self.mAnalyzeResult["DumpFile"]["path"])
        else:
            self.mAnalyzeResult["DumpFile"] = {}
            self.mAnalyzeResult["DumpFile"]["state"] = DumpFileState.noDump.value
            self.mAnalyzeResult["DumpFile"]["path"] = ""
            if "Attachment" not in self.mAnalyzeResult:
                return False

            for attachPath in self.mAnalyzeResult["Attachment"]:
                if re.search(r".dmp$", attachPath, flags=re.IGNORECASE):
                    self.mDumpFile.openDumpFile(attachPath, True)
                    if self.mDumpFile.getCrashedThread() is None:
                        continue
                    return self._updateDumpFileInfo(attachPath)
                elif re.search(r".zip$", attachPath, flags=re.IGNORECASE):
                    if not zipfile.is_zipfile(attachPath):
                        continue
                    zipFile = zipfile.ZipFile(attachPath)
                    for subFileName in zipFile.namelist():
                        if re.search(r".dmp$", subFileName, flags=re.IGNORECASE):
                            fileData = zipFile.read(subFileName)
                            self.mDumpFile.openDumpData(fileData, True)
                            if self.mDumpFile.getCrashedThread() is None:
                                continue
                            return self._updateDumpFileInfo(attachPath + "?" + subFileName)
                        else:
                            continue
        return False

    def _onCheckInTrace(self, item: WBXTraceItemV3, param: [any]):
        checkList: {} = param[0]
        if len(checkList) == 0:
            return False
        for key, detail in checkList.items():
            if self.sStopAnalyze:
                return False
            if key in item.mMessage:
                # item.mPosInFile
                self.mAnalyzeResult[param[2]][key] = {
                    "errName": detail[0],
                    "errType": detail[1],
                    "logIndex": item.mIndex,
                    "logPos": item.mPosInFile,
                    "logFile": param[1],
                }
                del checkList[key]
                return True
        return True

    def _handleKeyError(self) -> bool:
        recheck = appModel.readConfig(self.__class__.__name__, "recheck error", False)
        if "KeyError" not in self.mAnalyzeResult or recheck:
            self.mAnalyzeResult["KeyError"] = {}
        needToCheck = {}
        for err, name in self.mErrorDefinition.items():
            if err not in self.mAnalyzeResult["KeyError"]:
                needToCheck[err] = name
        if len(needToCheck) == 0:
            return True

        if "Attachment" not in self.mAnalyzeResult:
            return False

        for attachPath in self.mAnalyzeResult["Attachment"]:
            # every error only check 1 occur
            needToCheck = {}
            for err, name in self.mErrorDefinition.items():
                if err not in self.mAnalyzeResult["KeyError"]:
                    needToCheck[err] = name
            if len(needToCheck) == 0:
                continue

            WBXAnalyzer.setErrDefine(json.dumps(needToCheck))
            if re.search(r".wbt$", attachPath, flags=re.IGNORECASE):
                if WBXAnalyzer.isValid():
                    errDetail = WBXAnalyzer.analyzeFile(attachPath)
                    self.mAnalyzeResult["KeyError"].update(json.loads(errDetail))
                else:
                    tracerFile = WBXTracerFile(attachPath, True)
                    if not tracerFile.readTraces(self._onCheckInTrace, [needToCheck, attachPath, "KeyError"]):
                        Logger.e(appModel.getAppTag(), f"readTrace from {attachPath} failed")
            elif re.search(r".zip$", attachPath, flags=re.IGNORECASE):
                if not zipfile.is_zipfile(attachPath):
                    continue
                zipFile = zipfile.ZipFile(attachPath)
                for subFileName in zipFile.namelist():
                    if self.sStopAnalyze:
                        break
                    if re.search(r".wbt$", subFileName, flags=re.IGNORECASE):
                        try:
                            fileData = zipFile.read(subFileName)
                            fullSubFileName = f"{attachPath}?{subFileName}"
                            if WBXAnalyzer.isValid():
                                errDetail = WBXAnalyzer.analyzeData(fileData, fullSubFileName)
                                self.mAnalyzeResult["KeyError"].update(json.loads(errDetail))
                            else:
                                tracerFile = WBXTracerFile(fileData, False)
                                if not tracerFile.readTraces(self._onCheckInTrace,
                                                             [needToCheck, fullSubFileName, "KeyError"]):
                                    Logger.e(appModel.getAppTag(), f"readTrace from {fullSubFileName} failed")
                        except zipfile.BadZipFile as e:
                            Logger.e(appModel.getAppTag(), f"zipFile.read {subFileName} exception: {e}")
                    else:
                        continue
        # set no error value as ""
        for err, name in self.mErrorDefinition.items():
            if err not in self.mAnalyzeResult["KeyError"]:
                self.mAnalyzeResult["KeyError"][err] = {}
        return True

    def _handleNoticeMessage(self) -> bool:
        recheck = appModel.readConfig(self.__class__.__name__, "recheck notice", False)
        if "NoticeMessage" not in self.mAnalyzeResult or recheck:
            self.mAnalyzeResult["NoticeMessage"] = {}
        needToCheck = {}
        for err, name in self.mNoticeMessage.items():
            if err not in self.mAnalyzeResult["NoticeMessage"]:
                needToCheck[err] = name
        if len(needToCheck) == 0:
            return True

        if "Attachment" not in self.mAnalyzeResult:
            return False

        for attachPath in self.mAnalyzeResult["Attachment"]:
            # every error only check 1 occur
            needToCheck = {}
            for err, name in self.mNoticeMessage.items():
                if err not in self.mAnalyzeResult["NoticeMessage"]:
                    needToCheck[err] = name
            if len(needToCheck) == 0:
                continue

            WBXAnalyzer.setErrDefine(json.dumps(needToCheck))
            if re.search(r".wbt$", attachPath, flags=re.IGNORECASE):
                if WBXAnalyzer.isValid():
                    errDetail = WBXAnalyzer.analyzeFile(attachPath)
                    self.mAnalyzeResult["NoticeMessage"].update(json.loads(errDetail))
                else:
                    tracerFile = WBXTracerFile(attachPath, True)
                    if not tracerFile.readTraces(self._onCheckInTrace, [needToCheck, attachPath, "NoticeMessage"]):
                        Logger.e(appModel.getAppTag(), f"readTrace from {attachPath} failed")
            elif re.search(r".zip$", attachPath, flags=re.IGNORECASE):
                if not zipfile.is_zipfile(attachPath):
                    continue
                zipFile = zipfile.ZipFile(attachPath)
                for subFileName in zipFile.namelist():
                    if self.sStopAnalyze:
                        break
                    if re.search(r".wbt$", subFileName, flags=re.IGNORECASE):
                        try:
                            fileData = zipFile.read(subFileName)
                            fullSubFileName = f"{attachPath}?{subFileName}"
                            if WBXAnalyzer.isValid():
                                errDetail = WBXAnalyzer.analyzeData(fileData, fullSubFileName)
                                self.mAnalyzeResult["NoticeMessage"].update(json.loads(errDetail))
                            else:
                                tracerFile = WBXTracerFile(fileData, False)
                                if not tracerFile.readTraces(self._onCheckInTrace,
                                                             [needToCheck, fullSubFileName, "NoticeMessage"]):
                                    Logger.e(appModel.getAppTag(), f"readTrace from {fullSubFileName} failed")
                        except zipfile.BadZipFile as e:
                            Logger.e(appModel.getAppTag(), f"zipFile.read {subFileName} exception: {e}")
                    else:
                        continue
        # set no error value as ""
        for notice, textColor in self.mNoticeMessage.items():
            if notice not in self.mAnalyzeResult["NoticeMessage"]:
                self.mAnalyzeResult["NoticeMessage"][notice] = {}
        return True

    def _handleTimezone(self) -> bool:
        if "AppTimezone" in self.mAnalyzeResult["BaseInfo"]:
            return True
        self.mAnalyzeResult["BaseInfo"]["AppTimezone"] = "Unknown"
        if "Attachment" not in self.mAnalyzeResult:
            return False

        for attachPath in self.mAnalyzeResult["Attachment"]:
            if re.search(r".wbt$", attachPath, flags=re.IGNORECASE):
                timezoneID = WBXTracerFile(attachPath, True).getTimezoneID()
                if len(timezoneID) > 0:
                    self.mAnalyzeResult["BaseInfo"]["AppTimezone"] = timezoneID
                    return True
            elif re.search(r".zip$", attachPath, flags=re.IGNORECASE):
                if not zipfile.is_zipfile(attachPath):
                    continue
                zipFile = zipfile.ZipFile(attachPath)
                for subFileName in zipFile.namelist():
                    if self.sStopAnalyze:
                        break
                    if re.search(r".wbt$", subFileName, flags=re.IGNORECASE):
                        fileData = zipFile.read(subFileName)
                        timezoneID = WBXTracerFile(fileData, False).getTimezoneID()
                        if len(timezoneID) > 0:
                            self.mAnalyzeResult["BaseInfo"]["AppTimezone"] = timezoneID
                            return True
                    else:
                        continue
        return True

    def getDescription(self) -> Tuple[AnalyzerAction, str]:
        """
        rule:
          no attachments: no description
          no error key: error
          dump state
        :return:
        """
        retAction = AnalyzerAction.noDescription
        retString = ""
        if "Attachment" not in self.mAnalyzeResult or len(self.mAnalyzeResult["Attachment"]) == 0:
            return retAction, "no description"
        if "KeyError" in self.mAnalyzeResult:
            for err, errDetail in self.mAnalyzeResult["KeyError"].items():
                if len(errDetail) > 0:
                    if len(retString) > 0:
                        retString += os.linesep + errDetail["errName"]
                    else:
                        retString += errDetail["errName"]
                    retAction = AnalyzerAction.error
        if "NoticeMessage" in self.mAnalyzeResult:
            for notice, noticeDetail in self.mAnalyzeResult["NoticeMessage"].items():
                if len(noticeDetail) > 0:
                    if len(retString) > 0:
                        retString += os.linesep + noticeDetail["errName"]
                    else:
                        retString += noticeDetail["errName"]
        if "DumpFile" in self.mAnalyzeResult:
            dumpState = self.mAnalyzeResult["DumpFile"]["state"]
            if DumpFileState.crashed.value == dumpState:
                retAction = AnalyzerAction.crashed
                if len(retString) > 0:
                    retString += os.linesep
                retString += dumpState
                if "firstException" in self.mAnalyzeResult["DumpFile"]:
                    firstException = self.mAnalyzeResult["DumpFile"]["firstException"]
                    if len(firstException):
                        retString += "@ " + firstException
        return retAction, retString

    def getSummary(self):
        if "Summary" in self.mAnalyzeResult:
            errType = self.mAnalyzeResult["Summary"]["Type"]
            errDescription = self.mAnalyzeResult["Summary"]["Description"]
            errAddition = self.mAnalyzeResult["Summary"]["Addition"]
            if len(errType) == 0:
                return ""
            return f"{errType}: {errDescription}({errAddition})"
        else:
            return ""
