import _io
import os
import re
import subprocess
import threading
import time
from datetime import datetime

from src.Common import StringUtility, MathUtility, Const
from src.Common.Logger import Logger, LoggerLevel
from src.Common.RepeatTimer import RepeatTimer
from src.Model.AppModel import appModel

_nowYear = datetime.now().year
_adbLock: threading.RLock = threading.RLock()


def adbReturn(deviceId, params: str, needLog=False):
    shellParams = params.split(' ')
    shellParams.insert(0, "adb")
    if deviceId is not None:
        shellParams.insert(1, "-s")
        shellParams.insert(2, deviceId)
    _adbLock.acquire()
    try:
        if needLog:
            Logger.i(appModel.getAppTag(), f"shellParams={shellParams}")
        ret = subprocess.check_output(shellParams)
        if ret is not None:
            ret = ret.decode("utf-8").rstrip(os.linesep)
        else:
            ret = ""
        _adbLock.release()
        return ret
    except Exception as e:
        _adbLock.release()
        Logger.i(appModel.getAppTag(), f"shellParams={shellParams}, exception={e}")
        return ""


class AndroidLogItem:
    getLogLevelByStr = {
        'V': LoggerLevel.Verbose,
        'D': LoggerLevel.Debug,
        'I': LoggerLevel.Info,
        'W': LoggerLevel.Warning,
        'E': LoggerLevel.Error,
        'F': LoggerLevel.Fatal,
        'S': LoggerLevel.Silent
    }

    def __init__(self, logStr: str):
        # logBytes = b'04-30 14:58:53.366  1038  1339 I tag: msg'
        # logBytes = b'--------- beginning of x'
        # print(logStr)
        try:
            self._mMsg = logStr
            if re.search(r"^\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}", self._mMsg, flags=re.IGNORECASE):
                self._mDatetimeStr = f"{_nowYear}-{self._mMsg[0:18]}"
                self._mTagPos = self._mMsg[32:].find(':')
                self._mValid = True
            else:
                self._mDatetimeStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                self._mTagPos = 0
                self._mValid = False
        except Exception as e:
            self._mDatetimeStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            self._mTagPos = 0
            self._mValid = False
            Logger.e(appModel.getAppTag(), f"{logStr}: exception: {e}")
        return

    def isValid(self):
        return self._mValid

    def getDateTimeStr(self):
        return self._mDatetimeStr

    def getPID(self):
        if self._mValid:
            return self._mMsg[19:24]
        else:
            return "0"

    def getTID(self):
        if self._mValid:
            return self._mMsg[25:30]
        else:
            return "0"

    def getLogLevel(self):
        if self._mValid:
            return self.getLogLevelByStr.get(self._mMsg[31:32])
        else:
            return self.getLogLevelByStr.get('V')

    def getTag(self):
        if self._mValid:
            return self._mMsg[32:32 + self._mTagPos - 1]
        else:
            return ""

    def getMsg(self):
        if self._mValid:
            return self._mMsg[32 + self._mTagPos + 2:]
        else:
            return self._mMsg

    def getFull(self):
        return self._mMsg


class AndroidPackage:
    # package:/data/app/com.miui.abc-yVME9t1AlMpw5Cq1Y1MT8w==s
    # /base.apk=com.miui.abc uid:1000
    def __init__(self, item):
        self.mIsValid = False
        try:
            posPackage = item.find("package:") + len("package:")
            posPackageEnd = item.find("/base.apk=")
            if posPackageEnd < 0:
                return
            posAPK = posPackageEnd + len("/base.apk=")
            posAPKEnd = item.find(" uid:")
            if posAPKEnd < 0:
                posAPKEnd = len(item)
                posUID = posAPKEnd
            else:
                posUID = posAPKEnd + len(" uid:")
            self.mPackage = item[posPackage:posPackageEnd]
            self.mAPK = item[posAPK:posAPKEnd]
            self.mUID = item[posUID:]
            self.mIsValid = True
        except Exception:
            return
        return

    def __str__(self):
        return f"{self.mAPK}-{self.mUID}"

    def __lt__(self, other):
        return self.__str__() < other.__str__()


class AndroidProcess:
    # USER           UID   PID  PPID NAME
    # u0_a275      10275  9331   680 com.cisco.webex.meetings
    # u0_a275      10275  9431   680 com.cisco.webex.meetings:abc
    def __init__(self, item):
        self.mIsValid = False
        try:
            lineWords = StringUtility.splitBySpace(item)
            self.mUser = lineWords[0]  # user name
            self.mUID = int(lineWords[1])  # package id
            self.mPID = int(lineWords[2])  # process id
            self.mPPID = int(lineWords[3])  # parent process id
            self.mNAME = lineWords[4]
            self.mIsValid = True
        except Exception:
            return

    def __str__(self):
        return f"{self.mNAME}-{self.mPID}"

    def __lt__(self, other):
        return self.__str__() < other.__str__()


class AndroidDevice:
    def __init__(self, deviceId):
        self.mIsValid = False
        self.mID = deviceId
        self.mProductBrand = adbReturn(self.mID, "shell getprop ro.product.brand")  # Xiaomi
        self.mProductModel = adbReturn(self.mID, "shell getprop ro.product.model")  # MI 8 UD
        self.mProductName = adbReturn(self.mID, "shell getprop ro.product.name")  # equuleus
        self.mProductBoard = adbReturn(self.mID, "shell getprop ro.product.board")  # sdm845
        self.mBuildVersionRelease = adbReturn(self.mID, "shell getprop ro.build.version.release")  # 10
        self.mBuildVersionSDK = adbReturn(self.mID, "shell getprop ro.build.version.sdk")  # 29
        self.mABIList = adbReturn(self.mID, "shell getprop ro.product.cpu.abilist")  # arm64-v8a,armeabi-v7a,armeabi
        self._mThreadLogcat = None
        self._mProcessLogcat = None  # subprocess.Popen
        self.mIsValid = True
        return

    def finish(self):
        self.stopCaptureLogcat()
        self.mIsValid = False
        return

    def __str__(self):
        return f"{self.mProductBrand}-{self.mProductModel}" \
               f"(Android {self.mBuildVersionRelease}, API {self.mBuildVersionSDK})"

    def __lt__(self, other):
        return self.__str__() < other.__str__()

    @staticmethod
    def _splitLogs(preLog, logs, onFilter, onAdd):
        lines = logs.split(StringUtility.LineSepBytes)
        lineCount = len(lines)
        if lineCount <= 0:
            return None
        else:
            if preLog is not None:
                lines[0] = preLog + lines[0]
        logItems = []
        for line in lines[0:lineCount - 1]:
            try:
                logItem = AndroidLogItem(line.decode("utf-8"))
                if logItem.isValid():
                    if onFilter is not None and onFilter(logItem) is True:
                        continue
                    logItems.append(logItem)
            except UnicodeDecodeError as e:
                Logger.w(appModel.getAppTag(), f"exception={e}")
                continue
        if len(logItems) > 0 and onAdd is not None:
            onAdd(logItems)
        return lines[lineCount - 1]

    def _onLogcatThread(self, commandStr, onFilter, onAdd):
        if self._mProcessLogcat is None:
            Logger.i(appModel.getAppTag(), f"end with:self._mProcessLogcat is None")
            return

        Logger.i(appModel.getAppTag(), f"begin with commandStr={commandStr}")
        max_buffer_size = 1024 * 100
        preLog = b""
        while self.mIsValid and self._mProcessLogcat is not None:
            output: _io.BufferedReader = self._mProcessLogcat.stdout
            readOut = output.read1(max_buffer_size)
            if len(readOut) > 0:
                preLog = self._splitLogs(preLog, readOut, onFilter, onAdd)
            else:
                time.sleep(0.1)
                # Logger.i(appModel.getAppTag(), f"end with:{readAble}")
                # return
        Logger.i(appModel.getAppTag(), f"end")
        return

    def _onLogcatThreadLine(self, commandStr, onFilter, onAdd):
        if self._mProcessLogcat is None:
            Logger.i(appModel.getAppTag(), f"end with:self._mProcessLogcat is None")
            return

        Logger.i(appModel.getAppTag(), f"begin with commandStr={commandStr}")
        while self.mIsValid and self._mProcessLogcat is not None:
            line = self._mProcessLogcat.stdout.readline().rstrip()
            if not line:
                Logger.i(appModel.getAppTag(), f"end")
                return
            logItem = AndroidLogItem(line.decode("utf-8"))
            if onFilter is not None and onFilter(logItem) is True:
                continue
            if logItem.isValid() and onAdd is not None:
                onAdd([logItem])
        Logger.i(appModel.getAppTag(), f"end")
        return

    def startCaptureLogcat(self, onFilter, onAdd):
        Logger.i(appModel.getAppTag(), "")
        self.stopCaptureLogcat()

        # open handle
        commandStr = ["adb", "-s", self.mID, "logcat"]
        self._mProcessLogcat = subprocess.Popen(commandStr, stdout=subprocess.PIPE, stderr=None)
        self._mThreadLogcat = threading.Thread(target=self._onLogcatThread, args=(commandStr, onFilter, onAdd))
        self._mThreadLogcat.start()
        return

    def stopCaptureLogcat(self):
        Logger.i(appModel.getAppTag(), "")
        if self._mProcessLogcat is not None:
            Logger.i(appModel.getAppTag(), "kill logcat process")
            self._mProcessLogcat.kill()
            self._mProcessLogcat = None
        thread = self._mThreadLogcat
        self._mThreadLogcat = None
        if thread is not None:
            Logger.i(appModel.getAppTag(), f"{self}")
            if thread.is_alive():
                Logger.i(appModel.getAppTag(), "join prev thread")
                thread.join()
        return

    def getPackages(self) -> [AndroidPackage]:
        Logger.i(appModel.getAppTag(), "")
        packages = []
        cmdReturn = adbReturn(self.mID, "shell pm list packages -f -e -3 -U")

        items = cmdReturn.split(os.linesep)
        for item in items:
            package = AndroidPackage(item)
            if package is not None and package.mIsValid:
                packages.append(package)
        packages.sort()
        return packages

    def getProcesses(self, UID) -> [AndroidProcess]:
        Logger.i(appModel.getAppTag(), "")
        processes = []
        cmdReturn = adbReturn(self.mID, f"shell ps -U {UID} -o USER,UID,PID,PPID,NAME")

        items = cmdReturn.split(os.linesep)
        for item in items[1:]:
            process = AndroidProcess(item)
            if process is not None and process.mIsValid:
                processes.append(process)
        processes.sort()
        return processes

    def pushText(self, message):
        adbReturn(self.mID, f"shell input text '{message}'", True)
        return

    def installAPK(self, path: str):
        adbReturn(self.mID, f"install {path}", True)
        return


class AndroidDeviceManager:

    def __init__(self):
        # detect connected device
        self._mConnectListener = None
        self._mConnectPrev = []

        # detect device's process
        self._mProcessDeviceID = ""
        self._mProcessPackageID = ""
        self._mProcessListener = None
        self._mProcessPrev = []

        self._mLockerDetect: threading.RLock = threading.RLock()
        self._mTimerCount = 0
        self._mTimerDetect = None
        if Const.adbDetectTimer > 0:
            self._mTimerDetect = RepeatTimer(Const.adbDetectTimer, self._onDetectHandler)
            self._mTimerDetect.start()
        return

    def finish(self):
        if self._mTimerDetect:
            self._mTimerDetect.cancel()
        return

    def detectConnect(self, connectListener):
        Logger.i(appModel.getAppTag(), "begin")
        self._mLockerDetect.acquire()
        self._mConnectListener = connectListener
        self._mConnectPrev = []
        self._onDetectHandler()     # do first
        self._mLockerDetect.release()
        Logger.i(appModel.getAppTag(), "end")
        return

    def detectProcess(self, deviceID, packageID, processListener):
        Logger.i(appModel.getAppTag(), "begin")
        self._mLockerDetect.acquire()
        self._mProcessListener = processListener
        self._mProcessDeviceID = deviceID
        self._mProcessPackageID = packageID
        self._mProcessPrev = []
        self._mLockerDetect.release()
        Logger.i(appModel.getAppTag(), "end")
        return

    def _onDetectHandler(self):
        # Logger.i(appModel.getAppTag(), "begin")
        self._mLockerDetect.acquire()
        if self._mConnectListener is not None:
            self._onDetectConnect()
        if self._mProcessListener is not None:
            self._onDetectProcess()
        self._mTimerCount += 1
        self._mLockerDetect.release()
        # Logger.i(appModel.getAppTag(), "end")
        return

    def _onDetectConnect(self):
        cmdReturn = adbReturn(None, "devices").split(os.linesep)
        if len(cmdReturn) <= 0:
            return
        getDevIds = []
        for lineText in cmdReturn[1:]:
            if lineText is None or lineText == "":
                continue
            else:
                lineWords = StringUtility.splitBySpace(lineText)
                if lineWords is not None and lineWords[1] == "device":
                    getDevIds.append(lineWords[0])

        added, removed = MathUtility.getDiffInLists(self._mConnectPrev, getDevIds)
        if len(added) == 0 and len(removed) == 0:
            return
        if self._mConnectListener is not None:
            self._mConnectListener(added, removed)
        self._mConnectPrev = getDevIds
        return

    def _onDetectProcess(self):
        deviceID = self._mProcessDeviceID
        packageID = self._mProcessPackageID
        cmdReturn = adbReturn(deviceID, f"shell ps -U {packageID} -o USER,UID,PID,PPID,NAME").split(os.linesep)
        if len(cmdReturn) <= 0:
            return

        getProcessIds = []
        for lineText in cmdReturn[1:]:
            getProcessIds.append(lineText)

        added, removed = MathUtility.getDiffInLists(self._mProcessPrev, getProcessIds)
        if len(added) == 0 and len(removed) == 0:
            return
        if self._mProcessListener is not None:
            self._mProcessListener(added, removed)
        self._mProcessPrev = getProcessIds
        return
