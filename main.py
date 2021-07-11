from src.Common.PackageChecker import PackageChecker

PackageChecker("AndroidBoy", 500, 300)


def checkRunArgv():
    import sys
    from src.Common import SystemHelper
    print("sys.platform=" + sys.platform)
    print("sys.argv=" + sys.argv.__str__())
    if SystemHelper.isWindows():
        try:
            import win32con
            import win32gui

            for i in range(1, len(sys.argv)):
                argv = sys.argv[i].lower()
                if argv == "hide_cmd":
                    win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_HIDE)
        except BaseException as e:
            print("run failed: " + e.__str__())
    return


def runAndroidBoy():
    import os
    from src.Model.AppModel import appModel
    curPath = os.path.dirname(os.path.realpath(__file__))
    appModel.initApp("AndroidBoy", curPath, "AndroidBoyCfg.json")
    from src.Application.AndroidBoy import AndroidBoy
    app = AndroidBoy()
    # app = ADBShell(0.3, 0.3)
    # app = src.Application.UITester.UITester(0.3, 0.3)
    # app = StockFormula(0.8, 0.8)
    if app is not None:
        del app
    return


if __name__ == '__main__':
    checkRunArgv()
    runAndroidBoy()

# help:
# git archive --format zip --output AndroidBoy.zip master
