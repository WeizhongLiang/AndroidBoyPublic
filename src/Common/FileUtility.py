import json
import os

from typing import Tuple

from src.Common.Logger import Logger


def makeFolderForFile(filePath):
    folder = os.path.dirname(filePath)
    try:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        return True
    except Exception as e:
        Logger.e("FileUtility", f"makeFolder{folder} failed:{e}")
        return False


def makeFolder(folder):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        return True
    except Exception as e:
        Logger.e("FileUtility", f"makeFolder{folder} failed:{e}")
        return False


def saveFile(path, content):
    if not makeFolderForFile(path):
        return False
    try:
        file = open(path, "wb")
        file.write(content)
        file.close()
        Logger.i("FileUtility", f"saved to file: {path}.")
        return True
    except Exception as e:
        Logger.e("FileUtility", f"save to {path} failed:{e}")
        return False


def loadJsonFile(path: str):
    if os.path.exists(path):
        f = open(path, 'r')
        try:
            jsonContent = json.load(f)
        except Exception as e:
            Logger.e("FileUtility", f"loadJsonFile({path}) exception:{e}")
            jsonContent = json.loads("{}")
            f.close()
    else:
        jsonContent = json.loads("{}")
    return jsonContent


def saveJsonFile(path: str, jsonContent: {}) -> bool:
    try:
        fw = open(path, 'w')
        json.dump(jsonContent, fw, indent=2, sort_keys=True)
        fw.close()
        return True
    except Exception as e:
        Logger.e("FileUtility", f"saveJSonFile({path}) exception:{e}")
        return False


def getDictValue(dictValue: {}, nodes: [], ele: str, default: str) -> Tuple[bool, str]:
    for node in nodes:
        if node in dictValue:
            dictValue = dictValue[node]
        else:
            return False, default
    if ele in dictValue:
        return True, dictValue[ele]
    else:
        return False, default


def fileSizeFmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
