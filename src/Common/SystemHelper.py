import io
import signal
import subprocess
import sys
import threading
import time

import psutil
import os

from src.Common.Logger import Logger

# AIX               'aix'
# Linux             'linux'
# Windows           'win32'
# Windows/Cygwin    'cygwin'
# macOS             'darwin'


def isAIXc():
    return sys.platform == "aix"


def isLinux():
    return sys.platform == "linux"


def isWindows():
    return sys.platform == "win32"


def isCygwin():
    return sys.platform == "cygwin"


def isMac():
    return sys.platform == "darwin"


def desktopPath():
    if isWindows():
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    else:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')


def openAtExplorer(path: str):
    if isWindows():
        while not os.path.exists(path):
            path = os.path.dirname(path)
            if len(path) == 0:
                return
        subprocess.call(["explorer.exe", "/select,", f"{path}"])
    elif isMac():
        subprocess.call(["open", "-R", path])
    elif isLinux():
        subprocess.call(["xdg-open", path])
    return


class SelfProcessInfo:
    _instance = None

    def __init__(self):
        self._recentCPU = []
        self._mProcess = psutil.Process(os.getpid())
        return

    def getCPU(self, interval=None):
        self._recentCPU.append(self._mProcess.cpu_percent(interval))
        if len(self._recentCPU) > 5:
            self._recentCPU.pop(0)
        totalValue = 0
        for value in self._recentCPU:
            totalValue += value
        value = totalValue / len(self._recentCPU)
        return value

    def getMemory(self):
        mem_process = self._mProcess.memory_info().rss
        return round(mem_process / 1024 / 1024, 2)

    @staticmethod
    def _getInstance():
        if SelfProcessInfo._instance is None:
            SelfProcessInfo._instance = SelfProcessInfo()
        return SelfProcessInfo._instance

    @staticmethod
    def getSelfCPU(interval=None):
        return SelfProcessInfo._getInstance().getCPU(interval)

    @staticmethod
    def getSelfMemory():
        return SelfProcessInfo._getInstance().getMemory()


class CommandProcess:
    class PipeIO:
        def __init__(self, path):
            from src.Model.AppModel import appModel
            self._mValid = False
            self._mFile = None  # : io.TextIOWrapper
            try:
                self._mFile = open(path, "w+b")
            except FileExistsError as e:
                Logger.e(appModel.getAppTag(), f"Create PipeIO {path} failed: {e}")

            self._mCurReadPos = 0
            self._mValid = self._mFile is not None
            return

        def __del__(self):
            self.close()
            return

        def isValid(self) -> bool:
            return self._mValid

        def getFileIO(self):
            return self._mFile

        def newInputSize(self) -> int:
            if not self.isValid():
                return 0
            return self._mFile.tell() - self._mCurReadPos

        def read(self, maxSize=-1) -> bytes:
            newSize = self.newInputSize()
            if newSize <= 0:
                return b""
            self._mFile.seek(-newSize, io.SEEK_END)
            if 0 < maxSize < newSize:
                newSize = maxSize
            readBuf = self._mFile.read(newSize)
            self._mCurReadPos += newSize
            self._mFile.seek(0, io.SEEK_END)
            return readBuf

        def write(self, content: bytes):
            if not self.isValid():
                return -1
            self._mFile.write(content)
            return len(content)

        def close(self, deleteFile=True):
            if not self.isValid():
                return
            self._mFile.close()
            if deleteFile:
                os.remove(self._mFile.name)
            self._mFile = None
            self._mValid = False
            return

    def __init__(self, encoding="utf-8", onInput=None, onOutput=None, onError=None, onExit=None):
        from src.Model.AppModel import appModel
        self._mEncoding = encoding
        self._mCurrentInput = ""
        self._mCurrentOutput = ""
        self._mCurrentError = ""
        self._mOnInput = onInput
        self._mOnOutput = onOutput
        self._mOnError = onError
        self._mOnExit = onExit
        self._mSubProcess = None
        self._mThreadIOs = None

        self._mOutputIO = CommandProcess.PipeIO(appModel.getTmpFile(f"{self.__hash__()}_OutputIO.tmp"))
        self._mErrorIO = CommandProcess.PipeIO(appModel.getTmpFile(f"{self.__hash__()}_ErrorIO.tmp"))
        return

    def open(self, syncMode: bool, cmd: []):
        from src.Model.AppModel import appModel
        if self._isRunning():
            return False

        cmdContent = ""
        for param in cmd:
            cmdContent += param + " "
        try:
            self._mSubProcess = subprocess.Popen(cmd,
                                                 stdin=subprocess.PIPE,
                                                 stdout=self._mOutputIO.getFileIO(),
                                                 stderr=self._mErrorIO.getFileIO(),
                                                 shell=False)
            if syncMode:
                self._mThreadIOs = None
                self._processIOs("")
            else:
                self._mThreadIOs = threading.Thread(target=self._onIOsThread)
                self._mThreadIOs.start()
        except BaseException as e:
            errorStr = f"open [{cmdContent}] failed: {e}"
            Logger.e(appModel.getAppTag(), errorStr)
            self._mErrorIO.write(bytes(errorStr, self._mEncoding))
            self._processIOs("")
            return False
        return True

    def close(self):
        from src.Model.AppModel import appModel
        Logger.i(appModel.getAppTag(), "")
        if self._mSubProcess is not None:
            Logger.i(appModel.getAppTag(), "kill command process")
            self._mSubProcess.kill()
            while self._isRunning():
                time.sleep(0.001)
        thread = self._mThreadIOs
        self._mThreadIOs = None
        if thread is not None:
            if thread.is_alive():
                Logger.i(appModel.getAppTag(), "join prev thread")
                thread.join()
        self._mOutputIO.close()
        self._mErrorIO.close()
        return

    def _isRunning(self):
        if self._mSubProcess and self._mSubProcess.poll() is None:
            return True
        return False

    def _onIOsThread(self):
        from src.Model.AppModel import appModel
        while self._isRunning():
            self._processIOs(self._mCurrentInput)
            time.sleep(0.2)

        # check if there are error and output
        while self._processIOs(self._mCurrentInput) > 0:
            time.sleep(0.01)

        if self._mOnExit:
            self._mOnExit()
        Logger.i(appModel.getAppTag(), f"end")
        return

    def _processIOs(self, cmd) -> int:
        """ return read count """

        self._mCurrentError = self._mErrorIO.read(102400).decode(self._mEncoding)
        if len(self._mCurrentError) > 0 and self._mOnError:
            self._mOnError(self._mCurrentError)

        outputContent = self._mOutputIO.read(102400).decode(self._mEncoding)
        if outputContent.find(cmd, 0) == 0:
            self._mCurrentOutput = outputContent[len(cmd):]
        else:
            self._mCurrentOutput = outputContent
        if len(self._mCurrentOutput) > 0 and self._mOnOutput:
            self._mOnOutput(self._mCurrentOutput)
        return len(self._mCurrentError) + len(self._mCurrentOutput)

    def getEncoding(self):
        return self._mEncoding

    def getLastOutput(self):
        return self._mCurrentInput, self._mCurrentOutput, self._mCurrentError

    def getCommandResult(self, cmd) -> bool:
        """
        use for sync mode
        return read count
        """
        if not self._isRunning():
            return False

        self.inputCommand(cmd)
        return self._processIOs(cmd.decode(self._mEncoding)) > 0

    def processIOs(self):
        """
        use for sync mode
        return read count
        """
        if not self._isRunning():
            return False
        return self._processIOs("") > 0

    def inputCommand(self, cmd):
        if len(cmd) <= 0:
            return False
        if not self._isRunning():
            return False

        self._mCurrentInput = cmd.decode(self._mEncoding)
        if self._mOnInput:
            self._mOnInput(self._mCurrentInput)
        self._mSubProcess.stdin.write(cmd)
        self._mSubProcess.stdin.flush()
        return True

    def inputCtrlCEvent(self):
        if not self._isRunning():
            return False
        self._mSubProcess.send_signal(signal.SIGINT)
        while self._isRunning():
            time.sleep(0.001)
        self._mOutputIO.close()
        self._mErrorIO.close()
        return True
