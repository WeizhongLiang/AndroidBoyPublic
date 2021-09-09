import os
import subprocess

from src.Common import StringUtility
from src.Common.DumpFileHelper import SYMBOLIZER_APP
from src.Common.Logger import Logger
from src.Model.AppModel import appModel


def translateTrace(nativeSymbolFilePath: str, traceString: str) -> str:
    if len(traceString) <= 0:
        return ""
    if not os.path.exists(nativeSymbolFilePath):
        return traceString

    ## format trace str
    tempAddresses = open(appModel.getTmpFile("dump.addr"), "w")
    lines = traceString.split(os.linesep)
    for line in lines:
        stackValues = StringUtility.splitBySpace(line, '#')
        if len(stackValues) < 4:
            continue
        filename = os.path.basename(stackValues[3])
        tempAddresses.write(f"===== \"{line}\"\n{filename} 0x{stackValues[2]}\n\n")
    tempAddresses.close()

    ## parse
    tempAddresses = open(appModel.getTmpFile("dump.addr"), "r")
    symbolizer = appModel.getExtToolsFile("dump", SYMBOLIZER_APP)
    if not os.path.exists(symbolizer):
        return traceString

    symbolizerProcess = subprocess.Popen([symbolizer, '-pretty-print'],
                                         cwd=nativeSymbolFilePath,
                                         stdin=tempAddresses, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = symbolizerProcess.communicate()
    tempAddresses.close()
    # os.remove(tempAddresses.name)

    if stdout is not None:
        return stdout.decode("utf-8")
    else:
        return traceString
