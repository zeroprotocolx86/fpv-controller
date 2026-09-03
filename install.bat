@echo off

set "DIR=%~dp0"

echo.
echo FPV Controller - Adding to exceptions...
echo.

powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -Command \"Add-MpPreference -ExclusionPath ''%DIR%''; Unblock-File -Path ''%DIR%FPV-Controller.exe''; Write-Host Done; Start-Sleep 2\"' -Verb RunAs"

echo Starting FPV Controller...
start "" "%DIR%FPV-Controller.exe"
