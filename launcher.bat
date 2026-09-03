@echo off
chcp 65001 >nul
title FPV Controller

set "DIR=%~dp0"
set "EXE=%DIR%FPV-Controller.exe"

echo.
echo   FPV Controller
echo.

if not exist "%EXE%" (
    echo [ERROR] FPV-Controller.exe не знайдено!
    pause
    exit /b 1
)

:: Remove Mark of the Web (Zone.Identifier) - this is what usually blocks downloaded .exe
powershell -Command "Unblock-File -Path '%EXE%'" 2>nul

:: Try to run
start "" "%EXE%"
if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Якщо програма не запускається:
    echo     1. Клікни правою кнопкою на FPV-Controller.exe
    echo     2. Обери "Властивості"
    echo     3. Постав галочку "Розблокувати" внизу
    echo     4. Натисни "Застосувати"
    echo.
    pause
)
