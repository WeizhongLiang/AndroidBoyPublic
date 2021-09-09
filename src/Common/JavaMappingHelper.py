import os
import subprocess

from src.Common.Logger import Logger
from src.Model.AppModel import appModel


def translateTrace(mappingFilePath: str, traceString: str) -> str:
    if len(traceString) <= 0:
        return ""
    if not os.path.exists(mappingFilePath):
        return traceString

    Logger.i(appModel.getAppTag(), f"begin")
    runDir = os.path.join(appModel.mAssetsPath, "ExtTools", "retrace")

    # save temp file
    tempTrace = open(os.path.join(runDir, "java_trace.txt"), "w")
    tempTrace.write(traceString)
    tempTrace.close()

    # call java -jar retrace.jar mapping41.8.txt trace.txt
    retraceProcess = subprocess.Popen(
        ["java", "-jar", "retrace.jar", mappingFilePath, "java_trace.txt"],
        cwd=runDir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = retraceProcess.communicate()
    os.remove(tempTrace.name)

    Logger.i(appModel.getAppTag(), f"end")
    if stdout is not None:
        return stdout.decode("utf-8")
    else:
        return traceString


def translateTrace2(mappingFilePath: str, traceString: str) -> str:
    if len(traceString) <= 0:
        return ""
    if not os.path.exists(mappingFilePath):
        return traceString

    Logger.i(appModel.getAppTag(), f"begin")
    runDir = os.path.join(appModel.mAssetsPath, "ExtTools", "retrace2/bin")

    # save temp file
    tempTrace = open(os.path.join(runDir, "java_trace.txt"), "w")
    tempTrace.write(traceString)
    tempTrace.close()

    # call retrace mapping41.8.txt trace.txt
    retraceProcess = subprocess.Popen(
        ["./retrace", mappingFilePath, "java_trace.txt"],
        cwd=runDir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = retraceProcess.communicate()
    os.remove(tempTrace.name)

    Logger.i(appModel.getAppTag(), f"end")
    if stdout is not None:
        return stdout.decode("utf-8")
    else:
        return traceString
