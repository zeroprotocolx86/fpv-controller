"""
FPV Controller
All-in-one: HTTP + WebSocket + Gamepad + System Tray
"""

import os
import sys
import time
import signal
import socket
import json
import threading
import asyncio
import urllib.request
import subprocess
import tempfile
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler

CURRENT_VERSION = "1.3.5"
REPO = "zeroprotocolx86/fpv-controller"

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
    MEIPASS = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    BASE = os.path.dirname(os.path.abspath(__file__))
    MEIPASS = BASE

HTML_PATH = None
for d in [MEIPASS, BASE, os.path.dirname(BASE)]:
    p = os.path.join(d, "index.html")
    if os.path.isfile(p):
        HTML_PATH = p
        break
if HTML_PATH is None:
    HTML_PATH = os.path.join(BASE, "index.html")

# ===== CONFIG =====
def load_cfg():
    try:
        p = os.path.join(BASE, "config.json")
        with open(p) as f:
            return json.load(f)
    except:
        return {"port": 8766, "ws_port": 8765, "auto_open": False}

cfg = load_cfg()

# ===== LOCK FILE =====
LOCK_FILE = os.path.join(BASE, ".fpv.lock")

def write_lock():
    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
    except:
        pass

def read_lock():
    try:
        with open(LOCK_FILE) as f:
            return int(f.read().strip())
    except:
        return None

def remove_lock():
    try:
        os.remove(LOCK_FILE)
    except:
        pass

def kill_previous():
    pid = read_lock()
    if pid and pid != os.getpid():
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
        except:
            pass
    write_lock()

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

# ===== UPDATE =====
def parse_version(v):
    v = v.strip().lstrip("v")
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except:
            parts.append(0)
    return parts

def check_update():
    try:
        url = f"https://api.github.com/repos/{REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "FPV-Controller"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            tag = data.get("tag_name", "")
            if parse_version(tag) > parse_version(CURRENT_VERSION):
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe") and "Setup" in asset["name"]:
                        return tag, asset["browser_download_url"]
    except:
        pass
    return None, None

def do_update(url, tag):
    try:
        tmp = os.path.join(tempfile.gettempdir(), "FPV-Controller-Setup.exe")
        urllib.request.urlretrieve(url, tmp)
        if tray_icon:
            try:
                tray_icon.stop()
            except:
                pass
        remove_lock()
        subprocess.Popen([tmp], shell=True)
        os._exit(0)
    except:
        pass

def check_and_update():
    pass

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
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        elif not '.' in self.path.split('/')[-1]:
            self.path = '/index.html'
        return super().do_GET()
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

# ===== QUIT =====
tray_icon = None

def do_quit():
    remove_lock()
    if tray_icon:
        try:
            tray_icon.stop()
        except:
            pass
    os._exit(0)

def do_uninstall():
    import shutil
    remove_lock()
    if tray_icon:
        try:
            tray_icon.stop()
        except:
            pass
    install_dir = BASE
    try:
        for f in ["FPV-Controller.exe", "config.json", ".fpv.lock", "unins000.exe", "unins000.dat"]:
            p = os.path.join(install_dir, f)
            if os.path.exists(p):
                os.remove(p)
    except:
        pass
    try:
        uninstaller = os.path.join(install_dir, "unins000.exe")
        if os.path.exists(uninstaller):
            subprocess.Popen([uninstaller, "/SILENT"])
    except:
        pass
    os._exit(0)

# ===== MAIN =====
def main():
    global tray_icon

    if "--quit" in sys.argv:
        pid = read_lock()
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.3)
            except:
                pass
        remove_lock()
        return

    if "--uninstall" in sys.argv:
        do_uninstall()
        return

    kill_previous()
    ip = get_ip()
    port = cfg["port"]

    threading.Thread(target=run_http, daemon=True).start()
    start_ws()

    if HAS_TRAY:
        update_tag = [None]
        update_url = [None]

        def on_open(icon, item):
            import webbrowser
            webbrowser.open(f"http://{ip}:{port}")

        def on_info(icon, item):
            import webbrowser
            webbrowser.open(f"https://github.com/{REPO}")

        def on_update(icon, item):
            if update_tag[0] and update_url[0]:
                threading.Thread(target=do_update, args=(update_url[0], update_tag[0]), daemon=True).start()

        def on_restart(icon, item):
            do_quit()

        def on_uninstall(icon, item):
            do_uninstall()

        def on_quit(icon, item):
            do_quit()

        def build_menu():
            items = [
                pystray.MenuItem("Відкрити", on_open, default=True),
                pystray.MenuItem("Інформація", on_info),
                pystray.MenuItem("Перезапустити", on_restart),
                pystray.MenuItem("Видалити", on_uninstall),
            ]
            if update_tag[0]:
                items.append(pystray.MenuItem(f"Оновити до {update_tag[0]}", on_update))
            items.append(pystray.MenuItem("Вийти", on_quit))
            return pystray.Menu(*items)

        tray_icon = pystray.Icon("FPV", make_icon(), "FPV Controller", build_menu())

        def check_update_thread():
            tag, url = check_update()
            if tag and url:
                update_tag[0] = tag
                update_url[0] = url
                try:
                    tray_icon.update_menu()
                    tray_icon.notify(f"Доступна версія {tag}", "FPV Controller")
                except:
                    pass

        threading.Thread(target=check_update_thread, daemon=True).start()
        tray_icon.run()
    else:
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
