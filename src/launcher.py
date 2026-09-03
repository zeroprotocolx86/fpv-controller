"""
FPV Controller — all-in-one
HTTP + WebSocket + Gamepad + Tray
"""

import os
import sys
import time
import socket
import json
import threading
import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    import vgamepad as vg
except ImportError:
    vg = None

try:
    import websockets
except ImportError:
    websockets = None

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# ===== PATHS =====
if getattr(sys, 'frozen', False):
    BASE = os.path.dirname(sys.executable)
else:
    BASE = os.path.dirname(os.path.abspath(__file__))

HTML_PATH = os.path.join(BASE, "index.html")
if not os.path.exists(HTML_PATH):
    alt = os.path.join(os.path.dirname(BASE), "index.html")
    if os.path.exists(alt):
        HTML_PATH = alt

# ===== CONFIG =====
DEFAULT_CFG = {"port": 8766, "ws_port": 8765, "auto_open": True}

def load_cfg():
    try:
        p = os.path.join(BASE, "config.json")
        with open(p) as f:
            return json.load(f)
    except:
        return DEFAULT_CFG.copy()

cfg = load_cfg()

# ===== IP =====
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

# ===== GAMEPAD =====
gamepad = None
if vg:
    try:
        gamepad = vg.VX360Gamepad()
    except:
        pass

def update_gamepad(ch):
    if not gamepad:
        return
    try:
        def m(p): return (p - 1500) / 500.0
        gamepad.left_joystick(x_value=int(m(ch[0]) * 32767), y_value=int(-m(ch[1]) * 32767))
        gamepad.right_joystick(x_value=int(m(ch[2]) * 32767), y_value=int(-m(ch[3]) * 32767))
        gamepad.update()
    except:
        pass

channels = [1500, 1500, 1500, 1500]

# ===== WEBSOCKET =====
ws_running = False

async def ws_handler(websocket):
    async for message in websocket:
        try:
            msg = json.loads(message)
            if msg.get("type") == "channels" and isinstance(msg.get("ch"), list):
                channels[:] = [max(1000, min(2000, v)) for v in msg["ch"]]
                update_gamepad(channels)
        except:
            pass

async def ws_server():
    async with websockets.serve(ws_handler, "0.0.0.0", cfg["ws_port"]):
        await asyncio.Future()

def run_ws():
    global ws_running
    ws_running = True
    try:
        asyncio.run(ws_server())
    except:
        ws_running = False

def start_ws():
    t = threading.Thread(target=run_ws, daemon=True)
    t.start()

# ===== HTTP =====
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        d = os.path.dirname(HTML_PATH) if os.path.exists(HTML_PATH) else BASE
        super().__init__(*a, directory=d, **kw)
    def log_message(self, *a):
        pass

http_server = None

def run_http():
    global http_server
    try:
        d = os.path.dirname(HTML_PATH) if os.path.exists(HTML_PATH) else BASE
        http_server = HTTPServer(("0.0.0.0", cfg["port"]), Handler)
        http_server.serve_forever()
    except:
        pass

# ===== TRAY =====
def create_icon(color="#3fb950"):
    if not HAS_TRAY:
        return None
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, 60, 60], radius=12, fill="#1c2128", outline=color, width=3)
    draw.polygon([(24, 20), (44, 32), (24, 44)], fill=color)
    return img

tray_icon = None
running = True

def on_open(icon, item):
    import webbrowser
    webbrowser.open(f"http://{get_ip()}:{cfg['port']}")

def on_info(icon, item):
    ip = get_ip()
    msg = f"Телефон: http://{ip}:{cfg['port']}\n"
    msg += f"WS: ws://localhost:{cfg['ws_port']}\n\n"
    msg += "Xbox 360 геймпад: " + ("OK" if gamepad else "немає")
    if sys.platform == "win32":
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("FPV Controller", msg)
        root.destroy()

def on_quit(icon, item):
    global running
    running = False
    if http_server:
        http_server.shutdown()
    if icon:
        icon.stop()

# ===== MAIN =====
def main():
    global tray_icon

    ip = get_ip()
    port = cfg["port"]

    print(f"  FPV Controller")
    print(f"  Телефон: http://{ip}:{port}")

    threading.Thread(target=run_http, daemon=True).start()
    start_ws()

    if cfg.get("auto_open", True):
        time.sleep(1)
        try:
            import webbrowser
            webbrowser.open(f"http://{ip}:{port}")
        except:
            pass

    if HAS_TRAY:
        menu = pystray.Menu(
            pystray.MenuItem("Відкрити", on_open, default=True),
            pystray.MenuItem("Інформація", on_info),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Вийти", on_quit)
        )
        tray_icon = pystray.Icon("FPV", create_icon(), "FPV Controller", menu)
        tray_icon.run()
    else:
        print("Ctrl+C для зупинки")
        try:
            while running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
