import ctypes
import os

from src.Common import SystemHelper

_libPath = os.path.dirname(os.path.realpath(__file__))
if SystemHelper.isMac():
    _libPath = os.path.join(_libPath, "WBXTraceAnalyzer", "output", "mac", "libWBXTraceAnalyzer.dylib")
else:
    _libPath = os.path.join(_libPath, "WBXTraceAnalyzer", "output", "windows", "WBXTraceAnalyzer.dll")

try:
    _libHandle = ctypes.CDLL(_libPath)
    _setErrDefine = _libHandle.setErrDefine
    _setErrDefine.argtypes = [ctypes.c_char_p]
    _analyzeData = _libHandle.analyzeData
    _analyzeData.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
    _analyzeData.restype = ctypes.c_char_p
    _analyzeFile = _libHandle.analyzeFile
    _analyzeFile.argtypes = [ctypes.c_char_p]
    _analyzeFile.restype = ctypes.c_char_p
    _valid = True
except Exception as e:
    _valid = False


def isValid() -> bool:
    return _valid


def setErrDefine(errorDefine: str):
    if isValid():
        _setErrDefine(errorDefine.encode("ascii"))
    return


def analyzeData(logData: bytes, logFileName: str) -> str:
    if isValid():
        return _analyzeData(logData, len(logData), logFileName.encode("ascii")).decode("ascii")
    else:
        return "{}"


def analyzeFile(wbtPath: str) -> str:
    if isValid():
        return _analyzeFile(wbtPath.encode("ascii")).decode("ascii")
    else:
        return "{}"
