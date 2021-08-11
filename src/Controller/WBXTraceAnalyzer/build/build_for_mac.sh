#!/bin/bash

fileDir=$(dirname "$0")
# fileDir=$(pwd)
cd "$fileDir" || exit
echo "start build from: $fileDir"
echo ""
echo "========== begin =========="
xcodebuild -project ./mac/WBXTraceAnalyzer.xcodeproj -target WBXTraceAnalyzer
echo "========== end =========="
echo ""
read -n 1 -s -r -p "Press any key to continue"
