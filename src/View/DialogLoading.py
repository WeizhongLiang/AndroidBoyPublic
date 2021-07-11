from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from src.Layout.dialogLoading import Ui_Dialog
from src.Common.UITheme import uiTheme


class DialogLoading(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(DialogLoading, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)

        self.lbAnimation.setMovie(uiTheme.gifLoading)
        uiTheme.gifLoading.start()

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_PaintOnScreen)
        self.setModal(True)
        return

