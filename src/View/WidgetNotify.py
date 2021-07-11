from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QCursor, QColor, QFontMetrics
from PyQt5.QtWidgets import QWidget

from src.Common.Logger import Logger
from src.Model.AppModel import appModel

from src.Layout.widgetNotify import Ui_Form


class WidgetNotify(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(WidgetNotify, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._onTimer)

        pal = self.tbNotify.palette()
        pal.setColor(pal.Base, QColor(255, 255, 220))
        pal.setColor(pal.Text, QColor(0, 0, 0))
        self.tbNotify.setPalette(pal)
        self.tbNotify.setFontPointSize(15)
        self._fontMetrics = QFontMetrics(self.tbNotify.currentFont())

        return

    def notify(self, text, seconds):
        pos = self.parent().mapFromGlobal(QCursor.pos())
        rectText = self._fontMetrics.boundingRect(text)
        Logger.i(appModel.getAppTag(), f"({pos.x()},{pos.y()},{rectText.width()},{rectText.height()}): {text}")
        self.tbNotify.setText(text)
        self._timer.start(1000 * seconds)
        rectText = self._fontMetrics.boundingRect(text)
        self.setGeometry(pos.x(), pos.y(), rectText.width()*1.1, rectText.height()*1.8)
        self.tbNotify.setGeometry(0, 0, rectText.width()*1.1, rectText.height()*1.8)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        # self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.show()
        return

    def _onTimer(self):
        Logger.i(appModel.getAppTag(), "")
        self._timer.stop()
        self.close()
        return
