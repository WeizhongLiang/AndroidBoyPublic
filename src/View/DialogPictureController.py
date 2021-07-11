from PyQt5.QtCore import QObject, QEvent, Qt, QPoint
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QDialog

from src.Common import Const, QTHelper
from src.Common.Logger import Logger
from src.Layout.dialogPictureController import Ui_Dialog
from src.Model.AppModel import appModel


class DialogPictureController(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(DialogPictureController, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._mOldPos = self.pos()
        self.sliderZoom.hide()
        self.installEventFilter(self)
        self._bindEvent()
        return

    def mousePressEvent(self, event):
        self._mOldPos = event.globalPos()
        return

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self._mOldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._mOldPos = event.globalPos()
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
        return super(DialogPictureController, self).eventFilter(source, event)

    def _bindEvent(self):
        self.btUp.clicked.connect(self._onUp)
        self.btDown.clicked.connect(self._onDown)
        self.btLeft.clicked.connect(self._onLeft)
        self.btRight.clicked.connect(self._onRight)
        self.btZoom.clicked.connect(self._onZoom)
        return

    def _onUp(self):
        return

    def _onDown(self):
        return

    def _onLeft(self):
        return

    def _onRight(self):
        return

    def _onZoom(self):
        self.sliderZoom.show()
        return
