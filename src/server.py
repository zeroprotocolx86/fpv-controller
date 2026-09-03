import asyncio
import json
import sys
import os

try:
    import vgamepad as vg
except ImportError:
    print("[ERROR] pip install vgamepad")
    sys.exit(1)

try:
    import websockets
except ImportError:
    print("[ERROR] pip install websockets")
    sys.exit(1)

WS_PORT = 8765

gamepad = vg.VX360Gamepad()

def map_axis(pwm):
    return (pwm - 1500) / 500.0

def update_gamepad(channels):
    try:
        yaw   = map_axis(channels[0])
        thr   = map_axis(channels[1])
        pitch = map_axis(channels[2])
        roll  = map_axis(channels[3])
        gamepad.left_joystick(x_value=int(yaw * 32767), y_value=int(-thr * 32767))
        gamepad.right_joystick(x_value=int(roll * 32767), y_value=int(-pitch * 32767))
        gamepad.update()
    except Exception as e:
        print(f"[GAMEPAD] Error: {e}")

channels = [1500, 1500, 1500, 1500]
clients = set()

async def handler(websocket):
    clients.add(websocket)
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
        clients.discard(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", WS_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
