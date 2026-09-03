@echo off

set "DIR=%~dp0"
set "EXE=%DIR%FPV-Controller.exe"

if not exist "%EXE%" (
    echo FPV-Controller.exe not found!
    pause
    exit /b 1
)

start "" "%EXE%"
