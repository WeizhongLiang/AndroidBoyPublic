import os

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QEvent, QSize, QRect, QPoint
from PyQt5.QtGui import QPixmap, QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QWidget

from src.Common import QTHelper, DateTimeHelper
from src.Common.Logger import Logger
from src.Layout.viewPicture import Ui_Form
from src.Model.AppModel import appModel


class ViewPicture(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(ViewPicture, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self.lbPicture.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.mImage = QPixmap()
        self.installEventFilter(self)
        self._mPressPos = QPoint(0, 0)
        self._mScaleRation = 1.0
        self._mRectImage = QRect(0, 0, self.mImage.width(), self.mImage.height())
        # self._mDlgPictureController = DialogPictureController(self)

        self.show()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        return

    def resizeEvent(self, QResizeEvent):
        self._scaleImage()
        return

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        eventType = event.type()
        if eventType == QtCore.QEvent.MouseButtonPress:
            mouse = QMouseEvent(event)
            self._mPressPos = mouse.pos()
        elif eventType == QtCore.QEvent.MouseMove:
            mouse = QMouseEvent(event)
            moveX = mouse.x() - self._mPressPos.x()
            moveY = mouse.y() - self._mPressPos.y()
            Logger.i(appModel.getAppTag(), f"will move: ({moveX},{moveY})")
            # self.scrollArea.scroll(moveX, moveY)
            return False
        elif eventType == QtCore.QEvent.Wheel:
            wheel = QWheelEvent(event)
            numPixels = wheel.pixelDelta()
            numAngles = wheel.angleDelta()
            if numPixels.y() > 0 or numAngles.y() > 0:
                if self._mScaleRation < 4.0:
                    self._mScaleRation += 0.1
            else:
                if self._mScaleRation > 0.2:
                    self._mScaleRation -= 0.1
            self._scaleImage()
            return False
        return super(ViewPicture, self).eventFilter(source, event)

    def openPictureFile(self, path: str):
        Logger.i(appModel.getAppTag(), "")
        self.mImage = QPixmap(path)
        self._mRectImage = QRect(0, 0, self.mImage.width(), self.mImage.height())
        self._scaleImage()
        self.lbPicture.setPixmap(self.mImage)
        return

    def openPictureData(self, data):
        Logger.i(appModel.getAppTag(), "")

        tempDumpPath = appModel.getTmpFile(f"{DateTimeHelper.getNowString('%Y%m%d_%H%M%S')}")
        # save temp file
        tempDump = open(tempDumpPath, "wb")
        tempDump.write(data)
        tempDump.close()
        self.openPictureFile(tempDumpPath)
        # remove temp file
        os.remove(tempDumpPath)
        return

    def setScaleRation(self, ration: float):
        self._mScaleRation = ration
        if self._mScaleRation > 4.0:
            self._mScaleRation = 4.0
        if self._mScaleRation < 0.2:
            self._mScaleRation = 0.2
        self._scaleImage()
        return

    def _scaleImage(self):
        if self._mRectImage.width() == 0 or self._mRectImage.height() == 0:
            return

        rectLabel = self.lbPicture.geometry()
        scaleSize = QSize(rectLabel.width() * self._mScaleRation, rectLabel.height() * self._mScaleRation)
        if rectLabel.width() > rectLabel.height():
            scaleSize.setWidth(self._mRectImage.width() * scaleSize.height() / self._mRectImage.height())
        else:
            scaleSize.setHeight(self._mRectImage.height() * scaleSize.width() / self._mRectImage.width())
        Logger.i(appModel.getAppTag(), f"scale to ({scaleSize.width()},{scaleSize.height()})")
        self.lbPicture.setPixmap(self.mImage.scaled(scaleSize))
        return
