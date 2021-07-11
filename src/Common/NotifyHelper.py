from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMessageBox


# check color reference:
# https://doc.qt.io/qt-5/qml-color.html#svg-color-reference
# https://doc.qt.io/qt-5/stylesheet-reference.html
class TimerMessageBox(QMessageBox):
    def __init__(self, title, message, seconds=3, parent=None):
        super(TimerMessageBox, self).__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setStandardButtons(QMessageBox.NoButton)
        self.setStyleSheet("background-color: khaki;font: bold;font-size: 12px")
        # self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.timer = QTimer(self)
        self.timer.start(1000 * seconds)
        self.timer.timeout.connect(self._onTimer)
        pos = QPoint(QCursor.pos().x(), QCursor.pos().y())
        self.move(pos)

        self.show()

    def _onTimer(self):
        self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
