"""
FPV Controller Uninstaller
Видаляє FPV Controller з системи
"""

import os
import sys
import shutil
import subprocess
import ctypes

APP_NAME = "FPV Controller"
LOCAL_APPDATA = os.environ.get("LOCALAPPDATA", "")
INSTALL_DIR = os.path.join(LOCAL_APPDATA, APP_NAME)
START_MENU = os.path.join(os.environ.get("APPDATA", ""), 
    "Microsoft", "Windows", "Start Menu", "Programs", APP_NAME)
DESKTOP = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def kill_process():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "FPV-Controller.exe"], 
                      capture_output=True, timeout=5)
    except:
        pass

def remove_files():
    removed = []
    
    for directory in [INSTALL_DIR, START_MENU]:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                removed.append(directory)
            except Exception as e:
                print(f"  Помилка видалення {directory}: {e}")
    
    lnk = os.path.join(DESKTOP, f"{APP_NAME}.lnk")
    if os.path.exists(lnk):
        try:
            os.remove(lnk)
            removed.append(lnk)
        except:
            pass
    
    return removed

def run_uninstaller():
    unins = os.path.join(INSTALL_DIR, "unins000.exe")
    if os.path.exists(unins):
        try:
            subprocess.Popen([unins, "/SILENT"], shell=True)
            return True
        except:
            pass
    return False

def main():
    print(f"\n{'='*50}")
    print(f"  Видалення {APP_NAME}")
    print(f"{'='*50}\n")
    
    print("[1/3] Зупинка процесів...")
    kill_process()
    print("  Готово\n")
    
    print("[2/3] Видалення файлів...")
    removed = remove_files()
    if removed:
        for path in removed:
            print(f"  Видалено: {path}")
    else:
        print("  Файли не знайдено")
    print()
    
    print("[3/3] Завершення...")
    if run_uninstaller():
        print("  Запущено деінсталер Inno Setup")
    else:
        print("  Деінсталер не знайдено")
    
    print(f"\n{'='*50}")
    print(f"  {APP_NAME} видалено!")
    print(f"{'='*50}\n")
    
    input("Натисни Enter для завершення...")

if __name__ == "__main__":
    main()
