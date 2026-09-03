@echo off
chcp 65001 >nul
title FPV Controller — Додавання у винятки

echo.
echo   FPV Controller
echo   Додавання у винятки безпеки
echo.

:: Run PowerShell script as admin
powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0fix-permissions.ps1\"' -Verb RunAs"

exit /b
