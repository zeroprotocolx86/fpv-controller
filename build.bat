@echo off
echo Building FPV Controller for Windows...

pip install pyinstaller vgamepad websockets pystray Pillow

pyinstaller --onefile ^
  --name "FPV-Controller" ^
  --noconsole ^
  --add-data "index.html;." ^
  --add-data "src\server.py;src" ^
  --hidden-import vgamepad ^
  --hidden-import websockets ^
  --hidden-import pystray ^
  --hidden-import PIL ^
  src\launcher.py

echo Done: dist\FPV-Controller.exe
pause
