import os
import sys
import sysconfig


def printSystem(cmdStr: str) -> int:
    systemRet = os.system(cmdStr)
    if systemRet != 0:
        print(f"{cmdStr} failed: {systemRet}")
    return systemRet


print("sys.argv=" + sys.argv.__str__())
pythonDir = sysconfig.get_config_vars("prefix")[0]
if len(sys.argv) < 2:
    print("call me like: BaseDir")
    exit()
elif len(sys.argv) > 2:
    pythonDir = sys.argv[2]

baseDir = sys.argv[1]
if sys.platform == "win32":
    pyuic = os.path.join(pythonDir, "Scripts", "pyuic5")
    pyrcc = os.path.join(pythonDir, "Scripts", "pyrcc5")
else:
    pyuic = os.path.join(pythonDir, "bin", "pyuic5")
    pyrcc = os.path.join(pythonDir, "bin", "pyrcc5")
layoutDir = os.path.join(baseDir, "src", "Layout")

print(f"pyuic = {pyuic}")
print(f"pyrcc = {pyrcc}")
print(f"layoutDir = {layoutDir}")

os.chdir(layoutDir)
uiSuccessCount = 0
uiFailedCount = 0
rcSuccessCount = 0
rcFailedCount = 0
for file in os.listdir(layoutDir):
    fileName = os.path.splitext(file)
    if fileName[1] == ".ui":
        cmd = f"{pyuic} {file} -o {fileName[0]}.py"
        if printSystem(cmd) == 0:
            uiSuccessCount += 1
        else:
            uiFailedCount += 1
    elif fileName[1] == ".qrc":
        cmd = f"{pyrcc} {file} -o {fileName[0]}_rc.py"
        if printSystem(cmd) == 0:
            rcSuccessCount += 1
        else:
            rcFailedCount += 1

if uiFailedCount > 0 or rcFailedCount > 0:
    print("Failed:")
    print(f"Convert ui success: {uiSuccessCount}, failed: {uiFailedCount}")
    print(f"Convert rc success: {rcSuccessCount}, failed: {rcFailedCount}")
else:
    print(f"Success convert ui: {uiSuccessCount}, rc: {rcSuccessCount}")
