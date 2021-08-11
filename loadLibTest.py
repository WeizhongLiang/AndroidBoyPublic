import os
import re
import sys
import zipfile
import json

from src.Common.WBXTracerHelper import *
import src.Controller.WBXTraceAnalyzer as WBXAnalyzer

selfPath = os.path.dirname(os.path.realpath(__file__))
configPath = os.path.join(selfPath, "src", "Application", "Assets", "AndroidBoyCfg.json")
zipPath = os.path.join(selfPath, "webex-trace.zip")

mAnalyzeResult = {"KeyError": {}}


def _onCheckErrorInTrace(item: WBXTraceItemV3, param: [any]):
    checkList: {} = param[0]
    if len(checkList) == 0:
        return False
    for err, name in checkList.items():
        if err in item.mMessage:
            # item.mPosInFile
            mAnalyzeResult["KeyError"][err] = {
                "errName": name[0],
                "errType": name[1],
                "logIndex": item.mIndex,
                "logPos": item.mPosInFile,
                "logFile": param[1],
            }
            del checkList[err]
            return True
    return True


try:
    needToCheck = json.load(open(configPath, 'r'))["ViewOutlookDetector"]["errorDefinition"]
    errorDefine = json.dumps(needToCheck)

    procTime = DateTimeHelper.ProcessTime()
    WBXAnalyzer.setErrDefine(errorDefine)
    zipFile = zipfile.ZipFile(zipPath)
    for subFileName in zipFile.namelist():
        title = subFileName
        if not re.search(r".wbt$", subFileName, flags=re.IGNORECASE):
            continue
        fileData = zipFile.read(subFileName)
        fullSubFileName = f"{zipPath}?{subFileName}"
        if WBXAnalyzer.isValid():
            print(WBXAnalyzer.analyzeData(fileData, fullSubFileName))
        else:
            needToCheck = json.load(open(configPath, 'r'))["ViewOutlookDetector"]["errorDefinition"]
            mAnalyzeResult = {"KeyError": {}}
            WBXTracerFile(fileData, False).readTraces(
                _onCheckErrorInTrace, [needToCheck, "unknown file"])
            mAnalyzeResult = mAnalyzeResult["KeyError"]
            print(f"{json.dumps(mAnalyzeResult)}")
    print(f"end in {procTime.getMicroseconds()} seconds ")

except OSError:
    print("Unable to load the specified library.")
    sys.exit()

