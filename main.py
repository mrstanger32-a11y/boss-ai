import flet as ft
import asyncio
import os
import re
import uuid
import speech_recognition as sr
import edge_tts
import pygame
import pywhatkit
import psutil
from AppOpener import open as open_app
from groq import Groq
from dotenv import load_dotenv

import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

JARVIS_CYAN = "#00ffff"
JARVIS_GREEN = "#00ff88"
JARVIS_BLUE = "#0044ff"
DARK_BG = "#050810"

LOGO_PATH = "daemon_logo.jpg"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def set_system_volume(level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return True
    except:
        return False


async def speak(text: str):
    voice_file = f"temp_{uuid.uuid4().hex[:5]}.mp3"
    try:
        communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural", rate="+15%")
        await communicate.save(voice_file)
        pygame.mixer.music.load(voice_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
    except:
        pass
    finally:
        pygame.mixer.music.unload()
        if os.path.exists(voice_file):
            try:
                os.remove(voice_file)
            except:
                pass


async def main(page: ft.Page):
    page.bgcolor = DARK_BG
    page.title = "D.A.E.M.O.N. — J.A.R.V.I.S. HUD ULTRA"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_width = 1200
    page.window_height = 800
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # ─────────────────────────────────────────────────
    #  SPLASH SCREEN
    # ─────────────────────────────────────────────────
    boot_lines = [
        "INITIALIZING DAEMON CORE...",
        "LOADING NEURAL MODULES...",
        "CALIBRATING VOICE ENGINE...",
        "SYNCING SYSTEM SENSORS...",
        "ESTABLISHING SECURE LINK...",
        "SYSTEM READY.",
    ]

    boot_text = ft.Text(
        "",
        color=JARVIS_GREEN,
        size=13,
        font_family="Consolas",
        weight="bold",
    )

    progress_bar = ft.ProgressBar(
        width=420,
        value=0,
        color=JARVIS_GREEN,
        bgcolor="#001a0d",
    )

    hex_border = ft.Container(
        width=560,
        height=560,
        border_radius=20,
        border=ft.Border.all(2, JARVIS_CYAN),
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Image(
                        src=LOGO_PATH,
                        width=480,
                        height=380,
                        fit="contain",
                    ),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        [
                            boot_text,
                            ft.Container(height=10),
                            progress_bar,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(left=20, top=0, right=20, bottom=0),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=20,
        alignment=ft.Alignment(0, 0),
    )

    corner_tl = ft.Container(
        width=30, height=30,
        border=ft.Border(
            top=ft.BorderSide(2, JARVIS_CYAN),
            left=ft.BorderSide(2, JARVIS_CYAN),
        ),
    )
    corner_tr = ft.Container(
        width=30, height=30,
        border=ft.Border(
            top=ft.BorderSide(2, JARVIS_CYAN),
            right=ft.BorderSide(2, JARVIS_CYAN),
        ),
    )
    corner_bl = ft.Container(
        width=30, height=30,
        border=ft.Border(
            bottom=ft.BorderSide(2, JARVIS_CYAN),
            left=ft.BorderSide(2, JARVIS_CYAN),
        ),
    )
    corner_br = ft.Container(
        width=30, height=30,
        border=ft.Border(
            bottom=ft.BorderSide(2, JARVIS_CYAN),
            right=ft.BorderSide(2, JARVIS_CYAN),
        ),
    )

    splash_frame = ft.Stack([
        ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [corner_tl, ft.Container(expand=True), corner_tr],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        [corner_bl, ft.Container(expand=True), corner_br],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                expand=True,
            ),
            expand=True,
        ),
        ft.Container(
            content=hex_border,
            alignment=ft.Alignment(0, 0),
            expand=True,
        ),
    ])

    splash_container = ft.Container(
        content=splash_frame,
        expand=True,
        bgcolor=DARK_BG,
    )

    page.add(splash_container)
    page.update()

    total_steps = len(boot_lines)
    for i, line in enumerate(boot_lines):
        boot_text.value = line
        progress_bar.value = (i + 1) / total_steps
        page.update()
        await asyncio.sleep(0.55)

    await asyncio.sleep(0.4)

    # ─────────────────────────────────────────────────
    #  MAIN HUD
    # ─────────────────────────────────────────────────
    page.padding = 10
    page.controls.clear()

    chat_view = ft.ListView(expand=True, spacing=10, auto_scroll=True, padding=20)
    status_hud = ft.Text("SYSTEM ONLINE", color=JARVIS_CYAN, size=12, weight="bold")
    cpu_text = ft.Text("CPU: 0%", size=12, color=JARVIS_CYAN)
    pwr_text = ft.Text("POWER: 100%", size=12, color=JARVIS_CYAN)

    def bubble(text, is_user=False):
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        text,
                        color="white" if is_user else JARVIS_CYAN,
                        font_family="Consolas",
                        selectable=True,
                        width=450,
                    ),
                    bgcolor="#1a1a1a" if is_user else "#001122",
                    padding=15,
                    border_radius=10,
                    border=ft.Border.all(1, JARVIS_CYAN),
                )
            ],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        )

    async def process_input(cmd_text):
        if not cmd_text:
            return
        cmd_l = cmd_text.lower().strip()
        chat_view.controls.append(bubble(cmd_text, True))
        status_hud.value = "CORE PROCESSING..."
        page.update()

        response = ""
        if "brightness" in cmd_l:
            try:
                level = int(re.search(r'\d+', cmd_l).group())
                sbc.set_brightness(level)
                response = f"Brightness protocol updated to {level}%."
            except:
                response = "Adjusting screen luminance."
        elif "volume" in cmd_l:
            try:
                level = int(re.search(r'\d+', cmd_l).group())
                set_system_volume(level)
                response = f"Audio gain adjusted to {level}%."
            except:
                response = "Calibrating master volume."
        elif "play" in cmd_l:
            song = cmd_l.replace("play", "").strip()
            pywhatkit.playonyt(song)
            response = f"Initiating playback for {song}."
        elif "open" in cmd_l:
            app = cmd_l.replace("open", "").strip()
            try:
                open_app(app, match_closest=True)
                response = f"Launching {app} sub-routine."
            except:
                response = f"Failed to locate {app}."
        else:
            if client:
                try:
                    resp = await asyncio.to_thread(
                        client.chat.completions.create,
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are DAEMON / JARVIS. Be professional and concise."},
                            {"role": "user", "content": cmd_text},
                        ],
                        max_tokens=300,
                    )
                    response = resp.choices[0].message.content
                except:
                    response = "Neural network uplink failed."
            else:
                response = "AI Core offline."

        chat_view.controls.append(bubble(response, False))
        status_hud.value = "IDLE - READY"
        page.update()
        await speak(response)

    jarvis_core_vis = ft.Stack([
        ft.Container(width=300, height=300, border_radius=150,
                     border=ft.Border.all(2, JARVIS_CYAN)),
        ft.Container(width=240, height=240, border_radius=120,
                     border=ft.Border.all(2, JARVIS_BLUE),
                     offset=ft.Offset(30, 30)),
        ft.Container(
            width=180, height=180, border_radius=90,
            border=ft.Border.all(3, JARVIS_CYAN),
            offset=ft.Offset(60, 60),
            content=ft.Column(
                [
                    ft.Image(
                        src=LOGO_PATH,
                        width=120,
                        height=90,
                        fit="contain",
                    ),
                    ft.Text("D.A.E.M.O.N.", size=11, color=JARVIS_GREEN,
                            weight="bold", text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=2,
            ),
            alignment=ft.Alignment(0, 0),
        ),
    ])

    chat_box_hud = ft.Container(
        content=chat_view,
        border=ft.Border.all(1, JARVIS_CYAN),
        border_radius=15,
        bgcolor="#050810",
        width=550,
        height=500,
    )

    async def trigger_listening(e):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            status_hud.value = "LISTENING..."
            page.update()
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=8)
                text = r.recognize_google(audio)
                await process_input(text)
            except:
                status_hud.value = "IDLE - READY"
                page.update()

    async def on_send_click(e):
        val = input_box.value
        input_box.value = ""
        await process_input(val)

    input_box = ft.TextField(
        hint_text="[COMMAND INPUT]", expand=True,
        border_color=JARVIS_CYAN,
        color=JARVIS_CYAN, on_submit=on_send_click,
        fill_color="#001122", filled=True,
    )

    input_row = ft.Row([
        input_box,
        ft.ElevatedButton(
            "🎤",
            on_click=trigger_listening,
            color=JARVIS_CYAN,
            bgcolor="#001122",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, JARVIS_CYAN),
            ),
            height=50,
            width=60,
        ),
    ], width=700)

    page.add(
        ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("DIAGNOSTICS", size=10, color=JARVIS_CYAN, weight="bold"),
                    cpu_text, pwr_text,
                    ft.ProgressBar(width=180, value=0.6, color=JARVIS_CYAN, bgcolor="#002233"),
                    ft.Container(height=16),
                    ft.Text("OPERATIVE", size=9, color=JARVIS_GREEN, weight="bold"),
                    ft.Text("D.A.E.M.O.N.", size=9, color=JARVIS_GREEN),
                ], width=200),
                ft.Container(jarvis_core_vis, padding=20),
                chat_box_hud,
            ], alignment=ft.MainAxisAlignment.CENTER, expand=True),
            ft.Row([
                ft.Container(status_hud, width=200, alignment=ft.Alignment(0, 0)),
                ft.Container(input_row, padding=10),
            ], alignment=ft.MainAxisAlignment.CENTER),
        ], expand=True)
    )

    async def update_stats():
        while True:
            try:
                cpu_text.value = f"CPU: {psutil.cpu_percent()}%"
                battery = psutil.sensors_battery()
                pwr_text.value = f"POWER: {battery.percent if battery else '100'}%"
                page.update()
            except:
                pass
            await asyncio.sleep(3)

    asyncio.create_task(update_stats())
    page.update()
    await speak("Daemon online. All systems nominal.")


if __name__ == "__main__":
    ft.run(main, assets_dir=os.path.dirname(os.path.abspath(__file__)))