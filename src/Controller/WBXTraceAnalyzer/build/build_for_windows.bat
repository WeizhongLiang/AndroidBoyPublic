@echo off
set fileDir=%~dp0
set devenv="C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\Common7\IDE\devenv.com"

cd %fileDir%

echo "start build from: %fileDir%"
echo ""
echo "========== begin =========="
%devenv% ./windows/WBXTraceAnalyzer.vcxproj /Project "WBXTraceAnalyzer" /rebuild "Release|x64" /Out
echo "========== end =========="
echo ""
pause


