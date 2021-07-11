# AndroidBoyPublic


main.py: startup script
run.bat: a short cut to start up App from Windows OS.
run.sh: a short cut to start up App from MAC OS.
src
  Application
    AndroidBoy.py: App main UI
    Assets
      _AndroidBoyCfg.json: default config file
    Script
       getAllFolders.applescript: apple script for getting all folders under outlook account
       getMails.applescript: apple script for getting all mails under outlook account
    Common: some help utility
    Controller
      CCTGDownloader.py: controller for downloading apk and symbol files
      OutlookCtrl.py: controller for reading mail from local.
      TicketEmailAnalyzer: controller for analyzing ticket email.
    Layout: layout file using by QtPy5
    Model: a command AppModel
    Thirdparty
      google_trans_new: from: https://github.com/topics/google-trans-new, I have fixed one bug in it.
    View: UI file relates to layout file under Layout folder.


1. Please make sure Python 3.3+ has been installed.
  For Windows: https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe
  For Mac: https://www.python.org/ftp/python/3.9.6/python-3.9.6-macosx10.9.pkg

2. This App relies  on the following packages:
  psutil
  PyQt5
  PyQt5-stubs
  requests
  pyperclip
  colorama
  numpy
  pycryptodome
  pywin32 (For Windows)
  applescript (For Mac)

  When run this App, App will try to install them via PIP automatically, but in some case, the App
  can't find out where is the PIP command, and you need to specify the path of PIP in run.bat or run.sh.
  In most instances, it would be in this path:
  Windows: <The python path>/Script
  Mac: /Library/Frameworks/Python.framework/Versions/3.9/bin/pip
  Please refer to run.bat or run.sh.

