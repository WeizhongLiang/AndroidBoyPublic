import os
import re
import subprocess

from src.Common import StringUtility, SystemHelper, DateTimeHelper
from src.Common.Logger import Logger
from src.Model.AppModel import appModel


class StackInfo:
    def __init__(self):
        self.mText = ""
        self.mInfo = ""
        self.mSymbol = []
        self.mCustomerData = None
        return

    def getFullText(self):
        itemText = self.mText
        for symbol in self.mSymbol:
            if len(symbol) == 0:
                continue
            if symbol[0] != "?":
                itemText += os.linesep + "      " + symbol
        return itemText


class ThreadInfo:
    def __init__(self):
        self.mText = ""
        self.mStacks = []  # ViewDumpFile.StackInfo
        self.mCustomerData = None
        return

    def isCrashed(self):
        return "crash" in self.mText


if SystemHelper.isWindows():
    SYMBOLIZER_APP = "llvm-symbolizer.exe"
    STACKWALK_APP = "minidump_stackwalk.exe"
else:
    SYMBOLIZER_APP = "llvm-symbolizer"
    STACKWALK_APP = "minidump_stackwalk"


class DumpFileHelper:
    def __init__(self, onStackInfoUpdated, symbolFolder: str, dumpFilePath: str):
        Logger.d(appModel.getAppTag(), "")
        self._mOnStackInfoUpdated = onStackInfoUpdated
        self._mReadDumpOutput = ""
        self._mOpenError = ""
        self._mFileInfo = ""
        self._mThreads = []  # ViewDumpFile.ThreadInfo
        self._mSymbolFolder = symbolFolder
        if dumpFilePath is not None and len(dumpFilePath) > 0:
            self.openDumpFile(dumpFilePath)
        return

    def getThreads(self) -> [ThreadInfo]:
        return self._mThreads

    def getCrashedThread(self):
        """ return ThreadInfo or None """
        for thread in self._mThreads:
            if thread.isCrashed():
                return thread
        return None

    def getFileInfo(self):
        return self._mFileInfo

    def setStackInfoUpdatedCallback(self, onStackInfoUpdated):
        self._mOnStackInfoUpdated = onStackInfoUpdated
        return

    def setSymbolFolder(self, folder: str):
        self._mSymbolFolder = folder
        self._symbolizeStacks(self._mThreads, self._mSymbolFolder, self._mOnStackInfoUpdated)
        return

    def getSymbolFolder(self):
        return self._mSymbolFolder

    def openDumpFile(self, path: str, crashedOnly: bool = False) -> bool:
        Logger.d(appModel.getAppTag(), "")

        if not os.path.exists(path):
            return False

        stackWalk = appModel.getExtToolsFile("dump", STACKWALK_APP)
        if not os.path.exists(stackWalk):
            return False
        stackWalkProcess = subprocess.Popen([stackWalk, "-s", path],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = stackWalkProcess.communicate()
        self._mReadDumpOutput = stdout.decode("utf-8")
        self._mOpenError = stderr.decode("utf-8")
        if len(self._mReadDumpOutput) == 0 and len(self._mOpenError) != 0:
            return False

        # format dump output
        self._mFileInfo, self._mThreads = self._formatDumpOutput(self._mReadDumpOutput.split(os.linesep), crashedOnly)
        if os.path.exists(self._mSymbolFolder):
            self._symbolizeStacks(self._mThreads, self._mSymbolFolder, self._mOnStackInfoUpdated)
        return True

    def openDumpData(self, data, crashedOnly: bool = False) -> bool:
        Logger.d(appModel.getAppTag(), "")

        if not data or len(data) <= 0:
            return False

        tempDumpPath = appModel.getTmpFile(f"{DateTimeHelper.getNowString('%Y%m%d_%H%M%S')}.dmp")
        # save temp file
        tempDump = open(tempDumpPath, "wb")
        tempDump.write(data)
        tempDump.close()
        openReturn = self.openDumpFile(tempDumpPath, crashedOnly)
        # remove temp file
        os.remove(tempDumpPath)

        return openReturn

    def getOpenError(self):
        return self._mOpenError

    @staticmethod
    def _formatDumpOutput(lines: [str], crashedOnly: bool = False):
        Logger.d(appModel.getAppTag(), f"begin")
        thread = None
        stack = None
        threads = []
        fileInfo = ""
        for line in lines:
            if re.search(r"^Thread", line, flags=re.IGNORECASE):
                # example: Thread 103 (crashed)
                if thread is not None:
                    if stack is not None:
                        thread.mStacks.append(stack)
                        stack = None
                    threads.append(thread)
                    if crashedOnly and thread.isCrashed():
                        return fileInfo, threads
                thread = ThreadInfo()
                thread.mText = line
            elif re.search(r"^ *(0|[1-9][0-9]*).+ 0x", line, flags=re.IGNORECASE):
                # example: 5  libc.so + 0x1d4288
                if stack is not None:
                    if thread is not None:
                        thread.mStacks.append(stack)
                stack = StackInfo()
                stack.mText = line
            elif re.search(r"^Loaded modules", line, flags=re.IGNORECASE):
                # Loaded modules:
                if thread is not None:
                    if stack is not None:
                        thread.mStacks.append(stack)
                        stack = None
                        if stack:
                            pass
                    threads.append(thread)
                    if crashedOnly and thread.isCrashed():
                        return fileInfo, threads
                break
            else:
                if stack is not None:
                    # example: fp = 0x0000007914cfc150    lr = 0x000000798c132808
                    stack.mInfo += line
                    stack.mInfo += os.linesep
                else:
                    # example: Operating system: Android
                    fileInfo += line
                    fileInfo += os.linesep
        Logger.d(appModel.getAppTag(), f"end")
        return fileInfo, threads

    @staticmethod
    def _symbolizeStacks(threads: [ThreadInfo], symbolFolder: str, onStackInfoUpdated) -> bool:
        """
        :param threads: ThreadInfo
        :param symbolFolder: str
        :param onStackInfoUpdated: callback function: void fun(StackInfo)
        :return: bool
        """
        if len(threads) <= 0:
            return False

        Logger.i(appModel.getAppTag(), f"begin")
        # save temp file
        tempAddresses = open(appModel.getTmpFile("dump.addr"), "w")
        for thread in threads:
            for stack in thread.mStacks:
                # example: 5  libc.so + 0x1d4288
                stackValues = StringUtility.splitBySpace(stack.mText)
                # ['5', 'libc.so', '+', '0x1d4288']
                if len(stackValues) < 4:
                    continue
                tempAddresses.write(f"---- \"{stack.mText}\"\n{stackValues[1]} {stackValues[3]}\n")
        tempAddresses.close()

        # symbolizer temp file
        tempAddresses = open(appModel.getTmpFile("dump.addr"), "r")
        symbolizer = appModel.getExtToolsFile("dump", SYMBOLIZER_APP)
        if not os.path.exists(symbolizer) or not os.path.exists(symbolFolder):
            return False
        symbolizerProcess = subprocess.Popen([symbolizer],
                                             cwd=symbolFolder,
                                             stdin=tempAddresses, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = symbolizerProcess.communicate()
        tempAddresses.close()
        os.remove(tempAddresses.name)

        # update symbolizer result
        symbols = stdout.decode("utf-8").split("\n")
        symbolsLineIndex = 0
        for thread in threads:
            for stack in thread.mStacks:
                stack.mSymbol = []
                if symbols[symbolsLineIndex] == f"---- \"{stack.mText}\"":
                    stack.mSymbol.append(symbols[symbolsLineIndex + 1])
                    stack.mSymbol.append(symbols[symbolsLineIndex + 2])
                    symbolsLineIndex += 4
                if onStackInfoUpdated:
                    onStackInfoUpdated(stack)

        Logger.i(appModel.getAppTag(), f"end")
        return True
