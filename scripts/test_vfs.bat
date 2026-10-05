@echo off
cd /d %~dp0\..
python src\main.py --vfs data\vfs.json --script scripts\script.txt