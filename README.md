# FPV Controller

Телефон як віртуальний FPV-пульт (RadioMaster TX12) для тестування 프로그рам польотів.

Телефон перетворюється на Xbox 360 геймпад — flight sim бачить його як звичайний контролер.

## Що це робить

```
Телефон (джойстики) → WebSocket → ПК → Xbox 360 Gamepad → Flight Sim
```

- Два віртуальних джойстики на телефоні
- Mode 2 (як TX12): лівий = Throttle + Yaw, правий = Pitch + Roll
- Throttle не підтягується до центру (як на справжньому пульті)
- Expo, Rate, Deadband, Smoothing — налаштовуються
- Автоматично створює Xbox 360 геймпад на ПК
- Працює на Windows, macOS, Linux

## Встановлення

### Запуск з Python (простий спосіб)

```bash
# Клонувати
git clone https://github.com/username/fpv-controller.git
cd fpv-controller

# Встановити залежності
pip install -r requirements.txt

# Запустити
python src/launcher.py
```

### Збірка .exe (автономний)

**Windows:**
```bash
build.bat
```

**Linux / macOS:**
```bash
chmod +x build.sh
./build.sh
```

Готовий файл: `dist/FPV-Controller.exe` (або `FPV-Controller` на Linux/Mac)

## Використання

1. Запусти `FPV-Controller.exe`
2. Відкрий на телефоні: `http://<IP_ПК>:8766`
3. В flight simі обери Xbox 360 геймпад
4. Літай!

### Налаштування (ПКМ на значку в треї)

| Параметр | За замовч. | Опис |
|----------|-----------|------|
| Expo | 0.50 | М'якість по центру (0=лінійно, 1=м'яко) |
| Rate | 1.00 | Швидкість відгуку |
| Deadband | 3% | Мертва зона |
| Smoothing | 2 | Згладжування |

### Режими стіків

- **Mode 2** (за замовч.): Лівий = Throttle + Yaw, Правий = Pitch + Roll
- **Mode 1**: Лівий = Pitch + Roll, Правий = Throttle + Yaw

## Архітектура

```
fpv-controller/
├── index.html          # Веб-сторінка (джойстики)
├── src/
│   ├── launcher.py     # Головний запуск + System Tray
│   └── server.py       # WebSocket + Virtual Gamepad
├── requirements.txt
├── build.bat           # Збірка Windows
├── build.sh            # Збірка Linux/Mac
├── LICENSE
└── README.md
```

## Залежності

- **Python 3.10+**
- **vgamepad** — віртуальний Xbox 360 геймпад
- **websockets** — WebSocket сервер
- **pystray** + **Pillow** — значок в треї (опціонально)
- **PyInstaller** — для збірки .exe (опціонально)

### Для віртуального геймпаду

На Windows потрібен **ViGEmBus** драйвер:
https://github.com/nefarius/ViGEmBus/releases

## Ліцензія

MIT
