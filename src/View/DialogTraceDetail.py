import os

import pyperclip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from src.Common import Const
from src.Common.Logger import Logger
from src.Layout.dialogTraceDetail import Ui_Dialog
from src.Model.AppModel import appModel


class DialogTraceDetail(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(DialogTraceDetail, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)

        self.btOK.clicked.connect(lambda: self.done(Const.EXIT_OK))
        self.btCopy.clicked.connect(self.onCopy)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        return

    def setTrace(self, timeStr: str, pid: str, tid: str,
                 level: str, tag: str, message: str):
        allMessage = f"Time: {timeStr}{os.linesep}"
        allMessage += f"PID: {pid}{os.linesep}"
        allMessage += f"TID: {tid}{os.linesep}"
        allMessage += f"Level: {level}{os.linesep}"
        allMessage += f"Tag: {tag}{os.linesep}"
        allMessage += f"{os.linesep}{message}"
        self.tbMessage.setText(allMessage)
        return

    def onCopy(self):
        message = self.tbMessage.toPlainText()
        pyperclip.copy(message)
        return
