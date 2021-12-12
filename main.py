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


def runTestStock():
    import baostock as bs
    import pandas as pd

    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取交易日信息 ####
    rs = bs.query_trade_dates(start_date="2017-01-01", end_date="2017-06-30")
    print('query_trade_dates respond error_code:' + rs.error_code)
    print('query_trade_dates respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 结果集输出到csv文件 ####
    result.to_csv("D:\\trade_datas.csv", encoding="gbk", index=False)
    print(result)

    #### 登出系统 ####
    bs.logout()


def transH264():
    from src.Common.BinaryStream import BinaryStream
    fileSrc = open("D:\\github-repos\\AllCameras\\app\\src\\main\\assets\\len4_data.h264", mode="rb")
    fileTag = open("D:\\github-repos\\AllCameras\\app\\src\\main\\assets\\data.h264", mode="wb")
    bsRead = BinaryStream(fileSrc)
    bsWrite = BinaryStream(fileTag)
    while bsRead.readable():
        len = bsRead.readBigEndInt32()
        data = bsRead.readBytes(len)
        bsWrite.writeBytes(data)
    fileSrc.close()
    fileTag.close()
    return


if __name__ == '__main__':
    checkRunArgv()
    # transH264()
    runAndroidBoy()

# help:
# git archive --format zip --output AndroidBoy.zip master
