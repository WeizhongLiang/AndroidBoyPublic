import pyperclip
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QMenu, QFileDialog, QMessageBox

from src.Common import ADBHelper, QTHelper, SystemHelper
from src.Common.ADBHelper import *
from src.Common.LogcatFile import LogcatFile
from src.Common.Logger import Logger
from src.Layout.viewLogcat import Ui_Form

from src.Common.QTHelper import ListForQLineEdit
from src.Model.AppModel import appModel
from src.View.WidgetNotify import WidgetNotify
from src.View.DialogTraceViewSetting import DialogTraceViewSetting
from src.View.WidgetTracerList import WidgetTracerList


class ViewLogcat(QWidget, Ui_Form):

    _mEventDeviceChanged = QtCore.pyqtSignal(int)  # index

    def __init__(self, parent=None):
        super(ViewLogcat, self).__init__(parent)
        Logger.i(appModel.getAppTag(), "")
        self._mCurDevice = None
        self._mPreFilterPID = 0
        self._mPreFilterCount = 0
        self._mLogcatFileLock = threading.RLock()
        self._mLogcatFile = LogcatFile()

        self._mRecentPush = []
        for index in range(0, Const.maxRecentPush):
            msg = appModel.readConfig(self.__class__.__name__, f"RecentPush_{index}", None)
            if msg is not None:
                self._mRecentPush.append(msg)

        self.setupUi(self)
        QTHelper.switchMacUI(self)

        self.ckUsingRegx.setChecked(appModel.readConfig(self.__class__.__name__, f"FilterUsingRegx", False))
        self._mTracerWidget = WidgetTracerList(self, __class__.__name__, True)
        self.layoutTracer.addWidget(self._mTracerWidget)
        self._mNotifyWidget = WidgetNotify(self)
        self._mNotifyWidget.close()
        self._bindEvent()
        self._initLogLevel()
        self.show()
        self._initDeviceManager()
        return

    def closeEvent(self, event):
        Logger.i(appModel.getAppTag(), "")
        self._mDeviceManager.detectConnect(None)
        self._mDeviceManager.detectProcess("", "", None)
        self._mDeviceManager.finish()
        self._setCurDevice(None)
        self._mTracerWidget.closeEvent(event)
        self._mLogcatFile.closeWrite()
        ListForQLineEdit.closeInstance()
        return

    def _setCurDevice(self, device: AndroidDevice = None):
        if self._mCurDevice == device:
            return
        self._mPreFilterPID = -1
        self.cbPackages.clear()
        self.cbProcesses.clear()
        self._onStopLogcat()
        self._mCurDevice = device
        # self._onStartLogcat()
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

    def _initDeviceManager(self):
        self._mDeviceManager = ADBHelper.AndroidDeviceManager()
        self._mDeviceManager.detectConnect(self._onDeviceChanged)
        return

    def _bindEvent(self):
        Logger.i(appModel.getAppTag(), "")

        self.btStop.hide()

        self.cbDevices.currentIndexChanged.connect(self._onSelectDevice)
        self.cbPackages.currentIndexChanged.connect(self._onSelectPackage)
        self.cbProcesses.currentIndexChanged.connect(self._onSelectProcess)
        self.btStart.clicked.connect(self._onStartLogcat)
        self.btStop.clicked.connect(self._onStopLogcat)
        self.btSaveToFile.clicked.connect(self._onSaveToFile)
        self.btClear.clicked.connect(self._onClearLog)
        self.btAutoScroll.clicked.connect(self._onAutoScroll)
        self.btSetting.clicked.connect(self._onSettingLogcat)
        self.btMark.clicked.connect(self._onMark)
        self.btPrevMark.clicked.connect(self._onPrevMark)
        self.btNextMark.clicked.connect(self._onNextMark)
        self.btOpenLogFolder.clicked.connect(self._onBTOpenLogFolder)
        self.btFilter.clicked.connect(self._onFilterLogcat)
        self.ckUsingRegx.clicked.connect(self._onFilterLogcat)
        self.btInstallAPK.clicked.connect(self._onBTInstallAPK)
        self.btPushText.clicked.connect(self._onBTPushText)
        self.btClipperText.clicked.connect(self._onBTClipperText)
        self.btADBWifi.clicked.connect(self._onBTADBWifi)

        self.editFilter.textChanged.connect(self._onEditorTextChanged)

        self._mEventDeviceChanged.connect(self._onSelectDevice)
        return

    def _onEditorTextChanged(self, newText):
        inputList = appModel.getRecentInputList(newText)
        Logger.i(appModel.getAppTag(), f"newText={newText}, inputList={inputList}")
        ListForQLineEdit.getInstance().showList(inputList, self.editFilter)
        return

    def _onDeviceChanged(self, added, removed):
        Logger.i(appModel.getAppTag(), f"added={added}, removed={removed}")

        self.cbDevices.currentIndexChanged.disconnect(self._onSelectDevice)
        for devID in added:
            device = AndroidDevice(devID)
            self.cbDevices.addItem(device.__str__(), device)
        for devID in removed:
            for item in reversed(range(0, self.cbDevices.count())):
                device = self.cbDevices.itemData(item)
                if device.mID == devID:
                    self.cbDevices.removeItem(item)
                    device.finish()
        self.cbDevices.currentIndexChanged.connect(self._onSelectDevice)
        self._mEventDeviceChanged.emit(self.cbDevices.currentIndex())
        return

    def _onProcessChanged(self, added, removed):
        Logger.i(appModel.getAppTag(), f"added={added}, removed={removed}")

        self.cbProcesses.currentIndexChanged.disconnect(self._onSelectProcess)
        for processID in added:
            process = AndroidProcess(processID)
            self.cbProcesses.addItem(process.__str__(), process)
        for processID in removed:
            processTmp = AndroidProcess(processID)
            for item in reversed(range(0, self.cbProcesses.count())):
                process = self.cbProcesses.itemData(item)
                if process.mPID == processTmp.mPID:
                    self.cbProcesses.removeItem(item)
                if process.mPID == self._mPreFilterPID:
                    self._mPreFilterPID = -1
                    self.cbProcesses.setEditText("")
        lastSel = appModel.readConfig(self.__class__.__name__, "selProcess", "")
        setSel = self.cbProcesses.findText(lastSel + "-", Qt.MatchContains)
        if setSel >= 0 and setSel != self.cbProcesses.currentIndex():
            self.cbProcesses.setCurrentIndex(setSel)
        else:
            pass
            # self.cbProcesses.setCurrentIndex(0)
        self.cbProcesses.currentIndexChanged.connect(self._onSelectProcess)
        # select item
        self._onSelectProcess(self.cbProcesses.currentIndex())
        self.cbProcesses.update()
        return

    def _onSelectDevice(self, index):
        if index < 0:
            self._setCurDevice(None)
            self.cbDevices.update()
            self.cbPackages.update()
            self.cbProcesses.update()
            return

        curDevice = self.cbDevices.itemData(index)
        self._setCurDevice(curDevice)

        devInfo = "[%s - %s(%s@%s)]@[Android %s, API %s]: abi = [%s]" % \
                  (
                      curDevice.mProductBrand,
                      curDevice.mProductModel,
                      curDevice.mProductName,
                      curDevice.mProductBoard,
                      curDevice.mBuildVersionRelease,
                      curDevice.mBuildVersionSDK,
                      curDevice.mABIList,
                  )
        Logger.i(appModel.getAppTag(), f"index={index}, device={devInfo}")

        packages = curDevice.getPackages()
        lastSel = appModel.readConfig(self.__class__.__name__, "selPackage", "")
        self.cbPackages.clear()
        if len(packages) > 0:
            self.cbPackages.currentIndexChanged.disconnect(self._onSelectPackage)
            for package in packages:
                self.cbPackages.addItem(package.__str__(), package)
            setSel = self.cbPackages.findText(lastSel + "-", Qt.MatchContains)
            if setSel >= 0 and setSel != self.cbPackages.currentIndex():
                self.cbPackages.setCurrentIndex(setSel)
            else:
                self.cbPackages.setCurrentIndex(0)
            self.cbPackages.currentIndexChanged.connect(self._onSelectPackage)
            self._onSelectPackage(self.cbPackages.currentIndex())
        return

    def _onSelectPackage(self, index):
        if index < 0:
            return

        curPackage = self.cbPackages.itemData(index)
        self.cbProcesses.clear()
        self._mPreFilterPID = -1
        Logger.i(appModel.getAppTag(), f"index={index}, package={curPackage}")
        appModel.saveConfig(self.__class__.__name__, "selPackage", curPackage.mAPK)

        self._mDeviceManager.detectProcess(self._mCurDevice.mID, curPackage.mUID, self._onProcessChanged)
        return

    def _onSelectProcess(self, index):
        if index < 0:
            return

        curProcess = self.cbProcesses.itemData(index)
        Logger.i(appModel.getAppTag(), f"index={index}, process={curProcess}")
        appModel.saveConfig(self.__class__.__name__, "selProcess", curProcess.mNAME)

        self._mLogcatFileLock.acquire()
        self._mLogcatFile.writePIDName(curProcess.mPID, curProcess.mNAME)
        self._mLogcatFileLock.release()
        self._mPreFilterPID = curProcess.mPID
        self._mPreFilterCount = 0
        return

    def _onSelectLogLevel(self, index):
        if index < 0:
            return

        curLogLevel = self.cbLogLevel.itemData(index)
        appModel.saveConfig(self.__class__.__name__, "selLogLevel", curLogLevel.name)
        Logger.i(appModel.getAppTag(), f"index={index}, logLevel={curLogLevel}")
        self._mTracerWidget.setFilter(logLevel=curLogLevel)
        return

    def _onPreFilterLog(self, logItem: AndroidLogItem):
        if self._mPreFilterPID == -1:
            return False
        if int(logItem.getPID()) != self._mPreFilterPID:
            return True
        else:
            self._mPreFilterCount += 1
            # if self._mPreFilterCount % 1000 == 0:
            #    Logger.d(appModel.getAppTag(), f"_mPreFilterCount = {self._mPreFilterCount}")
            return False

    def _onLogcat(self, logItems: [AndroidLogItem]):
        self._mLogcatFileLock.acquire()
        for logItem in logItems:
            timeStr = logItem.getDateTimeStr()
            pid = logItem.getPID()
            tid = logItem.getTID()
            level = logItem.getLogLevel()
            tag = logItem.getTag()
            message = logItem.getMsg()
            self._mLogcatFile.writeTraces(logItem.getFull())
            self._mTracerWidget.addTrace(-1, timeStr, pid, tid, level, tag, message)
        self._mLogcatFileLock.release()
        return

    def _onStartLogcat(self):
        if self._mCurDevice is not None:
            Logger.i(appModel.getAppTag(), "")
            self._mTracerWidget.starTimer()
            self._mCurDevice.startCaptureLogcat(self._onPreFilterLog, self._onLogcat)
            self.btStart.hide()
            self.btStop.show()
        else:
            Logger.i(appModel.getAppTag(), "no selected device.")
        return

    def _onStopLogcat(self):
        Logger.i(appModel.getAppTag(), "")
        if self._mCurDevice is not None:
            self._mCurDevice.stopCaptureLogcat()
            self._mDeviceManager.detectProcess("", "", None)
            self.btStart.show()
            self.btStop.hide()
            self._mTracerWidget.stopTimer()
        return

    def _onSaveToFile(self):
        self._mLogcatFileLock.acquire()
        if self.btSaveToFile.isChecked():
            logcatPath = appModel.getLogcatFile("")
            self._mLogcatFile.createFile(logcatPath, "utf-8")
            if len(logcatPath) > 0:
                self._mNotifyWidget.notify(f"Write log into file:{logcatPath}", 2)
        else:
            logcatPath, traceCount = self._mLogcatFile.closeWrite()
            if len(logcatPath) > 0:
                if traceCount > 0:
                    self._mNotifyWidget.notify(f"Saved to file:{logcatPath}", 2)
                else:
                    self._mNotifyWidget.notify(f"No record was saved to file:{logcatPath}", 2)
        self._mLogcatFileLock.release()
        return

    def _onClearLog(self):
        Logger.i(appModel.getAppTag(), "")
        self._mTracerWidget.clearLog(True)
        return

    def _onAutoScroll(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        if self._mTracerWidget.isAutoScroll():
            self._mTracerWidget.setAutoScroll(False)
        else:
            self._mTracerWidget.setAutoScroll(True)
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

    def _onPrevMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        self._mTracerWidget.prevMark()
        return

    def _onNextMark(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        self._mTracerWidget.nextMark()
        return

    def _onBTOpenLogFolder(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        SystemHelper.openAtExplorer(appModel.getDefaultLogFolder())
        return

    def _onFilterLogcat(self):
        filterMsg = self.editFilter.text()
        appModel.addRecentInput(filterMsg)
        Logger.i(appModel.getAppTag(), f"filter {filterMsg} begin")
        self._mTracerWidget.setFilter(logInclude=filterMsg, usingRegx=self.ckUsingRegx.isChecked())
        appModel.saveConfig(self.__class__.__name__, f"FilterUsingRegx", self.ckUsingRegx.isChecked())
        Logger.i(appModel.getAppTag(), f"filter {filterMsg} end")
        return

    def _onBTInstallAPK(self):
        Logger.i(appModel.getAppTag(), f"{self}")
        if self._mCurDevice is None:
            return

        import os
        title = "Select apk file"
        startDir = appModel.readConfig(self.__class__.__name__, "selectAPKDir", "")
        typeFilter = f"APK Files ({Const.apkFileSuffix})"
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,
                                                caption=title,
                                                directory=startDir,
                                                filter=typeFilter,
                                                options=options)
        for selFile in files:
            fileDir = os.path.dirname(selFile)
            appModel.saveConfig(self.__class__.__name__, "selectAPKDir", fileDir)
            Logger.i(appModel.getAppTag(), f"will install: {selFile}")
            self._mCurDevice.installAPK(selFile)

        return

    def _onBTPushText(self):
        message = pyperclip.paste()
        try:
            index = self._mRecentPush.index(message)
            self._mRecentPush.pop(index)
            self._mRecentPush.insert(0, message)
        except ValueError:
            self._mRecentPush.insert(0, message)
            if len(self._mRecentPush) > Const.maxRecentPush:
                self._mRecentPush.pop(Const.maxRecentPush - 1)

        menu = QMenu(self)
        index = 0
        for msg in self._mRecentPush:
            msg = (msg[:30] + '..') if len(msg) > 30 else msg
            menu.addAction(f"push \"{msg}\"")
            appModel.saveConfig(self.__class__.__name__, f"RecentPush_{index}", self._mRecentPush[index])
            index += 1
        action = menu.exec_(self.mapToParent(QCursor.pos()))
        if action is None:
            return

        index = menu.actions().index(action)
        msg = self._mRecentPush[index]
        Logger.i(appModel.getAppTag(), f"{self._mCurDevice} - {msg}")
        if self._mCurDevice is None:
            return
        self._mCurDevice.pushText(msg)
        return

    def _onBTClipperText(self):
        Logger.i(appModel.getAppTag(), f"{self._mCurDevice}")
        if self._mCurDevice is None:
            return

        # installed clipper.apk?
        # download apk: https://github.com/majido/clipper/releases/download/v1.2.1/clipper.apk
        # open it in device and set it to auto run
        # call "adb shell am broadcast -a clipper.get" to get the clipper data

        devID = self._mCurDevice.mID
        apkName = "ca.zgrs.clipper"

        # find clipper
        clipperPackage: AndroidPackage = self._mCurDevice.findPackage(apkName)
        if clipperPackage is None:
            Logger.i(appModel.getAppTag(), f"{self._mCurDevice} will install clipper.apk first.")
            # install it
            clipperAPK = appModel.getExtToolsFile("android_clipper", "clipper.apk")
            # clipperAPK = appModel.getExtToolsFile("android_clipper", "Clipper_v2.4.17.apk")
            self._mCurDevice.installAPK(clipperAPK)
            # find again
            clipperPackage = self._mCurDevice.findPackage(apkName)
            if clipperPackage is None:
                Logger.e(appModel.getAppTag(), f"{self._mCurDevice} install clipper.apk failed.")
                return

        # open clipper
        # processes = self._mCurDevice.getProcesses(clipperPackage.mUID)
        # if len(processes) == 0:
        adbReturn(devID, f"shell am start -n ca.zgrs.clipper/ca.zgrs.clipper.Main", True)

        # call get clipper
        clipperText = adbReturn(devID, f"shell am broadcast -a clipper.get", True)
        if "Broadcast completed: result=0" in clipperText:
            # try again
            time.sleep(1)
            clipperText = adbReturn(devID, f"shell am broadcast -a clipper.get", True)
        qm = QMessageBox()
        qm.information(self,
                       f"Get clipper data from device",
                       f"{clipperText}",
                       qm.Ok)
        return

    def _onBTADBWifi(self):
        Logger.i(appModel.getAppTag(), f"{self._mCurDevice}")
        if self._mCurDevice is None:
            return

        # get ipv4 first
        wlan0 = adbReturn(self._mCurDevice.mID, f"shell ip addr show wlan0", True)
        match = re.search(f".+inet (.+?)/", wlan0)
        if match is None:
            QMessageBox().warning(self, '', f"No ipv4 found:{os.linesep}{wlan0}", QMessageBox.Yes)
            return
        ipv4 = match.group(1)

        # need to disconnect?
        qm = QMessageBox()
        ret = qm.question(self, '', f"Need to disconnect everything first?", qm.Yes | qm.No)
        if ret == qm.Yes:
            adbReturn(None, f"disconnect", True)
        else:
            adbReturn(None, f"disconnect {ipv4}", True)

        # set wifi connect port
        adbReturn(self._mCurDevice.mID, f"tcpip 5555", True)

        # connect it
        ret = adbReturn(None, f"connect {ipv4}:5555", True)
        QMessageBox().information(self, '', f"Connected to {ipv4} via WIFI:{os.linesep}{ret}", QMessageBox.Yes)
        return
