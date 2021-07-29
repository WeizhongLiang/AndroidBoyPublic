import os

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QEvent, QSize, QRect, QPoint
from PyQt5.QtGui import QPixmap, QMouseEvent, QWheelEvent, QPalette, QCursor, QTransform, QContextMenuEvent
from PyQt5.QtWidgets import QWidget, QMenu

from src.Common import QTHelper, DateTimeHelper
from src.Common.Logger import Logger
from src.Layout.viewPicture import Ui_Form

from src.Common.UITheme import uiTheme
from src.Model.AppModel import appModel


_maxRation = 2.0
_minRation = 0.2


class ViewPicture(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(ViewPicture, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self.saPicture.setBackgroundRole(QPalette.Dark)
        self.saPicture.setVisible(True)
        self.saPicture.setWidget(self.lbPicture)
        self.saPicture.setWidgetResizable(True)
        self._mScrollVertical = self.saPicture.verticalScrollBar()
        self._mScrollHorizontal = self.saPicture.horizontalScrollBar()
        self.lbPicture.installEventFilter(self)

        self.mImage = QPixmap()
        self._mPressPos = QPoint(0, 0)
        self._mScaleRation = 1.0
        self._mOffsetPoint = QPoint(0, 0)
        self._mRectLabel = self.lbPicture.geometry()
        self._mRectImage = QRect(0, 0, self.mImage.width(), self.mImage.height())
        self._mScaledSize = QSize(self._mRectImage.width(), self._mRectImage.height())
        # self._mDlgPictureController = DialogPictureController(self)

        self.show()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        return

    def resizeEvent(self, QResizeEvent):
        self._mRectLabel = self.lbPicture.geometry()
        self._updateImagePos()
        return

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if source != self.lbPicture:
            Logger.i(appModel.getAppTag(), f"source={source}")
            return super(ViewPicture, self).eventFilter(source, event)
        eventType = event.type()
        if eventType == QtCore.QEvent.MouseButtonPress:
            mouse = QMouseEvent(event)
            self._mPressPos = mouse.pos()
            self.setCursor(QCursor(QtCore.Qt.OpenHandCursor))
            return True
        if eventType == QtCore.QEvent.MouseButtonRelease:
            self._mPressPos = QPoint(0, 0)
            self.setCursor(QCursor(QtCore.Qt.ArrowCursor))
            return True
        elif eventType == QtCore.QEvent.MouseMove:
            mouse = QMouseEvent(event)
            self.setOffset(mouse.x() - self._mPressPos.x(), mouse.y() - self._mPressPos.y())
            return True
        elif eventType == QtCore.QEvent.Wheel:
            wheel = QWheelEvent(event)
            numPixels = wheel.pixelDelta()
            numAngles = wheel.angleDelta()
            if numPixels.y() > 0 or numAngles.y() > 0:
                self.setScaleRation(self._mScaleRation + 0.1)
            else:
                self.setScaleRation(self._mScaleRation - 0.1)
            return True
        return super(ViewPicture, self).eventFilter(source, event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        rotateClockwise = menu.addAction(uiTheme.iconRotateClockwise, "Clockwise rotate")
        rotateAnticlockwise = menu.addAction(uiTheme.iconRotateAnticlockwise, "Anticlockwise rotate")
        menu.addSeparator()
        zoomIn = menu.addAction(uiTheme.iconZoomIn, "Zoom in")
        zoomOut = menu.addAction(uiTheme.iconZoomOut, "Zoom out")
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is None:
            return
        elif action == rotateClockwise:
            self.setRotation(90)
        elif action == rotateAnticlockwise:
            self.setRotation(-90)
        elif action == zoomIn:
            self.setScaleRation(self._mScaleRation + 0.1)
        elif action == zoomOut:
            self.setScaleRation(self._mScaleRation - 0.1)
        return

    def openPictureFile(self, path: str):
        Logger.i(appModel.getAppTag(), "")
        self.mImage = QPixmap(path)
        self._mRectImage = QRect(0, 0, self.mImage.width(), self.mImage.height())
        self._updateImagePos()
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

    def setRotation(self, rotation: int):
        transform = QTransform()
        trans = transform.rotate(rotation)
        self.mImage = self.mImage.transformed(trans)
        self._mRectImage = QRect(0, 0, self.mImage.width(), self.mImage.height())
        self._updateImagePos()
        return

    def setOffset(self, deltaX: int, deltaY: int):
        newX = self._mOffsetPoint.x() - deltaX
        newY = self._mOffsetPoint.y() - deltaY
        if newX > self._mScaledSize.width():
            newX = self._mScaledSize.width()
        if newX < 0:
            newX = 0
        if newY > self._mScaledSize.height():
            newY = self._mScaledSize.height()
        if newY < 0:
            newY = 0
        self._mOffsetPoint.setX(newX)
        self._mOffsetPoint.setY(newY)
        # Logger.i(appModel.getAppTag(),
        #         f"self._mOffsetPoint=({self._mOffsetPoint.x()}, {self._mOffsetPoint.y()})")
        self._mScrollHorizontal.setValue(self._mOffsetPoint.x())
        self._mScrollVertical.setValue(self._mOffsetPoint.y())
        return

    def setScaleRation(self, ration: float):
        # Logger.i(appModel.getAppTag(), f"ration = {ration}")
        if ration > _maxRation:
            ration = _maxRation
        if ration < _minRation:
            ration = _minRation
        if self._mScaleRation != ration:
            self._mScaleRation = ration
            self._updateImagePos()
        return

    def _updateImagePos(self):
        if self._mRectImage.width() == 0 or self._mRectImage.height() == 0:
            return

        self._mScaledSize = QSize(self._mRectLabel.width() * self._mScaleRation,
                                  self._mRectLabel.height() * self._mScaleRation)
        if self._mRectLabel.width() > self._mRectLabel.height():
            self._mScaledSize.setWidth(
                self._mRectImage.width() * self._mScaledSize.height() / self._mRectImage.height())
        else:
            self._mScaledSize.setHeight(
                self._mRectImage.height() * self._mScaledSize.width() / self._mRectImage.width())
        # Logger.i(appModel.getAppTag(), f"scale=({self._mScaledSize.width()}, {self._mScaledSize.height()})"
        #                                f"@{self._mScaleRation:.1f}, "
        #                                f"offset=({self._mScrollHorizontal.value()}, {self._mScrollVertical.value()})")
        self.lbPicture.setPixmap(self.mImage.scaled(self._mScaledSize))
        self._mOffsetPoint.setX(self._mScrollHorizontal.value())
        self._mOffsetPoint.setY(self._mScrollVertical.value())
        return
