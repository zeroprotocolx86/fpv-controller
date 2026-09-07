"""
FPV Controller Uninstaller
Requires admin elevation - will re-launch with UAC if needed.
"""

import os
import sys
import ctypes
import subprocess
import time
import signal

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    script = os.path.abspath(__file__)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}"', None, 1
    )
    sys.exit(0)

def kill_process():
    lock = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)), ".fpv.lock")
    try:
        with open(lock) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
    except:
        pass
    try:
        os.remove(lock)
    except:
        pass

def remove_files(install_dir):
    removed = []
    for f in ["FPV-Controller.exe", "config.json", ".fpv.lock", "FPV-Uninstall.exe", "uninstall.py"]:
        p = os.path.join(install_dir, f)
        if os.path.exists(p):
            try:
                os.remove(p)
                removed.append(f)
            except:
                pass
    return removed

def run_inno_uninstall(install_dir):
    unins = os.path.join(install_dir, "unins000.exe")
    if os.path.exists(unins):
        subprocess.Popen([unins, "/SILENT"])

def main():
    if getattr(sys, 'frozen', False):
        install_dir = os.path.dirname(sys.executable)
    else:
        install_dir = os.path.dirname(os.path.abspath(__file__))

    if not is_admin():
        elevate()
        return

    kill_process()
    removed = remove_files(install_dir)
    run_inno_uninstall(install_dir)

    msg = "Видалено файли:\n" + "\n".join(removed) if removed else "Видалення завершено."
    ctypes.windll.user32.MessageBoxW(0, msg, "FPV Controller", 0x40 | 0x1000)

if __name__ == "__main__":
    main()
