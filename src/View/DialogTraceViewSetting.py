from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from src.Common import Const
from src.Common.Logger import Logger
from src.Layout.dialogTraceViewSetting import Ui_Dialog
from src.Model.AppModel import appModel


class DialogTraceViewSetting(QDialog, Ui_Dialog):
    def __init__(self, parent, check_index, check_time, check_pid, check_tid, check_level, check_tag):
        super(DialogTraceViewSetting, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)

        self.ckShowIndex.setChecked(check_index)
        self.ckShowTime.setChecked(check_time)
        self.ckShowPID.setChecked(check_pid)
        self.ckShowTID.setChecked(check_tid)
        self.ckShowLevel.setChecked(check_level)
        self.ckShowTag.setChecked(check_tag)

        self.ckShowIndex.stateChanged.connect(self._onCheck)
        self.ckShowTime.stateChanged.connect(self._onCheck)
        self.ckShowPID.stateChanged.connect(self._onCheck)
        self.ckShowTID.stateChanged.connect(self._onCheck)
        self.ckShowLevel.stateChanged.connect(self._onCheck)
        self.ckShowTag.stateChanged.connect(self._onCheck)
        self._onCheck()

        self.btOK.clicked.connect(lambda: self.done(Const.EXIT_OK))
        self.btCancel.clicked.connect(lambda: self.done(Const.EXIT_CANCEL))
        self.setModal(True)
        return

    def showIndex(self):
        return self.ckShowIndex.isChecked()

    def showTime(self):
        return self.ckShowTime.isChecked()

    def showPID(self):
        return self.ckShowPID.isChecked()

    def showTID(self):
        return self.ckShowTID.isChecked()

    def showLevel(self):
        return self.ckShowLevel.isChecked()

    def showTag(self):
        return self.ckShowTag.isChecked()

    def _onCheck(self):
        labelText = ""
        if self.ckShowIndex.isChecked():
            labelText += "12345"
        if self.ckShowTime.isChecked():
            labelText += " 2020-04-30 14:58:53.366"
        if self.ckShowPID.isChecked():
            labelText += "  1038"
        if self.ckShowTID.isChecked():
            labelText += "  1339"
        if self.ckShowLevel.isChecked():
            labelText += " Info"
        if self.ckShowTag.isChecked():
            labelText += " tag"
        if len(labelText) == 0:
            labelText += "I'm a sample"
        else:
            labelText += ": I'm a sample"
        self.lbSample.setText(labelText)
        return
