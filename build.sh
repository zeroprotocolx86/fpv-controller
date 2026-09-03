#!/bin/bash
# FPV Controller — Build script for Linux / macOS
echo "Building FPV Controller..."

# Install deps
pip install pyinstaller vgamepad websockets pystray Pillow 2>/dev/null

# Build
pyinstaller --onefile \
  --name "FPV-Controller" \
  --console \
  --add-data "index.html:." \
  --add-data "src/server.py:src" \
  --hidden-import vgamepad \
  --hidden-import websockets \
  --hidden-import pystray \
  --hidden-import PIL \
  src/launcher.py

echo "Done: dist/FPV-Controller"
