echo off

set curDir=%~dp0
set pythonCMD=C:\Users\weizlian\AppData\Local\Programs\Python\Python39\python.exe
set App=%curDir%main.py
echo pythonCMD: %pythonCMD%
echo App: %App%

%pythonCMD% %App% hide_cmd > out.log

:: echo python ./main.py