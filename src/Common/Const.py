import sys

EXIT_OK = 100
EXIT_CANCEL = 101

adbDetectTimer = 2  # seconds, can be float, 0 -> stop
maxRecentPush = 10
maxRecentCommands = 20

isDebugMode = sys.gettrace() is not None

apkFileSuffix = "*.apk"
mappingFileSuffix = "*.txt"
logFileSuffix = "*.txt *.wbt *.lgf *.dmp"
logFileRegular = r".txt|.wbt|.lgf|.dmp"
zipFileSuffix = "*.zip"
zipFileRegular = r".zip"
imageFileSuffix = "*.jpg *.jpeg *.bmp *.gif *.png *.pbm *.pgm *.xbm *.xpm"
imageFileRegular = r".jpg|.jpeg|.bmp|.gif|.png|.pbm|.pgm|.xbm|.xpm"
allSupportRegular = logFileRegular + "|" + zipFileRegular + "|" + imageFileRegular
