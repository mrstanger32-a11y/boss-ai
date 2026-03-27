import asyncio, os, re, uuid, time
import flet as ft
import speech_recognition as sr
import edge_tts, pygame, pywhatkit, psutil, wmi
from AppOpener import open as open_app
from groq import Groq
from dotenv import load_dotenv # Naya import

# --- ⚙️ CONFIG ---
# .env file se variables load karega
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Ab key safe hai

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

# Check ki key mil rahi hai ya nahi
if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY nahi mili! .env file check karo.")
    client = None
else:
    client = Groq(api_key=GROQ_API_KEY)

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

# --- 🕹️ ACTION ENGINE ---
async def process_command(cmd, chat_text, page):
    if not cmd or client is None: return
    cmd_l = cmd.lower().strip()
    chat_text.value = "..."
    page.update()

    answer = ""
    try:
        resp = await asyncio.to_thread(client.chat.completions.create,
               model="llama-3.3-70b-versatile",
               messages=[{"role": "system", "content": "Short answers only."}, {"role": "user", "content": cmd}],
               max_tokens=40)
        answer = resp.choices[0].message.content
    except: answer = "Connection error, Sir."

    chat_text.value = answer
    page.update()
    asyncio.create_task(speak(answer, chat_text, page))

# --- 🖼️ UI INTERFACE ---
async def main(page: ft.Page):
    page.title = "BOSS AI"
    page.bgcolor = "#0a0a0a"
    page.window_width = 450
    page.window_height = 700
    page.window_always_on_top = True
    page.padding = 10

    ai_char = ft.Image(
        src="ai_girl.gif",
        width=400,
        fit="contain",
    )

    chat_text = ft.Text(
        "I'm listening, Sir.",
        size=20,
        color="#00d4ff",
        weight="bold",
        text_align="center"
    )

    user_input = ft.TextField(
        hint_text="Type here...",
        border_radius=15,
        bgcolor="#1a1a1a",
        border_color="#00d4ff",
        color="white",
        expand=True,
        on_submit=lambda e: asyncio.create_task(on_send())
    )

    async def on_send():
        text = user_input.value
        if text:
            user_input.value = ""
            chat_text.value = f"You: {text}"
            page.update()
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