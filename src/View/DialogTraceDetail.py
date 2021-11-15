import os

import pyperclip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog

from src.Common import Const, JavaMappingHelper
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
        self.btMappingPath.clicked.connect(self.onMappingPath)
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

    def onMappingPath(self):
        title = "Select mapping file"
        startDir = appModel.mAssetsPath
        typeFilter = f"All Files ({Const.mappingFileSuffix})"
        typeFilter += f";;Mapping Files ({Const.mappingFileSuffix})"
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        mappingFile, _ = QFileDialog.getOpenFileName(self,
                                                     caption=title,
                                                     directory=startDir,
                                                     filter=typeFilter,
                                                     options=options)

        if len(mappingFile) == 0:
            return

        self.tbMappingPath.setText(mappingFile)
        message = self.tbMessage.toPlainText()
        if "Uncaught exception!!!" in message:
            message = JavaMappingHelper.translateTrace(mappingFile, message)
            self.tbMessage.setText(message)
        return
