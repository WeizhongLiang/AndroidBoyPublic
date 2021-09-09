from PyQt5.QtWidgets import QWidget, QFileDialog

from src.Common import JavaMappingHelper, NativeTraceParseHelper
from src.Common.Logger import Logger
from src.Model.AppModel import appModel
from src.Layout.traceParser import Ui_Form

SELECT_DIR_JAVA = "parserSelectDirJava"
SELECT_DIR_NATIVE = "parserSelectDirNative"
SELECT_DIR_TYPE = "parserSelectType"


class ViewTraceParser(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(ViewTraceParser, self).__init__(parent)
        self.setupUi(self)

        self.pushButton_parse.clicked.connect(self.onParseBtnClicked)
        self.pushButton_browser.clicked.connect(self.onBrowserBtnClicked)
        self.lineEdit_path.returnPressed.connect(self.onParseBtnClicked)

        self.TAG = 'ViewTraceParser'

        self.comboBox_type.insertItem(0, 'Native trace Parse')
        self.comboBox_type.insertItem(1, 'Java trace Parse')
        self.comboBox_type.currentIndexChanged.connect(self.onTypeChanged)

        index = appModel.readConfig(self.__class__.__name__, SELECT_DIR_TYPE, 0)
        self.comboBox_type.setCurrentIndex(index)
        self._initComboBoxType(index)

    def onParseBtnClicked(self):
        Logger.i(self.TAG, 'onParseBtnClicked')
        trace = self.plainTextEdit_trace.toPlainText()
        index = self.comboBox_type.currentIndex()
        path = self.lineEdit_path.text()
        if index == 1:
            result = JavaMappingHelper.translateTrace2(path, trace)
            self.textBrowser_result.setText(result)
        elif index == 0:
            result = NativeTraceParseHelper.translateTrace(path, trace)
            self.textBrowser_result.setText(result)

    def _selectNativeSymbolPath(self):
        startDir = self.__loadDirOrFilePath(0)
        folder = QFileDialog.getExistingDirectory(self, directory=startDir)
        if folder != '':
            appModel.saveConfig(self.__class__.__name__, SELECT_DIR_NATIVE, folder)
            self.lineEdit_path.setText(folder)

    def _selectMappingFile(self):
        startDir = self.__loadDirOrFilePath(1)
        path, ok = QFileDialog().getOpenFileName(self, 'Open', directory=startDir)
        if path != '':
            self.lineEdit_path.setText(path)
            appModel.saveConfig(self.__class__.__name__, SELECT_DIR_JAVA, path)

    def onBrowserBtnClicked(self):
        if self.comboBox_type.currentIndex() == 0:
            self._selectNativeSymbolPath()
        else:
            self._selectMappingFile()

    def __loadDirOrFilePath(self, fileType):
        if fileType == 0:
            startDir = appModel.readConfig(self.__class__.__name__, SELECT_DIR_NATIVE, "")
        elif fileType == 1:
            startDir = appModel.readConfig(self.__class__.__name__, SELECT_DIR_JAVA, "")
        else:
            startDir = appModel.readConfig(self.__class__.__name__, SELECT_DIR_NATIVE, "")
        return startDir

    def _initComboBoxType(self, index):
        startDir = self.__loadDirOrFilePath(index)
        self.lineEdit_path.setText(startDir)

    def onTypeChanged(self, index):
        self._initComboBoxType(index)
        appModel.saveConfig(self.__class__.__name__, SELECT_DIR_TYPE, index)
