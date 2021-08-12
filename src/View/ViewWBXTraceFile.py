from PyQt5.QtWidgets import QWidget

from src.Common import QTHelper
from src.Common.ADBHelper import *
from src.Common.LogcatFile import LogcatFile, LogcatItem
from src.Common.Logger import Logger, LoggerLevel
from src.Common.QTHelper import ListForQLineEdit
from src.Common.WBXTracerHelper import WBXTracerFile, WBXTraceItemV3
from src.Layout.viewWBXTraceFile import Ui_Form
from src.Model.AppModel import appModel
from src.View.DialogTraceViewSetting import DialogTraceViewSetting
from src.View.WidgetTracerList import WidgetTracerList


class ViewWBXTraceFile(QWidget, Ui_Form):
    getWBXTraceLevel = {
        1: LoggerLevel.Debug,
        2: LoggerLevel.Info,
        4: LoggerLevel.Warning,
        8: LoggerLevel.Error,
    }
    DATA_NONE = 0
    DATA_WBT = 1
    DATA_LGF = 2

    def __init__(self, parent=None):
        super(ViewWBXTraceFile, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self._mTraceDataType = self.DATA_NONE
        self._mWBXTracerFile = None
        self._mLGFTracerFile = LogcatFile()
        self._mTracerWidget = WidgetTracerList(self, __class__.__name__, False)
        self.layoutTracer.addWidget(self._mTracerWidget)
        self._bindEvent()
        self._initLogLevel()
        self._mReadTracesThread = threading.Thread(target=self._onReadTracesThread)
        self._mStartTraceIndex = 0
        self._mEndTraceIndex = -1
        self.show()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        self._stopReadTracesThread()
        self._mTracerWidget.closeEvent(event)
        ListForQLineEdit.closeInstance()
        return

    def resizeEvent(self, QResizeEvent):
        return

    def setTraceRange(self, startIndex: int, endIndex: int):
        self._mStartTraceIndex = startIndex
        self._mEndTraceIndex = endIndex
        return

    def scrollToItemByLogIndex(self, logIndex: int):
        itemIndex = self._mTracerWidget.getRowItemByLogIndex(logIndex)
        if itemIndex >= 0:
            self._mTracerWidget.setSelectRow(itemIndex)
        else:
            Logger.w(appModel.getAppTag(), f"can't local index: {logIndex}")
        return

    def openTraceFile(self, path: str, dataType: int):
        Logger.i(appModel.getAppTag(), "")
        self._stopReadTracesThread()
        self._mTracerWidget.clearLog()
        if dataType == self.DATA_WBT:
            self._mWBXTracerFile = WBXTracerFile(path)
            self._mTraceDataType = dataType
        elif dataType == self.DATA_LGF:
            self._mLGFTracerFile.openFile(path, "utf-8")
            self._mTraceDataType = dataType
        else:
            Logger.e(appModel.getAppTag(), f"unknown data type: {dataType}")
        self._mTracerWidget.clearLog()
        self._mReadTracesThread = threading.Thread(target=self._onReadTracesThread)
        self._mReadTracesThread.start()
        return

    def openTraceData(self, Data, dataType: int):
        Logger.i(appModel.getAppTag(), "")
        self._stopReadTracesThread()
        self._mTracerWidget.clearLog()
        if dataType == self.DATA_WBT:
            self._mWBXTracerFile = WBXTracerFile(Data, False)
            self._mTraceDataType = dataType
        elif dataType == self.DATA_LGF:
            self._mLGFTracerFile.setContent(Data)
            self._mTraceDataType = dataType
        else:
            Logger.e(appModel.getAppTag(), f"unknown data type: {dataType}")
        self._mTracerWidget.clearLog()
        self._mReadTracesThread = threading.Thread(target=self._onReadTracesThread)
        self._mReadTracesThread.start()
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
        self.cbLogLevel.currentIndexChanged.connect(self._onSelectLogLevel)
        self._onSelectLogLevel(self.cbLogLevel.currentIndex())
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self.btSave.close()
        self.btSave.clicked.connect(self._onSaveLog)
        self.btSetting.clicked.connect(self._onSettingLogcat)
        self.btMark.clicked.connect(self._onMark)
        self.btPrevMark.clicked.connect(self._onPrevMark)
        self.btNextMark.clicked.connect(self._onNextMark)
        self.btFilter.clicked.connect(self._onFilterLogcat)

        self.editFilter.textChanged.connect(self._onEditorTextChanged)
        return

    def _stopReadTracesThread(self):
        thread = self._mReadTracesThread
        if thread.is_alive():
            Logger.i(appModel.getAppTag(), "join prev thread")
            thread.join()
        return

    def _onEditorTextChanged(self, newText):
        inputList = appModel.getRecentInputList(newText)
        Logger.i(appModel.getAppTag(), f"newText={newText}, inputList={inputList}")
        ListForQLineEdit.getInstance().showList(inputList, self.editFilter)
        return

    def _onReadTracesThread(self):
        autoScroll = self._mTracerWidget.isAutoScroll()
        self._mTracerWidget.setAutoScroll(False)
        if self._mTraceDataType == self.DATA_WBT:
            header = self._mWBXTracerFile.getHeader()
            self._mTracerWidget.beginLoad(header.mTraceCount)
            self._mWBXTracerFile.readTracesRange(self._onReadWBXTrace, None,
                                                 self._mStartTraceIndex, self._mEndTraceIndex)
            self._mTracerWidget.endLoad()
            del self._mWBXTracerFile
        elif self._mTraceDataType == self.DATA_LGF:
            self._mTracerWidget.beginLoad(self._mLGFTracerFile.getTraceCount())
            self._mLGFTracerFile.readTraces(self._onReadLogcatTrace, None)
            self._mTracerWidget.endLoad()
            del self._mLGFTracerFile
        self._mTracerWidget.setAutoScroll(autoScroll)
        return

    def _onReadWBXTrace(self, trace: WBXTraceItemV3, param: [any]) -> bool:
        if param is not None:
            Logger.i(appModel.getAppTag(), f"param len: {len(param)}")
        timeStr = trace.mDateTime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        pid = f"{trace.mPID}"
        tid = f"{trace.mTID}"
        level = self.getWBXTraceLevel.get(trace.mLevel, LoggerLevel.Info)
        tag = trace.mName
        message = trace.mMessage
        self._mTracerWidget.addTrace(trace.mIndex, timeStr, pid, tid, level, tag, message)
        return True

    def _onReadLogcatTrace(self, traceLog: LogcatItem, param: [any]) -> bool:
        if param is not None:
            Logger.i(appModel.getAppTag(), f"param len: {len(param)}")
        timeStr = traceLog.getDateTimeStr()
        pid = traceLog.mPID
        tid = traceLog.mTID
        level = traceLog.getLoggerLevel()
        tag = traceLog.mTag
        message = traceLog.mMessage
        self._mTracerWidget.addTrace(traceLog.mIndex, timeStr, pid, tid, level, tag, message)
        return True

    def _onSelectLogLevel(self, index):
        if index < 0:
            return

        curLogLevel = self.cbLogLevel.itemData(index)
        appModel.saveConfig(self.__class__.__name__, "selLogLevel", curLogLevel.name)
        Logger.i(appModel.getAppTag(), f"index={index}, logLevel={curLogLevel}")
        self._mTracerWidget.setFilter(curLogLevel)
        return

    def _onClearLog(self):
        Logger.i(appModel.getAppTag(), "")
        self._mTracerWidget.clearLog()
        return

    def _onSaveLog(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        # self._mTracerWidget.saveLog(path)
        return

    def _onSettingLogcat(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        tracerWidget = self._mTracerWidget
        cols = tracerWidget.getColsVisual()
        self._mSettingDlg = DialogTraceViewSetting(self,
                                                   cols[0],
                                                   cols[1],
                                                   cols[2],
                                                   cols[3],
                                                   cols[4],
                                                   cols[5],
                                                   )
        setting = self._mSettingDlg
        result = setting.exec()
        if result == Const.EXIT_OK:
            cols[0] = setting.showIndex()
            cols[1] = setting.showTime()
            cols[2] = setting.showPID()
            cols[3] = setting.showTID()
            cols[4] = setting.showLevel()
            cols[5] = setting.showTag()
        tracerWidget.setColsVisual(cols)
        return

    def _onMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        self._mTracerWidget.markToggle()
        return

    def _onPrevMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        self._mTracerWidget.prevMark()
        return

    def _onNextMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        self._mTracerWidget.nextMark()
        return

    def _onFilterLogcat(self):
        filterMsg = self.editFilter.text()
        appModel.addRecentInput(filterMsg)
        Logger.i(appModel.getAppTag(), f"filter {filterMsg} begin")
        self._mTracerWidget.setFilter(logInclude=filterMsg)
        Logger.i(appModel.getAppTag(), f"filter {filterMsg} end")
        return
