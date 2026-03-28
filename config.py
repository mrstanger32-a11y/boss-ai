import os
from dotenv import load_dotenv
import pygame

# --- LOADING ENVIRONMENT ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- J.A.R.V.I.S. COLOR PALETTE (Futuristic HUD) ---
JARVIS_CYAN = "#00ffff"    # Main UI Glow
JARVIS_BLUE = "#0088ff"    # Secondary Accents
JARVIS_TEAL = "#00ccff"    # Progress Bars
JARVIS_RED = "#ff4444"     # Alert/Error States
DARK_BG = "#020406"        # Deep Space Black (Better for contrast)

# --- SYSTEM INITIALIZATION ---
pygame.mixer.init()

# --- AUDIO SETTINGS ---
# Agar tum chaho toh voice speed yahan se control kar sakte ho
VOICE_MODEL = "en-IN-NeerjaNeural"