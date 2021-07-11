from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtGui import QIntValidator, QKeyEvent
from PyQt5.QtWidgets import QDialog

from src.Common import Const
from src.Common.Logger import Logger
from src.Layout.dialogScrollTo import Ui_Dialog
from src.Model.AppModel import appModel


class DialogScrollTo(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(DialogScrollTo, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        self.installEventFilter(self)
        return

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.KeyRelease:
            key = QKeyEvent(event).key()
            if source is self:
                if key == Qt.Key_Return:
                    self.done(Const.EXIT_OK)
                    return True
                if key == Qt.Key_Escape:
                    self.done(Const.EXIT_CANCEL)
                    return True
        return super(DialogScrollTo, self).eventFilter(source, event)

    def setRange(self, start, end):
        start += 1
        end += 1
        self._lbRange.setText(f"({start} ~ {end})")
        self._editorRow.setValidator(QIntValidator(start, end, self._editorRow))
        return

    def setDefaultRow(self, row):
        self._editorRow.setText(f"{row}")
        return

    def getInputRow(self):
        try:
            return int(self._editorRow.text()) - 1
        except ValueError:
            return -1
