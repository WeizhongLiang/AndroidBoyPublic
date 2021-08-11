from typing import cast

from PyQt5.QtCore import QRect, QObject, QEvent, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QDesktopWidget, QWidget, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QTabWidget

from src.Common import SystemHelper
from src.Common.UITheme import uiTheme


def getCenterOf(width, height, parent: QWidget):
    if parent is None:
        parentRect = QDesktopWidget().availableGeometry()
    else:
        parentRect = parent.geometry()

    x = (parentRect.width() - width) / 2
    y = (parentRect.height() - height) / 2
    return QRect(x, y, width, height)


def showLayout(layout, show):
    for i in range(layout.count()):
        child = layout.itemAt(i)
        widget = child.widget()
        if widget is None:
            continue
        if show:
            widget.show()
        else:
            widget.hide()
    return


def enableLayout(layout, enable):
    for i in range(layout.count()):
        child = layout.itemAt(i)
        widget = child.widget()
        if widget is None:
            continue
        if enable:
            widget.setDisabled(False)
        else:
            widget.setDisabled(True)
    return


def switchMacUI(widget: QWidget):
    if not SystemHelper.isMac():
        return
    buttons = widget.findChildren(QPushButton)
    for button in buttons:
        if len(button.text()) == 0:
            if button.isCheckable():
                button.setStyleSheet(uiTheme.styleIconCheckButton)
            else:
                button.setStyleSheet(uiTheme.styleIconButton)
        else:
            button.setStyleSheet(uiTheme.styleTextButton)

    tabs = widget.findChildren(QTabWidget)
    for tab in tabs:
        tab.setStyleSheet(uiTheme.styleTabWidget)
        tab.tabBar().setStyleSheet(uiTheme.styleTabBar)

    # for child in widget.children():
    #     type = child.__class__.__name__
    #     if type == "QPushButton":
    #         pass
    return


class ListForQLineEdit(QListWidget):
    _instance = None

    @staticmethod
    def getInstance():
        # return ListForQLineEdit()
        # single instance may cause crash......
        if ListForQLineEdit._instance is None:
            ListForQLineEdit._instance = ListForQLineEdit()
        return ListForQLineEdit._instance

    @staticmethod
    def closeInstance():
        if ListForQLineEdit._instance is not None:
            ListForQLineEdit._instance.close()
            ListForQLineEdit._instance = None
        return

    def __init__(self, parent: QWidget = None):
        super(ListForQLineEdit, self).__init__(parent)
        self._mEditor = None
        self.itemClicked.connect(self._onSelectItem)
        self.hide()
        return

    def closeEvent(self, event) -> None:
        if self._mEditor is not None:
            self._mEditor.removeEventFilter(self)
            self.removeEventFilter(self)
        return

    def _onSelectItem(self, item: QListWidgetItem):
        if self._mEditor is not None:
            self._mEditor.setText(item.text())
        self.hide()
        return

    def showList(self, texts: [str], editor: QLineEdit, inBottom: bool = True):
        if editor is None:
            self.hide()
            return
        rowCount = len(texts)
        if rowCount == 0:
            self.hide()
            return

        self.clear()
        self.addItems(texts)
        width = self.sizeHintForColumn(0) + 2 * self.frameWidth()
        height = self.sizeHintForRow(0) * self.count() + 2 * self.frameWidth()
        self.setFixedSize(width, height)

        self._mEditor = editor
        self.setParent(cast(QWidget, editor.parent()))
        rectEditor = editor.geometry()
        if inBottom:
            rectEditor.setY(rectEditor.bottom())
        else:
            rectEditor.setY(rectEditor.top()-height)
        self.setGeometry(rectEditor)
        self._mEditor.installEventFilter(self)
        self.installEventFilter(self)

        self.setCurrentRow(0)
        self.show()
        return

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.KeyRelease:
            key = QKeyEvent(event).key()
            # Logger.i(appModel.getAppTag(), f"source={source}, key={key}")
            if source is self:
                if key == Qt.Key_Escape:
                    self.hide()
                    return True
                elif key == Qt.Key_Return:
                    self._mEditor.setText(self.currentItem().text())
                    self.hide()
                    self._mEditor.setFocus()
                    return True
            elif source is self._mEditor:
                if key == Qt.Key_Up:
                    self.setFocus()
                elif key == Qt.Key_Down:
                    self.setFocus()
                elif key == Qt.Key_Return:
                    self.hide()
                elif key == Qt.Key_Escape:
                    self.hide()
        elif event.type() == QEvent.FocusOut:
            if not self.hasFocus() and not self._mEditor.hasFocus():
                self.hide()
        return super(ListForQLineEdit, self).eventFilter(source, event)
