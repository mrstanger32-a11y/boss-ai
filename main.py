import asyncio, os, re, uuid, time, webbrowser
import flet as ft
import speech_recognition as sr
import edge_tts, pygame, pywhatkit, psutil, wmi
from AppOpener import open as open_app
from groq import Groq
from dotenv import load_dotenv

# --- Nayi Libraries for System Control ---
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- ⚙️ CONFIG ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY nahi mili! .env file check karo.")
    client = None
else:
    client = Groq(api_key=GROQ_API_KEY)

# --- 🔊 VOLUME HELPER FUNCTION ---
def set_system_volume(level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return True
    except: return False

# --- 🎤 VOICE ENGINE ---
async def speak(text: str, chat_text, page):
    voice_file = f"temp_{uuid.uuid4().hex[:5]}.mp3"
    try:
        communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural", rate="+22%")
        await communicate.save(voice_file)
        pygame.mixer.music.load(voice_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
    except: pass
    pygame.mixer.music.unload()
    if os.path.exists(voice_file):
        try: os.remove(voice_file)
        except: pass

# --- 🕹️ ACTION ENGINE (SYSTEM + WEB + APPS + AI) ---
async def process_command(cmd, chat_text, page):
    if not cmd: return
    cmd_l = cmd.lower().strip()
    chat_text.value = f"Analyzing: {cmd_l}"
    page.update()

    # ☀️ 1. Brightness Control (e.g., "set brightness to 50")
    if "brightness" in cmd_l:
        try:
            level = int(re.search(r'\d+', cmd_l).group())
            sbc.set_brightness(level)
            chat_text.value = f"Brightness set to {level}%"
        except:
            if "increase" in cmd_l: sbc.set_brightness(min(100, sbc.get_brightness()[0] + 20))
            else: sbc.set_brightness(max(0, sbc.get_brightness()[0] - 20))
            chat_text.value = "Brightness adjusted, Sir."
        page.update()
        return

    # 🔊 2. Volume Control (e.g., "set volume to 70")
    elif "volume" in cmd_l:
        try:
            level = int(re.search(r'\d+', cmd_l).group())
            set_system_volume(level)
            chat_text.value = f"Volume set to {level}%"
        except:
            chat_text.value = "Adjusting volume, Sir."
        page.update()
        return

    # 📺 3. YouTube Control (Purana Feature - Safe)
    elif "play" in cmd_l:
        song = cmd_l.replace("play", "").strip()
        chat_text.value = f"Playing {song} on YouTube..."
        page.update()
        pywhatkit.playonyt(song)
        return

    # 🖥️ 4. Open Apps (Purana Feature - Safe)
    elif "open" in cmd_l:
        app_name = cmd_l.replace("open", "").strip()
        chat_text.value = f"Opening {app_name}..."
        page.update()
        try:
            open_app(app_name, match_closest=True)
            return
        except:
            chat_text.value = f"Could not open {app_name}."
            page.update()

    # 🔍 5. Search on Google/Edge (Purana Feature - Safe)
    elif "search" in cmd_l or "google" in cmd_l:
        query = cmd_l.replace("search", "").replace("google", "").strip()
        chat_text.value = f"Searching for {query}..."
        page.update()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return

    # 🤖 6. AI Chat Logic (Purana Feature - Safe)
    if client:
        try:
            resp = await asyncio.to_thread(client.chat.completions.create,
                   model="llama-3.3-70b-versatile",
                   messages=[{"role": "system", "content": "Short answers only."}, {"role": "user", "content": cmd}],
                   max_tokens=40)
            answer = resp.choices[0].message.content
        except: answer = "Connection error, Sir."
    else:
        answer = "API Key missing, Sir."

    chat_text.value = answer
    page.update()
    asyncio.create_task(speak(answer, chat_text, page))

# --- 🖼️ UI INTERFACE (Same) ---
async def main(page: ft.Page):
    page.title = "BOSS AI"
    page.bgcolor = "#0a0a0a"
    page.window_width = 450
    page.window_height = 700
    page.window_always_on_top = True
    page.padding = 10

    ai_char = ft.Image(src="ai_girl.gif", width=400, fit="contain")
    chat_text = ft.Text("I'm listening, Sir.", size=20, color="#00d4ff", weight="bold", text_align="center")
    user_input = ft.TextField(
        hint_text="Type or Speak...", border_radius=15, bgcolor="#1a1a1a",
        border_color="#00d4ff", color="white", expand=True,
        on_submit=lambda e: asyncio.create_task(on_send())
    )

    async def on_send():
        text = user_input.value
        if text:
            user_input.value = ""
            await process_command(text, chat_text, page)

    async def start_listening(e):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            chat_text.value = "Listening..."
            page.update()
            try:
                audio = r.listen(source, timeout=3, phrase_time_limit=5)
                text = r.recognize_google(audio)
                await process_command(text, chat_text, page)
            except:
                chat_text.value = "Awaiting command..."
                page.update()

    page.add(
        ft.Column([
            ft.Container(content=ai_char, alignment=ft.Alignment(0, 0), expand=True),
            ft.Container(content=chat_text, padding=20, alignment=ft.Alignment(0, 0)),
            ft.Container(
                content=ft.Row([
                    user_input,
                    ft.FloatingActionButton(icon=ft.Icons.MIC, on_click=start_listening, bgcolor="#00d4ff")
                ]),
                padding=10,
            )
        ], expand=True)
    )
    page.update()

if __name__ == "__main__":
    ft.run(main)