import os
import subprocess
import threading
import tkinter
from tkinter import *

from typing import Tuple

sDependentModules = {
    "psutil": {"name": "psutil", "platform": ""},
    "PyQt5": {"name": "PyQt5", "platform": ""},
    "PyQt5-stubs": {"name": "PyQt5-stubs", "platform": ""},
    "requests": {"name": "requests", "platform": ""},
    "pyperclip": {"name": "pyperclip", "platform": ""},
    "colorama": {"name": "colorama", "platform": ""},
    "numpy": {"name": "numpy", "platform": ""},
    # "Crypto": {"name": "PyCryptodome", "platform": ""},
    "PyCryptodome": {"name": "pycryptodome", "platform": ""},
    # for windows
    "pyWin32": {"name": "pywin32", "platform": "win32"},
    # for mac
    "applescript": {"name": "applescript", "platform": "darwin"},
}


class PackageChecker:
    def __init__(self, name: str, width: int, height: int):
        import sys
        self._mThreadPIP = threading.Thread(target=self._onPIPThread)
        self._mName = name
        self._mWidth = width
        self._mHeight = height
        self._mErrorMsg = ""
        self._mExit = False
        print(f"{os.linesep}------- PackageChecker begin -------")

        findSuccess = False
        for i in range(1, len(sys.argv)):
            argv = sys.argv[i].lower()
            if "pip=" in argv:
                self._mPIPPath = argv[argv.find("=", 0)+1:]
                print(f"set pip to: {self._mPIPPath}")
                findSuccess = True
                break
        if not findSuccess:
            findSuccess, self._mPIPPath = self._getPIPPath()
        if findSuccess:
            self._mMissedPackages = self._checkPackages(sDependentModules)
        else:
            self._mMissedPackages = sDependentModules
        self._showUI(findSuccess)
        print(f"------- PackageChecker end -------{os.linesep}")
        return

    def getMissPackages(self):
        return self._mMissedPackages

    def _getCenterGeometryString(self, tkWnd: Tk, width, height):
        # print(f"getCenterGeometryString width={width},height={height}")
        screenWidth = tkWnd.winfo_screenwidth()
        screenHeight = tkWnd.winfo_screenheight()

        if width < 0 or height < 0:
            return
        if width < 1:
            self._mWidth = screenWidth * width
        if height < 1:
            self._mHeight = screenHeight * height

        offsetX = (screenWidth - self._mWidth) / 2
        offsetY = (screenHeight - self._mHeight) / 2
        return "%dx%d+%d+%d" % (self._mWidth, self._mHeight, offsetX, offsetY)

    def _getPIPPathLinux(self) -> Tuple[bool, str]:
        try:
            pipProcess = subprocess.Popen(["pip", "--version"],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = pipProcess.communicate()
            if len(stderr) != 0:
                error = stderr.decode("utf-8")
                self._mErrorMsg = f"Please install python first: {error}"
                return False, ""
            # pip 21.1.3 from /abc/def/pip (python 3.9)
            pipVersion = stdout.decode().rstrip()
            if len(pipVersion) > 0:
                return True, "pip"
            else:
                return False, ""
        except Exception as e:
            self._mErrorMsg = f"_getPIPPathLinux find where is pip failed: {e}"
            return False, ""

    def _getPIPPathWindows(self) -> Tuple[bool, str]:
        try:
            pipProcess = subprocess.Popen(["where", "python"],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = pipProcess.communicate()
            if len(stderr) != 0:
                error = stderr.decode("utf-8")
                self._mErrorMsg = f"Please install python first: {error}"
                return False, ""
            pythonPath = stdout.decode().rstrip().split(os.linesep)[0]
            return True, os.path.join(os.path.dirname(pythonPath), "Scripts", "pip")
        except Exception as e:
            self._mErrorMsg = f"_getPIPPathWindows find where is python failed: {e}"
            return False, ""

    def _getPIPPath(self) -> Tuple[bool, str]:
        import sys
        if sys.platform == "win32":
            return self._getPIPPathWindows()
        else:
            return self._getPIPPathLinux()

    def _checkPackages(self, packages: {}) -> {}:
        import sys
        self._mMissedPackages = {}
        try:
            pipProcess = subprocess.Popen([self._mPIPPath, "list"],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = pipProcess.communicate()
            packagesList = stdout.decode("utf-8")
            for alia, package in packages.items():
                platform = package["platform"]
                if len(platform) > 0 and sys.platform != platform:
                    continue
                if package["name"] not in packagesList:
                    # print(f"{alia}: need to be installed")
                    self._mMissedPackages[alia] = package
            return self._mMissedPackages
        except Exception as e:
            self._mErrorMsg = f"_checkPackages exec pip -list failed: {e}"
            self._mMissedPackages = packages
            return self._mMissedPackages

    def _showUI(self, findSuccess: bool) -> bool:
        if len(self._mMissedPackages) == 0:
            return True
        tkWnd = Tk()
        tkTextOutput = Text(tkWnd, fg="black", bg="lightyellow")
        tkWnd.title(self._mName)
        tkWnd.geometry(self._getCenterGeometryString(tkWnd, self._mWidth, self._mHeight))
        tkWnd.resizable(0, 0)
        tkWnd.update()
        tkTextOutput.tag_config("black", foreground="black")
        tkTextOutput.tag_config("red", foreground="red")
        tkTextOutput.tag_config("blue", foreground="blue")
        tkTextOutput.pack()
        tkTextOutput.place(x=0, y=0, width=self._mWidth, height=self._mHeight)
        # tkTextOutput.configure(state='normal')
        tkTextOutput.delete('1.0', 'end')
        if findSuccess:
            missInfo = "We need to install below packages before running the App:" + os.linesep
            for alia, package in self._mMissedPackages.items():
                name = package["name"]
                missInfo += f"  {alia} - {name}{os.linesep}"
            missInfo += os.linesep + os.linesep
            tkTextOutput.insert(tkinter.END, missInfo)
            # tkTextOutput.configure(state='disabled')
            self._mThreadPIP = threading.Thread(target=self._onPIPThread, args=(tkWnd, tkTextOutput))
            self._mThreadPIP.start()
        else:
            tkTextOutput.insert(tkinter.END, self._mErrorMsg, "red")
            self._mExit = True
        tkWnd.mainloop()
        tkWnd.destroy()
        if self._mExit:
            exit()
        return True

    def _onPIPThread(self, tkWnd: Tk, tkTextOutput: Text):
        for alia, package in self._mMissedPackages.items():
            name = package["name"]
            installCmd = [self._mPIPPath, "install", name]
            try:
                tkTextOutput.insert(
                    tkinter.END,
                    f"Installing {name} ......{os.linesep}{installCmd}{os.linesep}",
                    "blue")
                pipProcess = subprocess.Popen(installCmd,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = pipProcess.communicate()
                if len(stderr) > 0:
                    tkTextOutput.insert(tkinter.END, stderr.decode("utf-8"), "red")
                else:
                    tkTextOutput.insert(tkinter.END, stdout.decode("utf-8"), "black")
                tkTextOutput.insert(tkinter.END, os.linesep, "black")
            except Exception as e:
                tkTextOutput.insert(tkinter.END, f"{e}", "red")
            tkTextOutput.see(END)
        tkTextOutput.insert(tkinter.END, os.linesep + "Mission completed.", "black")
        tkTextOutput.see(END)
        self._mMissedPackages = self._checkPackages(sDependentModules)
        if len(self._mMissedPackages) == 0:
            self._mExit = False
            tkWnd.quit()
        else:
            tkTextOutput.insert(tkinter.END, os.linesep + "Packages install failed.", "red")
            tkTextOutput.see(END)
            self._mExit = True
        return
