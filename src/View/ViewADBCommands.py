from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, QEvent, QTimer
from PyQt5.QtGui import QKeyEvent, QTextCursor
from PyQt5.QtWidgets import QWidget

from src.Common import QTHelper, SystemHelper
from src.Common.ADBHelper import *
from src.Common.Logger import Logger
from src.Layout.viewADBCommands import Ui_Form

from src.Common.QTHelper import ListForQLineEdit
from src.Common.SystemHelper import CommandProcess
from src.Common.UITheme import uiTheme
from src.Model.AppModel import appModel


# openssl s_client -connect www.google.com:443
# nm -gU something.dylib

class ViewADBCommands(QWidget, Ui_Form):
    _mEventConnectState = QtCore.pyqtSignal(int)
    StateDisconnected = 0
    StateConnected = 1
    StateProcessing = 2
    StateWaiting = 3

    def __init__(self, parent=None):
        super(ViewADBCommands, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self._mTerminalCmd = ["cmd"]
        self._mAutoEcho = ""
        self._mOutputLock = threading.RLock()
        self._mOutputContent = []
        self._mUpdateTimer = QTimer()
        self._mProcessingStart = 0
        self._mRecentCommands = appModel.readConfig(__class__.__name__, "RecentCommands", [])

        self.setupUi(self)
        QTHelper.switchMacUI(self)
        self._bindEvent()
        self._editorOutput.setReadOnly(False)

        self._mSyncMode = False
        self._mADBCommands = CommandProcess("utf-8", self._onInput, self._onOutput, self._onError, self._onExit)
        self._mEventConnectState.emit(ViewADBCommands.StateDisconnected)
        self._onOpen()

        self.show()
        self._mUpdateTimer.start(100)
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        self._mADBCommands.close()
        self._mUpdateTimer.stop()
        ListForQLineEdit.closeInstance()
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self._mEventConnectState.connect(self._onEventConnectState)
        self._mUpdateTimer.timeout.connect(self._onUpdateTimer)
        self._btOpen.clicked.connect(self._onOpen)
        self._btStop.clicked.connect(self._onStop)
        self._btCommit.setDefault(True)
        self._btCommit.clicked.connect(self._onCommit)
        self._btSave.clicked.connect(self._onSave)
        self._btClear.clicked.connect(self._onClear)
        self.installEventFilter(self)
        self._editorCmd.textChanged.connect(self._onEditorTextChanged)
        return

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.KeyRelease:
            key = QKeyEvent(event).key()
            if source is self._editorCmd or source is self:
                if key == Qt.Key_Return:
                    if self._btCommit.isEnabled():
                        self._onCommit()
                        return True
        return super(ViewADBCommands, self).eventFilter(source, event)

    def _onEditorTextChanged(self, newText):
        inputList = appModel.getArrayConfigList(self._mRecentCommands, newText)
        # Logger.i(appModel.getAppTag(), f"newText={newText}, inputList={inputList}")
        ListForQLineEdit.getInstance().showList(inputList, self._editorCmd, inBottom=False)
        return

    def _onEventConnectState(self, state: int):
        if state == ViewADBCommands.StateDisconnected:
            # disconnected
            self._btOpen.show()
            self._btOpen.setFocus()
            self._btOpen.setDefault(True)
            self._btStop.hide()
            self._btCommit.hide()
            self._btCommit.setDisabled(True)
        elif state == ViewADBCommands.StateConnected:
            self._btOpen.hide()
            self._btStop.show()
            self._btCommit.show()
            self._btCommit.setDefault(True)
            self._btCommit.setDisabled(False)
            self._editorCmd.setFocus(True)
        elif state == ViewADBCommands.StateProcessing:
            self._mProcessingStart = datetime.now().timestamp()
            self._btCommit.setDisabled(True)
        elif state == ViewADBCommands.StateWaiting:
            self._mProcessingStart = 0
            self._btCommit.setDisabled(False)
        else:
            Logger.w(appModel.getAppTag(), f"Unknown state:{state}")
        return

    def _onOpen(self):
        self._editorCmd.clear()
        self._onClear()

        if SystemHelper.isWindows():
            self._mTerminalCmd = ["cmd"]
            self._mAutoEcho = ""
            self._mTerminalCmd = ["adb", "shell"]
            self._mAutoEcho = ""
        else:
            self._mTerminalCmd = ["adb logcat"]
            self._mAutoEcho = os.linesep + "equuleus:/ $"
            self._mTerminalCmd = ["/bin/sh"]
            self._mAutoEcho = os.linesep + ""

        if self._mADBCommands.open(self._mSyncMode, self._mTerminalCmd):
            self._mOutputLock.acquire()
            self._mOutputContent.append([uiTheme.cmdTipsColor, self._mAutoEcho])
            self._mOutputLock.release()
            self._mEventConnectState.emit(ViewADBCommands.StateConnected)
        else:
            self._mEventConnectState.emit(ViewADBCommands.StateDisconnected)
        return

    def _onStop(self):
        self._mADBCommands.inputCtrlCEvent()
        return

    def _onCommit(self):
        inputText = self._editorCmd.text()
        cmd = bytes(inputText + os.linesep, self._mADBCommands.getEncoding())
        if self._mSyncMode:
            self._mEventConnectState.emit(ViewADBCommands.StateProcessing)
            self._mADBCommands.getCommandResult(cmd)
        else:
            if not self._mADBCommands.inputCommand(cmd):
                self._mADBCommands.inputCommand(cmd)
        self._editorCmd.selectAll()
        appModel.addArrayConfig(__class__.__name__, "RecentCommands",
                                self._mRecentCommands, inputText)
        return

    def _onSave(self):
        # Logger.i(appModel.getAppTag(), f"{self}")
        self._editorOutput.clear()
        return

    def _onClear(self):
        # Logger.i(appModel.getAppTag(), f"{self}")
        self._editorOutput.clear()
        return

    def _onUpdateTimer(self):
        self._mOutputLock.acquire()
        if len(self._mOutputContent) > 0:
            Logger.d(appModel.getAppTag(), "begin")
            for color, content in self._mOutputContent:
                self._editorOutput.moveCursor(QTextCursor.End)
                self._editorOutput.setTextColor(color)
                self._editorOutput.insertPlainText(content)
            scrollBar = self._editorOutput.verticalScrollBar()
            scrollBar.setValue(scrollBar.maximum())
            self._mOutputContent.clear()
            Logger.d(appModel.getAppTag(), "end")
        self._mOutputLock.release()

        begin = self._mProcessingStart
        cur = datetime.now().timestamp()
        if begin != 0 and cur - begin > 5.0:
            Logger.w(appModel.getAppTag(), "wake up processing state.")
            self._mEventConnectState.emit(ViewADBCommands.StateWaiting)
        return

    def _onInput(self, cmd: str):
        Logger.d(appModel.getAppTag(), "begin")
        self._mEventConnectState.emit(ViewADBCommands.StateProcessing)
        self._mOutputLock.acquire()
        self._mOutputContent.append([uiTheme.cmdInputColor, cmd])
        self._mOutputLock.release()
        Logger.d(appModel.getAppTag(), "end")
        return

    def _onOutput(self, out: str):
        Logger.d(appModel.getAppTag(), "begin")
        self._mOutputLock.acquire()
        self._mOutputContent.append([uiTheme.cmdOutputColor, out])
        self._mOutputContent.append([uiTheme.cmdTipsColor, self._mAutoEcho])
        self._mOutputLock.release()
        self._mEventConnectState.emit(ViewADBCommands.StateWaiting)
        Logger.d(appModel.getAppTag(), "end")
        return

    def _onError(self, error: str):
        Logger.d(appModel.getAppTag(), "begin")
        self._mOutputLock.acquire()
        self._mOutputContent.append([uiTheme.cmdErrorColor, error])
        self._mOutputContent.append([uiTheme.cmdTipsColor, self._mAutoEcho])
        self._mOutputLock.release()
        self._mEventConnectState.emit(ViewADBCommands.StateWaiting)
        Logger.d(appModel.getAppTag(), "end")
        return

    def _onExit(self):
        Logger.w(appModel.getAppTag(), "begin")
        self._mOutputLock.acquire()
        self._mOutputContent.append([uiTheme.cmdErrorColor, f"{os.linesep}Conversation has terminated.{os.linesep}"])
        self._mOutputLock.release()
        self._mEventConnectState.emit(ViewADBCommands.StateDisconnected)
        Logger.w(appModel.getAppTag(), "end")
        return
