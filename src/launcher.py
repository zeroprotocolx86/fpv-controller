"""
FPV Controller — launcher + WS server + HTTP server + Tray
All-in-one, no subprocess needed
"""

import os
import sys
import time
import socket
import json
import asyncio
import threading
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

CONFIG_PATH = os.path.join(BASE, "config.json")
DEFAULT_CFG = {"port": 8766, "ws_port": 8765, "auto_open": True}

def load_cfg():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_CFG.copy()

def save_cfg(c):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(c, f, indent=2)
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

# ===== GAMEPAD =====
gamepad = None
if vg:
    try:
        gamepad = vg.VX360Gamepad()
    except:
        pass

def map_axis(pwm):
    return (pwm - 1500) / 500.0

def update_gamepad(channels):
    if not gamepad:
        return
    try:
        yaw   = map_axis(channels[0])
        thr   = map_axis(channels[1])
        pitch = map_axis(channels[2])
        roll  = map_axis(channels[3])
        gamepad.left_joystick(x_value=int(yaw * 32767), y_value=int(-thr * 32767))
        gamepad.right_joystick(x_value=int(roll * 32767), y_value=int(-pitch * 32767))
        gamepad.update()
    except:
        pass

channels = [1500, 1500, 1500, 1500]
ws_clients = set()
ws_running = False

# ===== WEBSOCKET =====
async def ws_handler(websocket):
    ws_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                msg = json.loads(message)
                if msg.get("type") == "channels" and isinstance(msg.get("ch"), list):
                    channels[:] = [max(1000, min(2000, v)) for v in msg["ch"]]
                    update_gamepad(channels)
            except:
                pass
    except:
        pass
    finally:
        ws_clients.discard(websocket)

async def ws_main():
    global ws_running
    ws_running = True
    try:
        async with websockets.serve(ws_handler, "0.0.0.0", cfg["ws_port"]):
            await asyncio.Future()
    except Exception as e:
        print(f"[WS] Error: {e}")
        ws_running = False

ws_thread = None
ws_loop = None

def start_ws():
    global ws_thread, ws_loop, ws_running
    if ws_running:
        return
    def run():
        global ws_loop, ws_running
        ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(ws_loop)
        ws_running = True
        try:
            ws_loop.run_until_complete(ws_main())
        except:
            ws_running = False
    ws_thread = threading.Thread(target=run, daemon=True)
    ws_thread.start()

def stop_ws():
    global ws_running, ws_loop
    ws_running = False
    if ws_loop:
        ws_loop.call_soon_threadsafe(ws_loop.stop)

def restart():
    stop_ws()
    time.sleep(0.5)
    start_ws()

# ===== HTTP SERVER =====
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
    except Exception as e:
        print(f"[HTTP] Error: {e}")

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
    ip = get_ip()
    import webbrowser
    webbrowser.open(f"http://{ip}:{cfg['port']}")

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

def on_info(icon, item):
    ip = get_ip()
    msg = f"FPV Controller\n\n"
    msg += f"Телефон: http://{ip}:{cfg['port']}\n"
    msg += f"WS: ws://localhost:{cfg['ws_port']}\n\n"
    if gamepad:
        msg += "Xbox 360 геймпад активний\n"
    else:
        msg += "Геймпад: встанови vgamepad\n"
    msg += "Відкрий flight sim"

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
    print("  FPV Controller")
    print(f"  Телефон: http://{ip}:{port}")
    if gamepad:
        print("  Xbox 360 геймпад: OK")
    else:
        print("  Геймпад: встанови vgamepad")
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
            pystray.MenuItem("Відкрити в браузері", on_open, default=True),
            pystray.MenuItem("Інформація", on_info),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Запустити WS", on_start),
            pystray.MenuItem("Зупинити WS", on_stop),
            pystray.MenuItem("Перезапустити WS", on_restart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Вийти", on_quit)
        )

        tray_icon = pystray.Icon(
            "FPV",
            create_icon(),
            "FPV Controller",
            menu
        )

        tray_icon.run()
    else:
        print("Натисни Ctrl+C для зупинки")
        try:
            while running:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_ws()

if __name__ == "__main__":
    main()
