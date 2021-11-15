import time
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5 import QtCore

from src.Common import QTHelper, FileUtility
from src.Common.IntEnum import IntEnum
from src.Common.Logger import Logger
from src.Model.AppModel import appModel
from src.Layout.widgetCCTGOperation import Ui_Form


class TaskState(IntEnum):
    unknown = 0
    error = 1
    notExist = 2
    ready = 3
    running = 4
    stop = 5


class OperationType(IntEnum):
    start = 0
    stop = 1
    delete = 2
    browser = 3


class WidgetCCTGOperation(QWidget, Ui_Form):
    def __init__(self, operationEvent, parent=None):
        super(WidgetCCTGOperation, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)
        self._mEventOperation = operationEvent
        self._ckSelect.setChecked(True)
        self._bindEvent()
        self.setTotalProgress(100)
        self.setCurProgress(0)
        self._mLastProcess = 0
        self._mLastTime = time.time()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        return

    def setState(self, state: TaskState):
        self._btDelete.setEnabled(True)
        self._btBrowser.setEnabled(True)
        if state == TaskState.error:
            self._btStart.setEnabled(True)
            self._btStop.setEnabled(False)
            self._btStart.setVisible(True)
            self._btStop.hide()
            self._lbProgress.setVisible(False)
        elif state == TaskState.notExist:
            self._btStart.setEnabled(True)
            self._btStop.setEnabled(False)
            self._btStart.setVisible(True)
            self._btStop.hide()
            self._pgDownload.setValue(0)
            self._lbProgress.setVisible(False)
        elif state == TaskState.ready:
            self._btStart.setEnabled(False)
            self._btStop.setEnabled(False)
            self._btStart.setVisible(True)
            self._btStop.hide()
            self._lbProgress.setVisible(False)
        elif state == TaskState.running:
            self._btStart.setEnabled(False)
            self._btStop.setEnabled(True)
            self._btStart.hide()
            self._btStop.setVisible(True)
            self._lbProgress.setVisible(True)
        elif state == TaskState.stop:
            self._btStart.setEnabled(True)
            self._btStop.setEnabled(False)
            self._btStart.setVisible(True)
            self._btStop.hide()
            self._lbProgress.setVisible(False)
        return

    def setTotalProgress(self, totalLen: int):
        self._pgDownload.setOrientation(Qt.Horizontal)
        self._pgDownload.setMaximum(totalLen)
        self._mLastProcess = 0
        self._mLastTime = time.time()
        self._lbProgress.setText("0% at 0KB/s")
        return

    def setCurProgress(self, curProgress: int):
        self._pgDownload.setValue(curProgress)
        curTimestamp = time.time()
        timeDiff = curTimestamp - self._mLastTime
        if timeDiff > 1.0:
            percent = (curProgress * 100) / self._pgDownload.maximum()
            speed = FileUtility.fileSizeFmt((curProgress - self._mLastProcess) / timeDiff )
            textProgress = f"{int(percent)}% at {speed}/s"
            self._lbProgress.setText(textProgress)
            self._mLastProcess = curProgress
            self._mLastTime = curTimestamp
        return

    def _bindEvent(self):
        self._btStart.clicked.connect(partial(self._onOperation, self._btStart, OperationType.start))
        self._btStop.clicked.connect(partial(self._onOperation, self._btStop, OperationType.stop))
        self._btDelete.clicked.connect(partial(self._onOperation, self._btDelete, OperationType.delete))
        self._btBrowser.clicked.connect(partial(self._onOperation, self._btBrowser, OperationType.browser))
        return

    def _onOperation(self, button: QPushButton, operation: OperationType):
        Logger.i(appModel.getAppTag(), f"operation = {operation}")
        button.setEnabled(False)
        if self._mEventOperation is not None:
            self._mEventOperation(operation)
        return

    def isChecked(self):
        return self._ckSelect.isChecked()
