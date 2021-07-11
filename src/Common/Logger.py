import colorama
import os
import traceback

from src.Common import Const
from src.Common.DateTimeHelper import getNowString
from src.Common.IntEnum import IntEnum


def getCurrentFunName(depth):
    # see more at : https://docs.python.org/3/library/inspect.html
    try:
        frameCaller = traceback.extract_stack(None, depth)[0]
        # frameCaller = sys._getframe(depth)
        # codeCaller = frameCaller.name
        # callerName = codeCaller.co_name
        # callerFile = os.path.basename(codeCaller.co_filename)
        # callerLine = frameCaller.f_lineno
        callerName = frameCaller.name
        callerFile = os.path.basename(frameCaller.filename)
        callerLine = frameCaller.lineno
        return "%s:%s@%d" % (callerFile, callerName, callerLine)
    except BaseException:
        return "%s:%s@%d" % ('unknown', 'unknown', -1)


class LoggerLevel(IntEnum):
    Verbose = 0
    Debug = 1
    Info = 2
    Warning = 3
    Error = 4
    Fatal = 5
    Silent = 6


_sLogStackDepth = 3


class Logger:
    if Const.isDebugMode:
        sShowLogLevel = LoggerLevel.Verbose
    else:
        sShowLogLevel = LoggerLevel.Info
    getLoggerColor = {
        LoggerLevel.Verbose: colorama.Fore.BLACK,
        LoggerLevel.Debug: colorama.Fore.LIGHTBLACK_EX,
        LoggerLevel.Info: colorama.Fore.BLACK,
        LoggerLevel.Warning: colorama.Fore.BLUE,
        LoggerLevel.Error: colorama.Fore.RED,
        LoggerLevel.Fatal: colorama.Fore.RED,
        LoggerLevel.Silent: colorama.Fore.RED
    }

    @staticmethod
    def _print(log: str):
        print(log)
        return

    @staticmethod
    def v(tag, log):
        if Logger.sShowLogLevel > LoggerLevel.Verbose:
            return
        Logger._print(Logger.getLoggerColor.get(LoggerLevel.Verbose)
                      + f"{getNowString(None)} Verbose/{tag}: {getCurrentFunName(_sLogStackDepth)}: {log}")
        return

    @staticmethod
    def d(tag, log):
        if Logger.sShowLogLevel > LoggerLevel.Debug:
            return
        Logger._print(Logger.getLoggerColor.get(LoggerLevel.Debug)
                      + f"{getNowString(None)} Debug/{tag}: {getCurrentFunName(_sLogStackDepth)}: {log}")
        return

    @staticmethod
    def i(tag, log):
        if Logger.sShowLogLevel > LoggerLevel.Info:
            return
        Logger._print(Logger.getLoggerColor.get(LoggerLevel.Info)
                      + f"{getNowString(None)} Info/{tag}: {getCurrentFunName(_sLogStackDepth)}: {log}")
        return

    @staticmethod
    def w(tag, log):
        if Logger.sShowLogLevel > LoggerLevel.Warning:
            return
        Logger._print(Logger.getLoggerColor.get(LoggerLevel.Warning)
                      + f"{getNowString(None)} Warning/{tag}: {getCurrentFunName(_sLogStackDepth)}: {log}")
        return

    @staticmethod
    def e(tag, log):
        if Logger.sShowLogLevel > LoggerLevel.Error:
            return
        Logger._print(Logger.getLoggerColor.get(LoggerLevel.Error)
                      + f"{getNowString(None)} Error/{tag}: {getCurrentFunName(_sLogStackDepth)}: {log}")
        return
