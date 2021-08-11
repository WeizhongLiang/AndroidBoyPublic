from PyQt5.QtWidgets import QDialog

from src.Common import QTHelper
from src.Common.Logger import Logger, LoggerLevel
from src.Layout.dialogGlobalFilter import Ui_Dialog

from src.Common.QTHelper import ListForQLineEdit
from src.Model.AppModel import appModel


class DialogGlobalFilter(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(DialogGlobalFilter, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self._initLogLevel()
        self._bindEvent()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        ListForQLineEdit.closeInstance()
        return

    def _initLogLevel(self):
        self.cbLogLevel.addItem("Verbose", LoggerLevel.Verbose)
        self.cbLogLevel.addItem("Debug", LoggerLevel.Debug)
        self.cbLogLevel.addItem("Info", LoggerLevel.Info)
        self.cbLogLevel.addItem("Warning", LoggerLevel.Warning)
        self.cbLogLevel.addItem("Error", LoggerLevel.Error)
        lastSel = appModel.readConfig(self.__class__.__name__, "selLogLevel", "Verbose")
        setSel = self.cbLogLevel.findText(lastSel)
        if setSel >= 0:
            self.cbLogLevel.setCurrentIndex(setSel)
        else:
            self.cbLogLevel.setCurrentIndex(0)
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self.btFilter.clicked.connect(self._onFilterLogcat)
        self.editFilter.textChanged.connect(self._onEditorTextChanged)
        return

    def _onEditorTextChanged(self, newText):
        inputList = appModel.getRecentInputList(newText)
        Logger.i(appModel.getAppTag(), f"newText={newText}, inputList={inputList}")
        ListForQLineEdit.getInstance().showList(inputList, self.editFilter)
        return

    def _onFilterLogcat(self):
        filterMsg = self.editFilter.text()
        appModel.addRecentInput(filterMsg)
        Logger.i(appModel.getAppTag(), f"filter {filterMsg} begin")
        Logger.i(appModel.getAppTag(), f"filter {filterMsg} end")
        return
