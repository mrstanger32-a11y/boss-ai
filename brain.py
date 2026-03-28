import asyncio, uuid, os, edge_tts, pygame
import speech_recognition as sr
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

async def ask_ai(cmd):
    if not client: return "API missing"
    try:
        resp = await asyncio.to_thread(client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": cmd}],
            max_tokens=100)
        return resp.choices[0].message.content
    except: return "[ERROR]: AI not responding."

async def speak(text):
    file = f"temp_{uuid.uuid4().hex[:5]}.mp3"
    try:
        tts = edge_tts.Communicate(text, "en-IN-NeerjaNeural")
        await tts.save(file)
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
        os.remove(file)
    except: pass

async def listen_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=5)
            return r.recognize_google(audio)
        except:
            return None