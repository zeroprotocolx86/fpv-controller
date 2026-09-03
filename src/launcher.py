"""
FPV Controller — launcher
Cross-platform: Windows / macOS / Linux
System tray icon with menu
"""

import os
import sys
import time
import socket
import json
import threading
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ===== PATHS =====
if getattr(sys, 'frozen', False):
    BASE = os.path.dirname(sys.executable)
else:
    BASE = os.path.dirname(os.path.abspath(__file__))

# Check for index.html next to exe or in parent
HTML_PATH = os.path.join(BASE, "index.html")
if not os.path.exists(HTML_PATH):
    HTML_PATH = os.path.join(os.path.dirname(BASE), "index.html")
SERVER_PATH = os.path.join(BASE, "server.py")
if not os.path.exists(SERVER_PATH):
    SERVER_PATH = os.path.join(os.path.dirname(BASE), "src", "server.py")
CONFIG_PATH = os.path.join(BASE, "config.json")

DEFAULT_CFG = {"port": 8766, "ws_port": 8765, "auto_open": True}

def load_cfg():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_CFG.copy()

def save_cfg(cfg):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except:
        pass

cfg = load_cfg()

# ===== FIND IP =====
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

# ===== HTTP SERVER =====
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=os.path.dirname(HTML_PATH), **kw)
    def log_message(self, *a):
        pass

http_server = None
ws_proc = None
tray_icon = None
running = True

def run_http():
    global http_server
    try:
        http_server = HTTPServer(("0.0.0.0", cfg["port"]), Handler)
        http_server.serve_forever()
    except Exception as e:
        print(f"[HTTP] Error: {e}")

def start_ws():
    global ws_proc
    try:
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW
        ws_proc = subprocess.Popen(
            [sys.executable, SERVER_PATH],
            cwd=os.path.dirname(SERVER_PATH),
            creationflags=creation_flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("[WS] Started")
    except Exception as e:
        print(f"[WS] Error: {e}")

def stop_ws():
    global ws_proc
    if ws_proc:
        try:
            ws_proc.terminate()
            ws_proc.wait(timeout=3)
        except:
            try:
                ws_proc.kill()
            except:
                pass
        ws_proc = None
        print("[WS] Stopped")

def restart():
    stop_ws()
    time.sleep(0.5)
    start_ws()

# ===== TRAY ICON (pystray) =====
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False
    print("[TRAY] pystray not installed, running without tray icon")
    print("[TRAY] Install: pip install pystray Pillow")

def create_icon(color="#3fb950"):
    if not HAS_TRAY:
        return None
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, 60, 60], radius=12, fill="#1c2128", outline=color, width=3)
    draw.polygon([(24, 20), (44, 32), (24, 44)], fill=color)
    return img

def on_open(icon, item):
    ip = get_ip()
    url = f"http://{ip}:{cfg['port']}"
    import webbrowser
    webbrowser.open(url)

def on_restart(icon, item):
    restart()
    if tray_icon:
        tray_icon.icon = create_icon("#3fb950")

def on_stop(icon, item):
    stop_ws()
    if tray_icon:
        tray_icon.icon = create_icon("#f85149")

def on_start(icon, item):
    start_ws()
    if tray_icon:
        tray_icon.icon = create_icon("#3fb950")

def on_quit(icon, item):
    global running
    running = False
    stop_ws()
    if http_server:
        http_server.shutdown()
    if icon:
        icon.stop()

def on_settings(icon, item):
    ip = get_ip()
    msg = f"FPV Controller\n\n"
    msg += f"Phone: http://{ip}:{cfg['port']}\n"
    msg += f"WS: ws://localhost:{cfg['ws_port']}\n\n"
    msg += f"Xbox 360 gamepad active\n"
    msg += f"Open flight sim to detect gamepad"

    if sys.platform == "win32":
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("FPV Controller", msg)
        root.destroy()
    else:
        print(msg)

# ===== MAIN =====
def main():
    global tray_icon

    ip = get_ip()
    port = cfg["port"]

    print("")
    print("  ╔═══════════════════════════════════╗")
    print("  ║        FPV CONTROLLER             ║")
    print("  ╚═══════════════════════════════════╝")
    print(f"  Phone: http://{ip}:{port}")
    print("  Xbox 360 gamepad active")
    print("")

    # Start HTTP
    t = threading.Thread(target=run_http, daemon=True)
    t.start()

    # Start WS
    start_ws()

    # Open browser
    if cfg.get("auto_open", True):
        time.sleep(1)
        import webbrowser
        try:
            webbrowser.open(f"http://{ip}:{port}")
        except:
            pass

    # Tray icon
    if HAS_TRAY:
        menu = pystray.Menu(
            pystray.MenuItem("Open in browser", on_open, default=True),
            pystray.MenuItem("Settings", on_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start WS", on_start),
            pystray.MenuItem("Stop WS", on_stop),
            pystray.MenuItem("Restart WS", on_restart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", on_quit)
        )

        tray_icon = pystray.Icon(
            "FPV",
            create_icon(),
            "FPV Controller",
            menu
        )

        tray_icon.run()
    else:
        # No tray — just wait
        print("Press Ctrl+C to stop")
        try:
            while running:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_ws()

if __name__ == "__main__":
    main()
