from typing import Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLineEdit
from src.Layout.dialogLogin import Ui_Dialog

from src.Common import Const, QTHelper
from src.Model.AppModel import appModel


class DialogLogin(QDialog, Ui_Dialog):
    def __init__(self, parent, title: str):
        super(DialogLogin, self).__init__(parent)
        self.setupUi(self)
        QTHelper.switchMacUI(self)
        self._mTitle = title
        self.setWindowTitle(self._mTitle)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setModal(True)
        self.editorPassword.setEchoMode(QLineEdit.Password)
        self._bindEvent()

        userInfo = appModel.readConfig(self.__class__.__name__, self._mTitle, ["", "", True])
        self.editorUserName.setText(userInfo[0])
        self.editorPassword.setText(userInfo[1])
        self.ckSave.setChecked(userInfo[2])
        return

    def _bindEvent(self):
        self.btOK.clicked.connect(self._onOK)
        self.btCancel.clicked.connect(self._onCancel)
        return

    def _onOK(self):
        self.done(Const.EXIT_OK)
        userInfo = [self.editorUserName.text(), ""]
        if self.ckSave.isChecked():
            userInfo.append(True)
        else:
            userInfo.append(False)
        appModel.saveConfig(self.__class__.__name__, self._mTitle, userInfo)
        return

    def _onCancel(self):
        self.done(Const.EXIT_CANCEL)
        return

    def getLoginInfo(self) -> Tuple[str, str]:
        return self.editorUserName.text(), self.editorPassword.text()
