import os
import sys
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from gtts import gTTS
from db import init_db, register_user, authenticate_user, get_user_playlists, add_user_playlist, delete_user_playlist
from spotify_player import get_spotify_player_html

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Emotion_onnx-main')))
from util import FaceDetector, HSEmotionRecognizer

det_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Emotion_onnx-main', 'weights', 'detection.onnx'))
emo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Emotion_onnx-main', 'weights', 'emotion.onnx'))
detector = FaceDetector(det_path)
fer = HSEmotionRecognizer(emo_path)

st.set_page_config(
    page_title="Viso Vibe",
    page_icon="🎶",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── Playlists & Metadata (unchanged) ───────────────────────────────────────
zoro_yt = {
    "happy": "PLAzYd4uzG2LrbXNOAugat_pdqF2ueDZ2-",
    "sad":   "PL_DaWb6RFQc1z_KhtsFR3SsOgXXb-E5js",
    "calm":  "PLF0p4MtOouIJl6we_7n5RdWUQ_7EZaCPh",
    "angry": "PLjtEEV8UfHg8U5GoFsyXhSAIiSY3AChNQ"
}

meta_map = {
    "happy": ("Happy Vibes Mix",    "Tamil High Energy"),
    "sad":   ("Soulful Melodies",   "Tamil Heartbreak & Love"),
    "calm":  ("Calm & Breezy Lo-Fi","Tamil Chill Tracks"),
    "angry": ("Rage & Workout BGMs","Tamil Mass Beats")
}

# ─── Mood Palettes ───────────────────────────────────────────────────────────
mood_palettes = {
    "happy": {
        "c1": "255,196,0",   "c2": "255,107,53",  "c3": "255,45,110",
        "accent": "#FFC400", "glow": "#FF6B35",
        "name": "Solar",     "emoji": "☀️",
        "desc": "Radiant & Electric",
        "grad": "linear-gradient(135deg, rgba(255,196,0,0.9) 0%, rgba(255,107,53,0.9) 100%)"
    },
    "sad": {
        "c1": "64,120,255",  "c2": "120,60,220",  "c3": "80,200,255",
        "accent": "#4078FF", "glow": "#7860DC",
        "name": "Cobalt",    "emoji": "🌊",
        "desc": "Deep & Reflective",
        "grad": "linear-gradient(135deg, rgba(64,120,255,0.9) 0%, rgba(120,60,220,0.9) 100%)"
    },
    "calm": {
        "c1": "52,199,145",  "c2": "20,140,180",  "c3": "120,80,220",
        "accent": "#34C791", "glow": "#148CB4",
        "name": "Sage",      "emoji": "🌿",
        "desc": "Serene & Balanced",
        "grad": "linear-gradient(135deg, rgba(52,199,145,0.9) 0%, rgba(20,140,180,0.9) 100%)"
    },
    "angry": {
        "c1": "230,30,30",   "c2": "255,90,0",    "c3": "200,0,90",
        "accent": "#E61E1E", "glow": "#FF5A00",
        "name": "Crimson",   "emoji": "🔥",
        "desc": "Raw & Intense",
        "grad": "linear-gradient(135deg, rgba(230,30,30,0.9) 0%, rgba(255,90,0,0.9) 100%)"
    },
}

# ─── DB Init & Session State ──────────────────────────────────────────────────────────────────────
init_db()

_state_defaults = {
    "luffy_vibe": None,
    "sai": None,
    "rock_artist": None,
    "yt_id": None,
    "naruto": None,
    "user": None,
    "custom_queue": [],
}
for _key, _default in _state_defaults.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default

current_mood = st.session_state.luffy_vibe or "calm"
pal = mood_palettes.get(current_mood, mood_palettes["calm"])
c1, c2, c3 = pal["c1"], pal["c2"], pal["c3"]

# ─── Global CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

html, body, [data-testid="stApp"] {{
    font-family: 'Inter', system-ui, sans-serif;
    background: #06060F;
    overflow-x: hidden;
    min-height: 100vh;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* ── Ambient background ── */
[data-testid="stApp"]::before {{
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
        radial-gradient(ellipse 90% 70% at 10% 10%,  rgba({c1}, 0.14) 0%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 90% 85%,  rgba({c2}, 0.12) 0%, transparent 55%),
        radial-gradient(ellipse 55% 55% at 50% 45%,  rgba({c3}, 0.07) 0%, transparent 60%),
        radial-gradient(ellipse 100% 40% at 50% 100%, rgba({c1}, 0.06) 0%, transparent 50%),
        #06060F;
    transition: background 1.4s cubic-bezier(0.4,0,0.2,1);
    pointer-events: none;
}}

/* Subtle noise texture overlay */
[data-testid="stApp"]::after {{
    content: "";
    position: fixed;
    inset: 0;
    z-index: 1;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    opacity: 0.4;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0 !important; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}
section[data-testid="stSidebar"] {{ display: none; }}

/* ── Layout ── */
.main .block-container {{
    max-width: 460px !important;
    margin: 0 auto !important;
    padding: 0 18px 120px 18px !important;
    position: relative;
    z-index: 2;
}}

/* ── Header ── */
.vv-header {{
    padding: 44px 0 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    position: relative;
}}

.vv-eyebrow {{
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.22);
    margin-bottom: 18px;
}}

/* Logo */
.vv-logo-orbit {{
    position: relative;
    width: 80px;
    height: 80px;
    margin-bottom: 20px;
}}

.vv-orbit-ring {{
    position: absolute;
    border-radius: 50%;
    border: 1px solid transparent;
}}

.vv-orbit-ring-1 {{
    inset: 0;
    border-color: rgba({c1}, 0.35);
    border-top-color: rgba({c1}, 0.9);
    animation: orbitSpin1 3.5s linear infinite;
}}

.vv-orbit-ring-2 {{
    inset: 8px;
    border-color: rgba({c2}, 0.25);
    border-bottom-color: rgba({c2}, 0.7);
    animation: orbitSpin1 2.2s linear infinite reverse;
}}

.vv-orbit-ring-3 {{
    inset: 18px;
    border-color: rgba({c3}, 0.18);
    border-left-color: rgba({c3}, 0.5);
    animation: orbitSpin1 4.8s linear infinite;
}}

.vv-logo-nucleus {{
    position: absolute;
    inset: 26px;
    border-radius: 50%;
    background: {pal["grad"]};
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 0 30px rgba({c1}, 0.5),
        0 0 60px rgba({c1}, 0.2),
        inset 0 1px 0 rgba(255,255,255,0.3);
}}

.vv-nucleus-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255,255,255,0.95);
    box-shadow: 0 0 10px rgba(255,255,255,0.8);
    animation: nucleusPulse 2s ease-in-out infinite;
}}

@keyframes orbitSpin1 {{ to {{ transform: rotate(360deg); }} }}
@keyframes nucleusPulse {{
    0%, 100% {{ transform: scale(1);   opacity: 1; }}
    50%       {{ transform: scale(1.3); opacity: 0.7; }}
}}

/* Brand wordmark */
.vv-wordmark {{
    position: relative;
    margin-bottom: 8px;
}}

.vv-brand-main {{
    font-family: 'Space Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: 8px;
    text-transform: uppercase;
    background: linear-gradient(
        90deg,
        rgba({c1}, 1) 0%,
        rgba(255,255,255,0.95) 40%,
        rgba({c2}, 1) 70%,
        rgba({c3}, 0.9) 100%
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    line-height: 1;
    filter: drop-shadow(0 0 20px rgba({c1}, 0.3));
}}

.vv-tagline {{
    font-size: 9.5px;
    font-weight: 500;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.2);
    text-align: center;
    margin-top: 4px;
}}

/* Header divider */
.vv-rule {{
    width: 100%;
    height: 1px;
    position: relative;
    margin: 28px 0 32px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba({c1}, 0.4) 25%,
        rgba({c2}, 0.4) 50%,
        rgba({c3}, 0.3) 75%,
        transparent 100%
    );
    overflow: visible;
}}

.vv-rule::after {{
    content: "";
    position: absolute;
    top: -1px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, rgba({c1}, 0.9), rgba({c2}, 0.9));
    border-radius: 2px;
    filter: blur(1px);
}}

/* ── Camera Section ── */
.cam-wrap {{
    position: relative;
    margin-bottom: 4px;
}}

.cam-label-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
    padding: 0 2px;
}}

.cam-label {{
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
}}

.cam-status-dot {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba({c1}, 0.7);
    font-weight: 600;
}}

.cam-status-dot::before {{
    content: "";
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: rgba({c1}, 0.9);
    box-shadow: 0 0 8px rgba({c1}, 0.6);
    animation: liveBlink 2s ease-in-out infinite;
    display: inline-block;
}}

@keyframes liveBlink {{
    0%, 100% {{ opacity: 1; }}
    50%       {{ opacity: 0.3; }}
}}

/* Camera input glassmorphism overrides */
div[data-testid="stCameraInput"] {{
    width: 100% !important;
}}

div[data-testid="stCameraInput"] > div {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

div[data-testid="stCameraInput"] video {{
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    width: 100% !important;
    object-fit: cover !important;
    background: #0d0d1c !important;
    box-shadow:
        0 0 0 1px rgba({c1}, 0.08),
        0 20px 60px rgba(0,0,0,0.7),
        inset 0 1px 0 rgba(255,255,255,0.05) !important;
}}

/* Shutter button */
div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"] {{
    all: unset !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 68px !important;
    height: 68px !important;
    border-radius: 50% !important;
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px solid rgba({c1}, 0.3) !important;
    box-shadow:
        0 0 0 8px rgba({c1}, 0.05),
        0 0 30px rgba({c1}, 0.2),
        inset 0 1px 0 rgba(255,255,255,0.1) !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    margin: 18px auto !important;
    position: relative !important;
    overflow: hidden !important;
    backdrop-filter: blur(20px) !important;
    color: transparent !important;
    font-size: 0px !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"]::before {{
    content: "" !important;
    position: absolute !important;
    inset: 6px !important;
    border-radius: 50% !important;
    border: 1px solid rgba({c1}, 0.4) !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"]::after {{
    content: "" !important;
    position: absolute !important;
    width: 26px !important;
    height: 26px !important;
    border-radius: 50% !important;
    background: {pal["grad"]} !important;
    box-shadow: 0 0 18px rgba({c1}, 0.7) !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"]:hover {{
    transform: scale(1.1) !important;
    box-shadow:
        0 0 0 12px rgba({c1}, 0.07),
        0 0 50px rgba({c1}, 0.4),
        inset 0 1px 0 rgba(255,255,255,0.15) !important;
    border-color: rgba({c1}, 0.6) !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"]:active {{
    transform: scale(0.92) !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"] p,
div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"] span,
div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"] div {{
    display: none !important;
}}

/* ── Scan overlay (shown when analyzing) ── */
div[data-testid="stSpinner"] {{
    display: flex;
    align-items: center;
    justify-content: center;
}}

div[data-testid="stSpinner"] > div {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 24px;
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(30px);
    border: 1px solid rgba({c1}, 0.15);
    border-radius: 100px;
}}

div[data-testid="stSpinner"] p {{
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.5) !important;
    font-family: 'Space Mono', monospace !important;
    margin: 0 !important;
}}

/* ── Mood result ── */
.mood-reveal-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    padding: 28px 0 24px;
    animation: fadeUp 0.6s cubic-bezier(0.22,1,0.36,1) both;
}}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.mood-chip-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}}

.mood-chip {{
    padding: 5px 14px;
    border-radius: 100px;
    background: rgba({c1}, 0.1);
    border: 1px solid rgba({c1}, 0.25);
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba({c1}, 0.9);
    backdrop-filter: blur(10px);
}}

.mood-display {{
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}}

.mood-emoji {{
    font-size: 48px;
    margin-bottom: 12px;
    animation: emojiDrop 0.7s cubic-bezier(0.34,1.56,0.64,1) both;
    filter: drop-shadow(0 4px 20px rgba({c1}, 0.4));
}}

@keyframes emojiDrop {{
    from {{ transform: scale(0) rotate(-20deg); opacity: 0; }}
    to   {{ transform: scale(1) rotate(0deg);  opacity: 1; }}
}}

.mood-name-large {{
    font-family: 'Space Mono', monospace;
    font-size: 52px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: {pal["grad"]};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 8px;
    animation: revealSlide 0.6s 0.15s cubic-bezier(0.22,1,0.36,1) both;
    filter: drop-shadow(0 0 30px rgba({c1}, 0.35));
}}

@keyframes revealSlide {{
    from {{ opacity: 0; transform: translateY(12px) scale(0.95); }}
    to   {{ opacity: 1; transform: translateY(0)    scale(1); }}
}}

.mood-sub {{
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.22);
    animation: revealSlide 0.6s 0.25s cubic-bezier(0.22,1,0.36,1) both;
}}

.mood-palette-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 14px;
    padding: 6px 14px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 100px;
    backdrop-filter: blur(20px);
}}

.mpb-swatch {{
    display: flex;
    gap: 3px;
}}

.mpb-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
}}

.mpb-label {{
    font-size: 8.5px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.28);
}}

/* ── Reset button ── */
button[kind="primary"] {{
    border-radius: 14px !important;
    height: 50px !important;
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba({c1}, 0.22) !important;
    color: rgba(255,255,255,0.5) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05) !important;
    width: 100% !important;
}}

button[kind="primary"] p {{
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 3px !important;
    color: rgba(255,255,255,0.5) !important;
    margin: 0 !important;
}}

button[kind="primary"]:hover {{
    background: rgba({c1}, 0.08) !important;
    border-color: rgba({c1}, 0.5) !important;
    color: rgba(255,255,255,0.85) !important;
    box-shadow:
        0 0 30px rgba({c1}, 0.15),
        inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transform: translateY(-1px) !important;
}}

button[kind="primary"]:active {{
    transform: translateY(0) !important;
}}

/* ── Auth & Playlist Management Bar ── */
.user-bar-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    margin-bottom: 22px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 100px;
    backdrop-filter: blur(30px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06);
}}
.user-info-text {{
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.75);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.user-status-pill {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    background: rgba({c1}, 0.15);
    border: 1px solid rgba({c1}, 0.35);
    color: rgba({c1}, 1);
    font-weight: 700;
    font-family: 'Space Mono', monospace;
}}
div[data-testid="stExpander"] {{
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    background: rgba(12, 12, 24, 0.6) !important;
    backdrop-filter: blur(25px) !important;
    margin-bottom: 20px !important;
    overflow: hidden !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
}}
div[data-testid="stExpander"] details summary {{
    padding: 12px 16px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: rgba(255, 255, 255, 0.85) !important;
}}
div[data-baseweb="tab-list"] {{
    background: rgba(255, 255, 255, 0.02) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 6px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}}
button[data-baseweb="tab"] {{
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: rgba(255, 255, 255, 0.5) !important;
    border-radius: 8px !important;
    padding: 6px 14px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    background: rgba({c1}, 0.15) !important;
    color: rgba({c1}, 1) !important;
    font-weight: 700 !important;
}}
div[data-baseweb="input"] input {{
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
}}
div[data-baseweb="input"] input:focus {{
    border-color: rgba({c1}, 0.7) !important;
    box-shadow: 0 0 15px rgba({c1}, 0.25) !important;
}}
.playlist-card-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    margin-bottom: 10px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    transition: all 0.2s ease;
}}
.playlist-card-row:hover {{
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba({c1}, 0.3);
    transform: translateX(2px);
}}
.playlist-card-title {{
    font-size: 12.5px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.95);
    margin-bottom: 2px;
}}
.playlist-card-sub {{
    font-size: 9.5px;
    font-family: 'Space Mono', monospace;
    color: rgba({c1}, 0.8);
    letter-spacing: 1px;
}}
/* ── Error ── */
div[data-testid="stAlert"] {{
    background: rgba(220,30,30,0.06) !important;
    border: 1px solid rgba(220,30,30,0.18) !important;
    border-radius: 14px !important;
    color: rgba(255,120,120,0.75) !important;
    font-size: 11px !important;
    backdrop-filter: blur(20px) !important;
}}

/* ── Section divider ── */
.section-gap {{ height: 20px; }}
.bottom-gap  {{ height: 24px; }}
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="vv-header">
    <div class="vv-eyebrow">Emotion-driven music</div>
    <div class="vv-logo-orbit">
        <div class="vv-orbit-ring vv-orbit-ring-1"></div>
        <div class="vv-orbit-ring vv-orbit-ring-2"></div>
        <div class="vv-orbit-ring vv-orbit-ring-3"></div>
        <div class="vv-logo-nucleus">
            <div class="vv-nucleus-dot"></div>
        </div>
    </div>
    <div class="vv-wordmark">
        <div class="vv-brand-main">VISO VIBE</div>
    </div>
    <div class="vv-tagline">Emotion · Frequency · Music</div>
</div>
<div class="vv-rule"></div>
""", unsafe_allow_html=True)


# ─── User Profile & Playlist Personalization ──────────────────────────────────
user = st.session_state.get('user', None)

if not user:
    with st.expander("👤 Log In / Sign Up (Remember Your Music)", expanded=False):
        tab_login, tab_signup = st.tabs(["Log In", "Create Account"])
        
        with tab_login:
            log_user = st.text_input("Username", key="login_username")
            log_pass = st.text_input("Password", type="password", key="login_password")
            if st.button("Log In", key="btn_login", use_container_width=True):
                auth_res = authenticate_user(log_user, log_pass)
                if auth_res:
                    st.session_state.user = auth_res
                    st.success(f"Welcome back, {auth_res['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
                    
        with tab_signup:
            sign_user = st.text_input("Choose Username", key="signup_username")
            sign_pass = st.text_input("Choose Password", type="password", key="signup_password")
            if st.button("Sign Up", key="btn_signup", use_container_width=True):
                ok, msg = register_user(sign_user, sign_pass)
                if ok:
                    st.success(msg + " You can now log in.")
                else:
                    st.error(msg)
else:
    # Authenticated user bar
    col_u1, col_u2 = st.columns([2.5, 1])
    with col_u1:
        st.markdown(f'''
        <div class="user-bar-container">
            <span class="user-info-text">Active Profile: <span class="user-status-pill">{user['username']}</span></span>
            <span style="font-size: 10px; opacity: 0.5;">Saved Playlists Active</span>
        </div>
        ''', unsafe_allow_html=True)
    with col_u2:
        if st.button("Log Out", key="btn_logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.custom_queue = []
            st.rerun()

    # User Playlist Customization
    with st.expander("🎵 My Custom Mood Playlists", expanded=False):
        st.markdown('<p style="font-size: 11px; opacity: 0.6; margin-bottom: 12px;">Add YouTube playlists or videos for any emotion. The AI will play your uploaded songs when your mood is detected.</p>', unsafe_allow_html=True)
        
        user_playlists = get_user_playlists(user['id'])
        
        selected_mood_tab = st.selectbox(
            "Select Emotion to View / Add",
            ["Happy", "Sad", "Calm", "Angry"],
            index=0
        ).lower()
        
        existing = user_playlists.get(selected_mood_tab, [])
        if existing:
            st.markdown(f"**Your saved playlists for {selected_mood_tab.capitalize()}:**")
            for pl in existing:
                col_pl1, col_pl2 = st.columns([4, 1])
                with col_pl1:
                    st.markdown(f'''
                    <div class="playlist-card-row">
                        <div>
                            <div class="playlist-card-title">{pl['title']}</div>
                            <div class="playlist-card-sub">{pl['artist']} · {pl['source_type'].upper()}</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                with col_pl2:
                    if st.button("🗑️", key=f"del_pl_{pl['id']}"):
                        delete_user_playlist(user['id'], pl['id'])
                        st.rerun()
        else:
            st.info(f"No custom playlists yet for {selected_mood_tab.capitalize()}. Add one below!")

        st.markdown("---")
        st.markdown(f"**Add New Playlist / Song for {selected_mood_tab.capitalize()}**")
        new_title = st.text_input("Playlist / Song Title", placeholder="e.g. My Favorite Chill Mix", key="new_pl_title")
        new_artist = st.text_input("Artist / Description", placeholder="e.g. Lofi Beats / Favorites", key="new_pl_artist")
        new_url = st.text_input("YouTube URL or Playlist ID", placeholder="e.g. https://www.youtube.com/playlist?list=... or video link", key="new_pl_url")
        
        if st.button("Save Playlist for This Emotion", key="save_pl_btn", type="primary"):
            if new_url:
                ok, msg = add_user_playlist(user['id'], selected_mood_tab, new_title, new_url, new_artist)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Please provide a valid YouTube URL or ID.")



# ─── Camera / Detection Flow ─────────────────────────────────────────────────
if st.session_state.luffy_vibe is None:

    st.markdown(f"""
    <div class="cam-label-row">
        <div class="cam-label">Face Capture</div>
        <div class="cam-status-dot">Live</div>
    </div>
    """, unsafe_allow_html=True)

    gojo = st.camera_input("", label_visibility="collapsed")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 5px; margin-bottom: 20px;">
        <span style="font-size: 13px; font-weight: 900; letter-spacing: 4px; text-transform: uppercase; color: rgba(255,255,255,0.6);">TAKE PHOTO</span>
    </div>
    """, unsafe_allow_html=True)

    if gojo is not None:
        with st.spinner("Reading your frequency..."):
            try:
                img_raw = Image.open(gojo).convert("RGB")
                img_arr = np.array(img_raw)

                boxes = detector.detect(img_arr, (640, 640))

                if boxes is not None:
                    box = boxes[0].astype('int32')
                    face_image = img_arr[box[1]:box[3], box[0]:box[2]]
                    pil_image = Image.fromarray(face_image).resize((224, 224))
                    emotion, _ = fer.predict_emotions(np.array(pil_image), logits=False)
                    raw_emotion = emotion.lower()

                    emotion_remap = {
                        "happiness": "happy",
                        "anger":     "angry",
                        "sadness":   "sad",
                        "surprise":  "surprise",
                        "fear":      "fear",
                        "disgust":   "disgust",
                        "neutral":   "neutral",
                    }
                    luffy = emotion_remap.get(raw_emotion, raw_emotion)
                    if luffy not in zoro_yt:
                        luffy = "calm"
                else:
                    luffy = "calm"

                st.session_state.luffy_vibe = luffy

                tts_buf = BytesIO()
                kurama = gTTS(text=f"Vibe detected. You feel {luffy}.", lang="en", slow=False)
                kurama.write_to_fp(tts_buf)
                tts_buf.seek(0)
                st.session_state.naruto = base64.b64encode(tts_buf.read()).decode("utf-8")

                                # Load user custom playlists if authenticated, else use curated defaults
                cur_user = st.session_state.get('user', None)
                user_queue = []
                if cur_user:
                    user_pls = get_user_playlists(cur_user['id']).get(luffy, [])
                    for pl in user_pls:
                        user_queue.append({
                            "title": pl['title'],
                            "artist": pl['artist'],
                            "source_type": pl['source_type'],
                            "source_id": pl['source_id']
                        })

                if user_queue:
                    st.session_state.custom_queue = user_queue
                    st.session_state.sai         = user_queue[0]['title']
                    st.session_state.rock_artist = user_queue[0]['artist']
                    st.session_state.yt_id       = user_queue[0]['source_id']
                else:
                    st.session_state.custom_queue = [{
                        "title": meta_map.get(luffy, meta_map["calm"])[0],
                        "artist": meta_map.get(luffy, meta_map["calm"])[1],
                        "source_type": "playlist",
                        "source_id": zoro_yt.get(luffy, zoro_yt["calm"])
                    }]
                    st.session_state.yt_id       = zoro_yt.get(luffy, zoro_yt["calm"])
                    st.session_state.sai         = meta_map.get(luffy, meta_map["calm"])[0]
                    st.session_state.rock_artist = meta_map.get(luffy, meta_map["calm"])[1]

                st.rerun()

            except Exception:
                st.error("No face detected. Good lighting + face the camera directly.")

else:
    # ─── Mood Result ─────────────────────────────────────────────────────────
    dp = mood_palettes.get(st.session_state.luffy_vibe, mood_palettes["calm"])

    st.markdown(f"""
    <div class="mood-reveal-wrap">
        <div class="mood-chip-row">
            <div class="mood-chip">Detected Mood</div>
        </div>
        <div class="mood-display">
            <div class="mood-emoji">{dp["emoji"]}</div>
            <div class="mood-name-large">{st.session_state.luffy_vibe}</div>
            <div class="mood-sub">{dp["desc"]}</div>
            <div class="mood-palette-badge">
                <div class="mpb-swatch">
                    <div class="mpb-dot" style="background:rgba({dp['c1']},0.9);"></div>
                    <div class="mpb-dot" style="background:rgba({dp['c2']},0.9);"></div>
                    <div class="mpb-dot" style="background:rgba({dp['c3']},0.9);"></div>
                </div>
                <div class="mpb-label">Palette · {dp["name"]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TTS autoplay ──────────────────────────────────────────────────────────
    if st.session_state.naruto:
        components.html(
            f'<audio autoplay src="data:audio/mp3;base64,{st.session_state.naruto}"></audio>',
            height=0, width=0
        )
        st.session_state.naruto = None

    # ─── Music Player Card ────────────────────────────────────────────────────
    if st.session_state.yt_id:
        dc1, dc2, dc3 = dp["c1"], dp["c2"], dp["c3"]
        daccent        = dp["accent"]
        dglow          = dp["glow"]
        dgrad          = dp["grad"]
        dsai           = st.session_state.sai
        dartist        = st.session_state.rock_artist
        dytid          = st.session_state.yt_id

        q_items = st.session_state.get('custom_queue', [])
        if not q_items:
            q_items = [{
                "title": dsai,
                "artist": dartist,
                "source_type": "playlist",
                "source_id": dytid
            }]

        player_html = get_spotify_player_html(
            dc1, dc2, dc3, daccent, dglow, dgrad, dsai, dartist, q_items, 0
        )
        components.html(player_html, height=480)

    st.markdown('<div class="bottom-gap"></div>', unsafe_allow_html=True)

    _, col_reset, _ = st.columns([1, 1.6, 1])
    with col_reset:
        if st.button("↺  New Scan", key="reset_btn", type="primary", use_container_width=True):
            for key in ["luffy_vibe", "sai", "rock_artist", "yt_id", "naruto"]:
                st.session_state[key] = None
            st.session_state["custom_queue"] = []
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# REQUIREMENTS FOR STREAMLIT CLOUD HOSTING
# ──────────────────────────────────────────────────────────────────────────────
#
# requirements.txt
# ────────────────
# streamlit>=1.32.0
# numpy>=1.24.0
# opencv-python-headless>=4.8.0
# Pillow>=10.0.0
# gTTS>=2.5.0
# onnxruntime>=1.17.0
#
# packages.txt  (system-level deps for Streamlit Cloud)
# ─────────────
# libgl1-mesa-glx
# libglib2.0-0
#
# Directory structure expected:
# ├── app.py
# ├── requirements.txt
# ├── packages.txt
# └── Emotion_onnx-main/
#     ├── util.py
#     └── weights/
#         ├── detection.onnx
#         └── emotion.onnx
#
# Streamlit Cloud deploy notes:
#  • Push all files to a public GitHub repo
#  • Set "Main file path" to app.py in Streamlit Cloud settings
#  • No secrets / API keys needed
#  • Free tier supports onnxruntime inference fine
# ──────────────────────────────────────────────────────────────────────────────