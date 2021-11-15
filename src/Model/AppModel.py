import json
import sys
from datetime import datetime

from src.Common import FileUtility
from src.Common.Logger import *


class AppModel:
    configRecentInput = "RecentInput"

    def __init__(self):
        self._mAppName = "Application"
        self._mBasePath = os.getcwd()
        self.mSrcPath = ""
        self.mLayoutPath = ""
        self.mAppPath = ""
        self.mAssetsPath = ""
        self.mScriptPath = ""
        self._mAppTag = self._mAppName

        self._mAppConfig: [json] = None
        self._mConfigPath = None
        self._mRecentInput = []
        return

    def initApp(self, name, basePath: str, confName: str):
        if basePath is None:
            basePath = os.getcwd()
        self._mBasePath = basePath

        self.mSrcPath = os.path.join(self._mBasePath, "src")
        self.mLayoutPath = os.path.join(self.mSrcPath, "Layout")
        self.mAppPath = os.path.join(self.mSrcPath, "Application")
        self.mAssetsPath = os.path.join(self.mAppPath, "Assets")
        self.mScriptPath = os.path.join(self.mAppPath, "Script")
        sys.path.append(self.mLayoutPath)
        sys.path.append(self.mAppPath)

        self._mAppName = name
        self._mAppTag = name

        Logger.sShowLogLevel = LoggerLevel.Verbose
        Logger.i(self.getAppTag(), f"mBasePath={self._mBasePath}")
        Logger.i(self.getAppTag(), f"mSrcPath={self.mSrcPath}")
        Logger.i(self.getAppTag(), f"mLayoutPath={self.mLayoutPath}")
        Logger.i(self.getAppTag(), f"mAppPath={self.mAppPath}")
        Logger.i(self.getAppTag(), f"mAssetsPath={self.mAssetsPath}")
        Logger.i(self.getAppTag(), f"mScriptPath={self.mScriptPath}")
        if confName is not None:
            self._mAppConfig = FileUtility.loadJsonFile(self.getAssetsFile(confName))
            if len(self._mAppConfig) == 0:
                defaultConfName = "_" + confName
                self._mAppConfig = FileUtility.loadJsonFile(self.getAssetsFile(defaultConfName))
            self._mRecentInput = self.readConfig(self.getAppName(), self.configRecentInput, [])
            self._mConfigPath = self.getAssetsFile(confName)
            self.storeConfig()
        return

    def getAppName(self):
        return self._mAppName

    def getAppTag(self):
        return self._mAppName

    def getAppAbsolutePath(self, basePath: str, subPaths: [str], fileName: str):
        if basePath is None:
            folder = self._mBasePath
        else:
            folder = basePath
        for sub in subPaths:
            folder = os.path.join(folder, sub)
            FileUtility.makeFolder(folder)
        if fileName is not None and len(fileName) > 0:
            return os.path.join(folder, fileName)
        else:
            return folder

    def getWebexSymbolsFolder(self):
        return self.getAppAbsolutePath(self.mAssetsPath, ["WebexSymbols"], "")

    def getSrcFile(self, name):
        FileUtility.makeFolder(self.mSrcPath)
        return os.path.join(self.mSrcPath, name)

    def getLayoutFile(self, name):
        FileUtility.makeFolder(self.mLayoutPath)
        return os.path.join(self.mLayoutPath, name)

    def getAssetsFile(self, name):
        FileUtility.makeFolder(self.mAssetsPath)
        return os.path.join(self.mAssetsPath, name)

    def getScriptFile(self, name):
        FileUtility.makeFolder(self.mScriptPath)
        return os.path.join(self.mScriptPath, name)

    def getDefaultLogFolder(self) -> str:
        folder = os.path.join(self.mAssetsPath, "LogcatFiles")
        FileUtility.makeFolder(folder)
        return folder

    def getLogcatFile(self, deviceID: str):
        folder = self.getDefaultLogFolder()
        nowString = datetime.now().strftime('%Y%m%d_%H%M%S')
        if deviceID is None or len(deviceID) == 0:
            return os.path.join(folder, f"{nowString}.lgf")
        else:
            return os.path.join(folder, f"{deviceID}@{nowString}.lgf")

    def getTmpFile(self, name):
        folder = os.path.join(self.mAssetsPath, "Tmp")
        FileUtility.makeFolder(folder)
        return os.path.join(folder, name)

    def getExtToolsFile(self, subDir, name):
        folder = os.path.join(self.mAssetsPath, "ExtTools")
        FileUtility.makeFolder(folder)
        if subDir is not None:
            folder = os.path.join(folder, subDir)
            FileUtility.makeFolder(folder)
        return os.path.join(folder, name)

    def saveConfig(self, key, subKey, value):
        if self._mAppConfig is None:
            return False
        try:
            if subKey is None:
                self._mAppConfig[key] = value
            else:
                if key not in self._mAppConfig:
                    self._mAppConfig[key] = json.loads("{}")
                self._mAppConfig[key][subKey] = value
            return True
        except Exception as e:
            Logger.e(self.getAppTag(), f"saveConfigEx({key}{subKey}={value}) exception:{e}")
            return False

    def readConfig(self, key, subKey=None, defValue=None):
        if self._mAppConfig is None or key not in self._mAppConfig:
            return defValue
        try:
            if subKey is not None:
                if subKey not in self._mAppConfig[key]:
                    return defValue
                else:
                    return self._mAppConfig[key][subKey]
            else:
                return self._mAppConfig[key]
        except Exception as e:
            Logger.e(self.getAppTag(), f"readConfigEx({key}{subKey}) exception:{e}")
            return defValue

    def storeConfig(self):
        if self._mAppConfig is None:
            return False
        if self._mConfigPath is None:
            return False
        try:
            fw = open(self._mConfigPath, 'w')
            json.dump(self._mAppConfig, fw, indent=2, sort_keys=True)
            fw.close()
        except Exception as e:
            Logger.e(self.getAppTag(), f"storeConfig({self._mConfigPath}) exception:{e}")
        return True

    def addRecentInput(self, inputText):
        self.addArrayConfig(self.getAppName(), self.configRecentInput,
                            self._mRecentInput, inputText)
        return

    def getRecentInputList(self, includeText) -> [str]:
        return self.getArrayConfigList(self._mRecentInput, includeText)

    def addArrayConfig(self, key, subKey, arrayValues, newValue):
        if newValue in arrayValues or len(newValue) == 0:
            return
        arrayValues.append(newValue)
        if len(arrayValues) > 1024:
            arrayValues.pop(0)
        self.saveConfig(key, subKey, arrayValues)
        return

    @staticmethod
    def getArrayConfigList(arrayValues, value) -> [str]:
        retList = []
        if len(value) > 0:
            for text in arrayValues:
                if value.lower() in text.lower():
                    retList.append(text)
        return retList


appModel = AppModel()
