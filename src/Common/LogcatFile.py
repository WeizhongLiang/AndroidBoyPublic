import os
import re
from datetime import datetime
from typing import Tuple

from src.Common import DateTimeHelper
from src.Common.Logger import Logger, LoggerLevel
from src.Model.AppModel import appModel


class LogcatItem:
    getLogLevelByStr = {
        'V': LoggerLevel.Verbose,
        'D': LoggerLevel.Debug,
        'I': LoggerLevel.Info,
        'W': LoggerLevel.Warning,
        'E': LoggerLevel.Error,
        'F': LoggerLevel.Fatal,
        'S': LoggerLevel.Silent
    }

    def __init__(self, index: int, date: float, pid: str, tid: str, package: str, level: str, tag: str, msg: str):
        self.mIndex = index
        self.mDate = date
        self.mPID = pid
        self.mTID = tid
        self.mPackage = package
        self.mLevel = level
        self.mTag = tag
        self.mMessage = msg
        return

    def getDateTimeStr(self) -> str:
        return DateTimeHelper.getTimestampString(self.mDate, None)

    def getLoggerLevel(self) -> LoggerLevel:
        return LogcatItem.getLogLevelByStr.get(self.mLevel[0])


class LogcatFile:
    _accessNone = 0
    _accessWrite = 1
    _accessRead = 2
    _flushCount = 1024
    _defaultTime = datetime.strptime("1971-01-01 00:00:00.0", "%Y-%m-%d %H:%M:%S.%f")
    _defaultYear = _defaultTime.year

    regSpace = r"\s{1,}"
    regIndex = r"\d{1,}"
    regDatetime1 = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3,}"  # 2018-02-07 06:16:28.555
    regDatetime2 = r"\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3,}"  # 02-07 06:16:28.555
    regDatetime3 = r"\d{0,}\.\d{3,}"  # 1517955388.555
    regPID_TID = r"\d{0,}-\d{0,}"
    regPID_TID2 = r"\d{0,}\s{1,}\d{0,}"
    regPackageName = r"[A-Za-z]\S{0,}"
    regLevel = r"(V|D|I|W|E)"
    regLevel2 = r"(Verbose|Debug|Info|Warning|Error|Fatal|Silent)"
    regTag = r".+"
    regMessage = r"\s.{0,}"
    regulars = {
        -1: [re.compile(r".+"), -1],
        0: [re.compile(fr"^{regDatetime1}\s{regPID_TID}/{regPackageName}\s{regLevel}/{regTag}:"), 3],
        1: [re.compile(fr"^{regDatetime1}\s{regPID_TID}/{regPackageName}\s{regLevel}:"), 3],
        2: [re.compile(fr"^{regDatetime1}\s{regPID_TID}\s{regLevel}/{regTag}:"), 3],
        3: [re.compile(fr"^{regDatetime1}\s{regPID_TID}\s{regLevel}:"), 3],
        4: [re.compile(fr"^{regDatetime1}\s{regPackageName}\s{regLevel}/{regTag}:"), 3],
        5: [re.compile(fr"^{regDatetime1}\s{regPackageName}\s{regLevel}:"), 3],
        6: [re.compile(fr"^{regDatetime1}\s{regLevel}/{regTag}:"), 2],
        7: [re.compile(fr"^{regDatetime1}\s{regLevel}:"), 2],

        8: [re.compile(fr"^{regDatetime2}\s{regPID_TID}/{regPackageName}\s{regLevel}/{regTag}:"), 3],
        9: [re.compile(fr"^{regDatetime2}\s{regPID_TID}/{regPackageName}\s{regLevel}:"), 3],
        10: [re.compile(fr"^{regDatetime2}\s{regPID_TID}\s{regLevel}/{regTag}:"), 3],
        11: [re.compile(fr"^{regDatetime2}\s{regPID_TID}\s{regLevel}:"), 3],
        12: [re.compile(fr"^{regDatetime2}\s{regPackageName}\s{regLevel}/{regTag}:"), 3],
        13: [re.compile(fr"^{regDatetime2}\s{regPackageName}\s{regLevel}:"), 3],
        14: [re.compile(fr"^{regDatetime2}\s{regLevel}/{regTag}:"), 2],
        15: [re.compile(fr"^{regDatetime2}\s{regLevel}:"), 2],

        16: [re.compile(fr"^{regDatetime3}\s{regPID_TID}/{regPackageName}\s{regLevel}/{regTag}:"), 2],
        17: [re.compile(fr"^{regDatetime3}\s{regPID_TID}/{regPackageName}\s{regLevel}:"), 2],
        18: [re.compile(fr"^{regDatetime3}\s{regPID_TID}\s{regLevel}/{regTag}:"), 2],
        19: [re.compile(fr"^{regDatetime3}\s{regPID_TID}\s{regLevel}:"), 2],
        20: [re.compile(fr"^{regDatetime3}\s{regPackageName}\s{regLevel}/{regTag}:"), 2],
        21: [re.compile(fr"^{regDatetime3}\s{regPackageName}\s{regLevel}:"), 2],
        22: [re.compile(fr"^{regDatetime3}\s{regLevel}/{regTag}:"), 1],
        23: [re.compile(fr"^{regDatetime3}\s{regLevel}:"), 1],

        24: [re.compile(fr"^{regPID_TID}/{regPackageName}\s{regLevel}/{regTag}:"), 1],
        25: [re.compile(fr"^{regPID_TID}/{regPackageName}\s{regLevel}:"), 1],
        26: [re.compile(fr"^{regPID_TID}\s{regLevel}/{regTag}:"), 1],
        27: [re.compile(fr"^{regPID_TID}\s{regLevel}:"), 1],
        28: [re.compile(fr"^{regPackageName}\s{regLevel}/{regTag}:"), 1],
        29: [re.compile(fr"^{regPackageName}\s{regLevel}:"), 1],
        30: [re.compile(fr"^{regLevel}/{regTag}:"), 0],
        31: [re.compile(fr"^{regLevel}:"), 0],

        32: [re.compile(fr"^{regDatetime2}{regSpace}{regPID_TID2}{regSpace}{regLevel}{regSpace}{regTag}:"), 5],

        33: [re.compile(fr"^{regIndex}{regSpace}{regDatetime1}"
                        fr"{regSpace}{regPID_TID2}{regSpace}{regLevel2}{regSpace}{regTag}:"), 7],

        999: [re.compile(r""), 0],   # last choice ... just show it
    }

    @staticmethod
    def _formatNonTime(logSplit: [str], startIndex: int, fmtType: int):
        if fmtType == 0:
            sec = re.split(r"/", logSplit[startIndex], 1)
            p_t = re.split(r"-", sec[0], 1)
            levels = logSplit[startIndex+1].split("/", 1)
            tags = levels[1].split(":", 1)
            # [date, time], pid, tid, package, level, tag, msg
            return p_t[0], p_t[1], sec[1], levels[0], tags[0], tags[1]
        elif fmtType == 1:
            sec = re.split(r"/", logSplit[startIndex], 1)
            p_t = re.split(r"-", sec[0], 1)
            levels = logSplit[startIndex+1].split(":", 1)
            # [date, time], pid, tid, package, level, [tag], msg
            return p_t[0], p_t[1], sec[1], levels[0], "", levels[1]
        elif fmtType == 2:
            p_t = re.split(r"-", logSplit[startIndex], 1)
            levels = logSplit[startIndex+1].split("/", 1)
            tags = levels[1].split(":", 1)
            # [date, time], pid, tid, [package], level, tag, msg
            return p_t[0], p_t[1], "", levels[0], tags[0], tags[1]
        elif fmtType == 3:
            p_t = re.split(r"-", logSplit[startIndex], 1)
            levels = logSplit[startIndex+1].split(":", 1)
            # [date, time], pid, tid, [package], level, [tag], msg
            return p_t[0], p_t[1], "", levels[0], "", levels[1]
        elif fmtType == 4:
            levels = logSplit[startIndex+1].split("/", 1)
            tags = levels[1].split(":", 1)
            # [date, time], [pid, tid], package, level, tag, msg
            return "", "", logSplit[startIndex], levels[0], tags[0], tags[1]
        elif fmtType == 5:
            levels = logSplit[startIndex+1].split(":", 1)
            # [date, time], [pid, tid], package, level, [tag], msg
            return "", "", logSplit[startIndex], levels[0], "", levels[1]
        elif fmtType == 6:
            levels = logSplit[startIndex].split("/", 1)
            tags = levels[1].split(":", 1)
            # [date, time], [pid, tid], [package], level, tag, msg
            return "", "", "", levels[0], tags[0], tags[1]
        elif fmtType == 7:
            tags = logSplit[startIndex].split(":", 1)
            # [date, time], [pid, tid], [package], level, [tag], msg
            return "", "", "", tags[0], "", tags[1]
        else:
            return "", "", "", "", "", ""

    @staticmethod
    def formatData(logLine: str, fmtType: int, pattern: [re.Pattern, int]) -> LogcatItem:
        if pattern[1] == 0:
            logSplit = [logLine]
        else:
            logSplit = re.split(r"\s+", logLine, maxsplit=pattern[1])
        try:
            if fmtType == 999:
                return LogcatItem(-1, LogcatFile._defaultTime.timestamp(), "", "", "", "V", "", logLine)
            elif fmtType in range(0, 8):
                logTime = datetime.strptime(f"{logSplit[0]} {logSplit[1]}", "%Y-%m-%d %H:%M:%S.%f")
                ret = LogcatFile._formatNonTime(logSplit, 2, fmtType)
                return LogcatItem(-1, logTime.timestamp(),
                                  ret[0], ret[1], ret[2], ret[3], ret[4], ret[5])
            elif fmtType in range(8, 16):
                logTime = datetime.strptime(
                    f"{LogcatFile._defaultYear}-{logSplit[0]} {logSplit[1]}", "%Y-%m-%d %H:%M:%S.%f")
                ret = LogcatFile._formatNonTime(logSplit, 2, fmtType - 8)
                return LogcatItem(-1, logTime.timestamp(),
                                  ret[0], ret[1], ret[2], ret[3], ret[4], ret[5])
            elif fmtType in range(16, 24):
                ret = LogcatFile._formatNonTime(logSplit, 1, fmtType - 16)
                return LogcatItem(-1, float(logSplit[0]),
                                  ret[0], ret[1], ret[2], ret[3], ret[4], ret[5])
            elif fmtType in range(24, 32):
                ret = LogcatFile._formatNonTime(logSplit, 0, fmtType - 24)
                return LogcatItem(-1, LogcatFile._defaultTime.timestamp(),
                                  ret[0], ret[1], ret[2], ret[3], ret[4], ret[5])
            elif fmtType == 32:
                logTime = datetime.strptime(
                    f"{LogcatFile._defaultYear}-{logSplit[0]} {logSplit[1]}", "%Y-%m-%d %H:%M:%S.%f")
                tags = logSplit[pattern[1]].split(":", 1)
                return LogcatItem(-1, logTime.timestamp(),
                                  logSplit[2], logSplit[3], "", logSplit[4], tags[0], tags[1])
            elif fmtType == 33:
                logTime = datetime.strptime(f"{logSplit[1]} {logSplit[2]}", "%Y-%m-%d %H:%M:%S.%f")
                return LogcatItem(-1, logTime.timestamp(),
                                  logSplit[3], logSplit[4], "", logSplit[5], logSplit[6], logSplit[7])
        except IndexError as e:
            Logger.e(appModel.getAppTag(), f"formatData exception:{logLine}, error:{e}")
        except ValueError as e:
            Logger.e(appModel.getAppTag(), f"formatData exception:{logLine}, error:{e}")

        return LogcatItem(-1, LogcatFile._defaultTime.timestamp(),
                          "", "", "", "", "", "")

    @staticmethod
    def detectFormat(logLine: str) -> Tuple[int, list[re.Pattern, int]]:
        invalidReg = None
        for fmtType, reg in LogcatFile.regulars.items():
            if fmtType < 0:
                invalidReg = reg
                continue
            if reg[0].search(logLine):
                return fmtType, reg
        return -1, invalidReg

    def __init__(self):
        self._mAccess = self._accessNone
        self._mWriteFile = None
        self._mWriteFilePath = ""
        self._mFlushCount = self._flushCount
        self._mTraceCount = 0

        # for read
        self._mFileContent = None
        return

    def createFile(self, path: str, encoding):
        Logger.i(appModel.getAppTag(), f"path = {path}")
        try:
            self._mWriteFile = open(path, mode='w', encoding=encoding)
        except Exception as e:
            Logger.e(appModel.getAppTag(), f"path = {path}, exception: {e}")
            return False
        self._mAccess = self._accessWrite
        self._mFlushCount = self._flushCount
        self._mTraceCount = 0
        self._mWriteFilePath = path
        return True

    def writeTraces(self, trace: str):
        if self._mAccess != self._accessWrite:
            return
        self._mWriteFile.write(trace)
        self._mWriteFile.write('\n')
        self._mTraceCount += 1
        self._mFlushCount -= 1
        if self._mFlushCount == 0:
            self.flushWrite()
            self._mFlushCount = self._flushCount
        return

    def flushWrite(self):
        if self._mAccess != self._accessWrite:
            return
        # Logger.i(appModel.getAppTag(), f"")
        self._mWriteFile.flush()
        return

    def writePIDName(self, PID: int, name: str):
        if self._mAccess != self._accessWrite:
            return
        self._mWriteFile.write(f"<tag>pid=[{PID}] name=[{name}]\n")
        return

    def closeWrite(self):
        if self._mAccess == self._accessNone:
            return "", 0
        Logger.i(appModel.getAppTag(), f"path = {self._mWriteFilePath}")
        self._mAccess = self._accessNone
        if self._mWriteFile is not None:
            self._mWriteFile.close()
        filePath = self._mWriteFilePath
        traceCount = self._mTraceCount
        if self._mTraceCount == 0:
            # auto del blank file
            os.remove(self._mWriteFilePath)
        self._mFileContent = None
        self._mTraceCount = 0
        self._mWriteFilePath = ""
        return filePath, traceCount

    def getWriteFilePath(self):
        return self._mWriteFilePath

    def openFile(self, path: str, encoding):
        Logger.i(appModel.getAppTag(), f"path = {path}")
        try:
            file = open(path, mode="r", encoding=encoding, errors="ignore")
            file.seek(0, 2)
            fileLen = file.tell()
            file.seek(0, 0)
            self.setContent(file.read(fileLen))
            file.close()
        except Exception as e:
            Logger.e(appModel.getAppTag(), f"path = {path}, exception: {e}")
            return False
        return True

    def setContent(self, fileContent):
        Logger.i(appModel.getAppTag(), "")
        self._mFileContent = fileContent
        self._mAccess = self._accessRead
        self._calTraceCount(self._mFileContent)
        return True

    def _calTraceCount(self, contentData):
        Logger.i(appModel.getAppTag(), "begin")
        procTime = DateTimeHelper.ProcessTime()
        itemCount = 0
        lineStart = 0
        lineEnd = contentData.find("\n", lineStart)
        while lineEnd > 0:
            if contentData.find("<tag>", lineStart, lineStart + 6) != lineStart:
                itemCount += 1
            lineStart = lineEnd + 1
            lineEnd = contentData.find("\n", lineStart)
        self._mTraceCount = itemCount
        Logger.i(appModel.getAppTag(), f"end total {itemCount} rows "
                                       f"in {procTime.getMicroseconds()} seconds ")
        return itemCount

    def readTraces(self, onTrace, param: [any]):
        if self._mAccess != self._accessRead:
            return False
        Logger.i(appModel.getAppTag(), "begin")
        procTime = DateTimeHelper.ProcessTime()
        contentData = self._mFileContent
        lineStart = 0
        lineEnd = contentData.find("\n", lineStart)
        if lineEnd < 0:
            lineEnd = len(contentData)
        while lineEnd >= 0:
            if contentData.find("<tag>", lineStart, lineStart + 6) != lineStart:
                logLine = contentData[lineStart:lineEnd]
                fmtType, pattern = LogcatFile.detectFormat(logLine)
                if fmtType > 0:
                    logItem = LogcatFile.formatData(logLine, fmtType, pattern)
                    if onTrace is not None:
                        if not onTrace(logItem, param):
                            break
            lineStart = lineEnd + 1
            lineEnd = contentData.find("\n", lineStart)
        Logger.i(appModel.getAppTag(), f"end read {self._mTraceCount} rows "
                                       f"in {procTime.getMicroseconds()} seconds ")
        return True

    def getTraceCount(self):
        return self._mTraceCount
