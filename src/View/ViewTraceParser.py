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

        self.TAG = 'ViewTraceParser'

        self.comboBox_type.insertItem(0, 'Native Trace Parser')
        self.comboBox_type.insertItem(1, 'Java Trace Parser')
        self.comboBox_type.currentIndexChanged.connect(self.onTypeChanged)

        index = appModel.readConfig(self.__class__.__name__, SELECT_DIR_TYPE, 0)
        self.comboBox_type.setCurrentIndex(index)

        self.comboBox_paths.setMaxCount(20)
        self._initComboBoxType(index)

    def onParseBtnClicked(self):
        Logger.i(self.TAG, 'onParseBtnClicked')
        trace = self.plainTextEdit_trace.toPlainText()
        index = self.comboBox_type.currentIndex()
        path = self.comboBox_paths.currentText()
        if path == '':
            return

        if index == 1:
            result = JavaMappingHelper.translateTrace2(path, trace)
            self.textBrowser_result.setText(result)
        elif index == 0:
            result = NativeTraceParseHelper.translateTrace(path, trace)
            self.textBrowser_result.setText(result)

        item0Txt = self.comboBox_paths.itemText(0)
        self.comboBox_paths.setItemText(0, path)
        self.comboBox_paths.setItemText(self.comboBox_paths.currentIndex(), item0Txt)
        self.comboBox_paths.setCurrentIndex(0)
        self._savePath(index, path)

    def _selectNativeSymbolPath(self):
        pathList = self.__loadDirOrFilePath(0)
        startDir = ''
        if len(pathList) > 0:
            startDir = pathList[0]
        folder = QFileDialog.getExistingDirectory(self, directory=startDir)
        if folder != '':
            self._addPaths(0, folder)

    def _addPaths(self, type, path):
        index = self.comboBox_paths.findText(path)
        if -1 == index:
            self.comboBox_paths.insertItem(0, path)
            self.comboBox_paths.setCurrentIndex(0)
        else:
            self.comboBox_paths.setCurrentIndex(index)
        self._savePath(type, path)

    def _savePath(self, type, path):
        allItems = ''
        for i in range(self.comboBox_paths.count()):
            text = self.comboBox_paths.itemText(i)
            if text != '':
                allItems += text + ';;'
        if type == 0:
            appModel.saveConfig(self.__class__.__name__, SELECT_DIR_NATIVE, allItems)
        elif type == 1:
            appModel.saveConfig(self.__class__.__name__, SELECT_DIR_JAVA, allItems)
        else:
            appModel.saveConfig(self.__class__.__name__, SELECT_DIR_JAVA, allItems)


    def _selectMappingFile(self):
        pathList = self.__loadDirOrFilePath(1)
        startDir = ''
        if len(pathList) > 0:
            startDir = pathList[0]
        path, ok = QFileDialog().getOpenFileName(self, 'Open', directory=startDir)
        if path != '':
            self._addPaths(1, path)

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
        dirList = startDir.split(';;')
        targetList = []
        for i in dirList:
            if i != '':
                targetList.append(i)
        return targetList

    def _initComboBoxType(self, index):
        startDir = self.__loadDirOrFilePath(index)
        self.comboBox_paths.addItems(startDir)

    def onTypeChanged(self, index):
        self.comboBox_paths.clear()
        self._initComboBoxType(index)
