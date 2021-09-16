#!/bin/bash

python=/usr/local/bin/python3.9
pip=/Library/Frameworks/Python.framework/Versions/3.9/bin/pip3
fileDir=$(dirname "$0")
# fileDir=$(pwd)
echo "$fileDir"
cd "$fileDir" || exit
$python ./main.py pip=$pip &> ./output.txt &
# $python ./main.py pythonPath=$python pipPath=$pip &> ./output.txt &

# for mac, do below to close terminal window:
# in Terminal.app
# Preferences > Profiles > (Select a Profile) > Shell.
# on 'When the shell exits' chosen 'Close the window'
exit
