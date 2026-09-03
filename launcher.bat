@echo off
chcp 65001 >nul
title FPV Controller

set "EXE=%~dp0FPV-Controller.exe"

:: Check if already in exceptions
powershell -Command "if (Get-MpPreference | Select-Object -ExpandProperty ExclusionPath | Where-Object { $_ -eq '%~dp0' }) { exit 0 } else { exit 1 }"
if %ERRORLEVEL% equ 0 (
    echo [OK] Already in exceptions, starting...
    start "" "%EXE%"
    exit /b
)

echo.
echo   FPV Controller
echo.
echo   Потрібні права адміністратора
echo   для додавання у винятки Windows Defender.
echo.

:: Request admin and add exclusion
powershell -Command "Start-Process powershell -ArgumentList '-Command', 'Add-MpPreference -ExclusionPath \"%~dp0\"; Write-Host \"[OK] Додано у винятки\"; Start-Sleep 2' -Verb RunAs"

:: Wait a bit
timeout /t 3 /nobreak >nul

:: Start the app
echo [OK] Запуск...
start "" "%EXE%"
