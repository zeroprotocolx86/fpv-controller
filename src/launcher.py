"""
FPV Controller
All-in-one: HTTP + WebSocket + Gamepad + System Tray
"""

import os
import sys
import time
import socket
import json
import threading
import asyncio
import traceback
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
    for d in [os.path.dirname(BASE), BASE]:
        p = os.path.join(d, "index.html")
        if os.path.exists(p):
            HTML_PATH = p
            break

# ===== CONFIG =====
def load_cfg():
    try:
        p = os.path.join(BASE, "config.json")
        with open(p) as f:
            return json.load(f)
    except:
        return {"port": 8766, "ws_port": 8765, "auto_open": True}

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
    except Exception as e:
        print(f"[GAMEPAD] {e}")

channels = [1500, 1500, 1500, 1500]

def update_gamepad(ch):
    if not gamepad:
        return
    try:
        def m(p):
            return (p - 1500) / 500.0
        gamepad.left_joystick(
            x_value=int(m(ch[0]) * 32767),
            y_value=int(-m(ch[1]) * 32767)
        )
        gamepad.right_joystick(
            x_value=int(m(ch[2]) * 32767),
            y_value=int(-m(ch[3]) * 32767)
        )
        gamepad.update()
    except:
        pass

# ===== WEBSOCKET =====
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
    try:
        asyncio.run(ws_server())
    except Exception as e:
        print(f"[WS] {e}")

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

def run_http():
    try:
        d = os.path.dirname(HTML_PATH) if os.path.exists(HTML_PATH) else BASE
        srv = HTTPServer(("0.0.0.0", cfg["port"]), Handler)
        srv.serve_forever()
    except Exception as e:
        print(f"[HTTP] {e}")

# ===== ICON =====
def make_icon(color="#3fb950"):
    if not HAS_TRAY:
        return None
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 4, 60, 60], radius=12, fill="#1c2128", outline=color, width=3)
    d.polygon([(24, 20), (44, 32), (24, 44)], fill=color)
    return img

# ===== MAIN =====
def main():
    ip = get_ip()
    port = cfg["port"]

    print("")
    print("  FPV Controller")
    print(f"  Phone: http://{ip}:{port}")
    print(f"  Gamepad: {'OK' if gamepad else 'NO'}")
    print("")

    # Start servers
    threading.Thread(target=run_http, daemon=True).start()
    start_ws()

    # Open browser
    if cfg.get("auto_open", True):
        time.sleep(1)
        try:
            import webbrowser
            webbrowser.open(f"http://{ip}:{port}")
        except:
            pass

    # System tray
    if HAS_TRAY:
        def on_open(icon, item):
            import webbrowser
            webbrowser.open(f"http://{ip}:{port}")

        def on_quit(icon, item):
            icon.stop()

        menu = pystray.Menu(
            pystray.MenuItem("Open", on_open, default=True),
            pystray.MenuItem("Quit", on_quit)
        )

        icon = pystray.Icon("FPV", make_icon(), "FPV Controller", menu)
        icon.run()
    else:
        print("No tray - press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        input("Press Enter...")
