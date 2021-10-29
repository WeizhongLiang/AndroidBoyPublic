# AndroidBoyPublic


```
main.py: startup script
run.bat: a shortcut to start up App from Windows OS.
run.sh: a shortcut to start up App from macOS.
src
  Application
    AndroidBoy.py: App main UI
    Assets
      _AndroidBoyCfg.json: default config file
    Script
      getAllFolders.applescript: apple script for getting all folders under Outlook account
      getMails.applescript: apple script for getting all mails under Outlook account
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
  PyQt6
  PyQt6-stubs
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
  
3. To run Outlook detector in macOS, please install "JSON Helper for AppleScript" first.

4. Config your IDE (if you like):
Add "<-" and "-> :
"Setting" -> "Appearance & Behavior" -> "Menus and Toolbars"
	"Navigation Bar Toolbar" -> "CodeWithMeNavbarGroup" -> "+" -> "Add Action..."
		"Main Menu" -> "Navigate", select "Back" and "Forward"

Add qt designer:
"Setting" -> "Tools" -> "External Tools" -> "+"
	Name: QtDesigner
	Description: Open in qt designer
	Program(Windows): $PyInterpreterDirectory$\Scripts\designer.exe
	Program(Mac): /Applications/Qt Designer.app
	Arguments: $FileDir$\$FileNameWithoutExtension$.ui
	Working directory: $ProjectFileDir$
"Setting" -> "Appearance & Behavior" -> "Menus and Toolbars"
	"Scope View Popup Menu" -> "Project View Popup Menu" -> "New" -> "+" -> "Add Action..."
		"External Tools" -> "External Tools" -> "QtDesigner"

Add qt ui convert:
"Setting" -> "Tools" -> "External Tools" -> "+"
	Name: Qt ui2py
	Description: Convert ui files to py
	Program(Windows): $PyInterpreterDirectory$\python
	Arguments(Windows): $ProjectFileDir$\Qt_ui2py.py $ProjectFileDir$ $PyInterpreterDirectory$
	Program(Mac): $ModuleSdkPath$
	Arguments(Mac): $ProjectFileDir$/Qt_ui2py.py $ProjectFileDir$ 
	Working directory: $ProjectFileDir$
"Setting" -> "Appearance & Behavior" -> "Menus and Toolbars"
	"Navigation Bar Toolbar" -> "CodeWithMeNavbarGroup" -> "+" -> "Add Action..."
		"External Tools" -> "External Tools" -> "Qt ui2py"
```

