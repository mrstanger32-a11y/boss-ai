import re, webbrowser, pywhatkit
from AppOpener import open as open_app
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def set_volume(level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
    except:
        pass


async def handle_command(cmd):
    cmd = cmd.lower()
    if "brightness" in cmd:
        val = re.search(r'\d+', cmd)
        if val:
            sbc.set_brightness(int(val.group()))
            return f"Brightness set to {val.group()}%"

    if "play" in cmd:
        song = cmd.replace("play", "").strip()
        pywhatkit.playonyt(song)
        return f"Playing {song}"

    if "open" in cmd:
        app = cmd.replace("open", "").strip()
        open_app(app, match_closest=True)
        return f"Opening {app}"

    return None