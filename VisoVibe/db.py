import os
import sqlite3
import hashlib
import streamlit as st

# Check if Turso credentials are provided via Streamlit secrets or environment variables
def get_turso_credentials():
    url = None
    token = None
    
    # 1. Check Streamlit secrets (Streamlit Cloud or .streamlit/secrets.toml)
    try:
        if hasattr(st, "secrets"):
            if "TURSO_DATABASE_URL" in st.secrets:
                url = st.secrets["TURSO_DATABASE_URL"]
            if "TURSO_AUTH_TOKEN" in st.secrets:
                token = st.secrets["TURSO_AUTH_TOKEN"]
    except Exception:
        pass

    # 2. Check environment variables as fallback
    if not url:
        url = os.environ.get("TURSO_DATABASE_URL")
    if not token:
        token = os.environ.get("TURSO_AUTH_TOKEN")
        
    return url, token

TURSO_URL, TURSO_TOKEN = get_turso_credentials()
USE_TURSO = bool(TURSO_URL and TURSO_TOKEN)
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "visovibe.db")

# Helper to execute queries on either Turso (libsql_client) or local sqlite3
def _get_turso_client():
    import libsql_client
    # Convert libsql:// protocol to https:// if required by HTTP client
    t_url = TURSO_URL
    if t_url.startswith("libsql://"):
        t_url = t_url.replace("libsql://", "https://")
    return libsql_client.create_client_sync(url=t_url, auth_token=TURSO_TOKEN)

def _execute(query, params=None):
    """
    Executes a query and returns (rows, last_insert_rowid).
    Works seamlessly across Turso cloud and local SQLite.
    """
    params = params or ()
    if USE_TURSO:
        client = _get_turso_client()
        res = client.execute(query, params)
        rows = [list(r) for r in res.rows]
        last_id = res.last_insert_rowid
        client.close()
        return rows, last_id
    else:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return rows, last_id

def init_db():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            emotion TEXT NOT NULL,
            title TEXT NOT NULL,
            source_type TEXT NOT NULL DEFAULT 'playlist',
            source_id TEXT NOT NULL,
            artist TEXT DEFAULT 'Curated',
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, emotion, source_id)
        )
        """
    ]
    for q in queries:
        _execute(q)

def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(username: str, password: str):
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password cannot be empty."

    try:
        # Check if username exists
        existing_rows, _ = _execute("SELECT id FROM users WHERE username = ?", (username,))
        if existing_rows:
            return False, "Username already exists."

        _, user_id = _execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, _hash_pw(password))
        )

        # Seed default default playlists for this user
        default_playlists = [
            ("happy", "Happy Vibes Mix", "PLAzYd4uzG2LrbXNOAugat_pdqF2ueDZ2-", "High Energy Vibes"),
            ("sad", "Soulful Melodies", "PL_DaWb6RFQc1z_KhtsFR3SsOgXXb-E5js", "Heartbreak & Chill"),
            ("calm", "Calm & Breezy Lo-Fi", "PLF0p4MtOouIJl6we_7n5RdWUQ_7EZaCPh", "Chill Tracks"),
            ("angry", "Rage & Workout BGMs", "PLjtEEV8UfHg8U5GoFsyXhSAIiSY3AChNQ", "Intense Mass Beats")
        ]
        for emo, title, pid, art in default_playlists:
            _execute("""
                INSERT OR IGNORE INTO user_playlists (user_id, emotion, title, source_type, source_id, artist)
                VALUES (?, ?, ?, 'playlist', ?, ?)
            """, (user_id, emo, title, pid, art))

        return True, "Registered successfully!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def authenticate_user(username: str, password: str):
    username = username.strip().lower()
    try:
        rows, _ = _execute(
            "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
            (username, _hash_pw(password))
        )
        if rows:
            return {"id": rows[0][0], "username": rows[0][1]}
    except Exception:
        pass
    return None

def get_user_playlists(user_id: int):
    result = {"happy": [], "sad": [], "calm": [], "angry": []}
    try:
        rows, _ = _execute("""
            SELECT id, emotion, title, source_type, source_id, artist, is_active
            FROM user_playlists WHERE user_id = ? ORDER BY id DESC
        """, (user_id,))
        for r in rows:
            emo = str(r[1]).lower()
            if emo in result:
                result[emo].append({
                    "id": r[0],
                    "emotion": emo,
                    "title": r[2],
                    "source_type": r[3],
                    "source_id": r[4],
                    "artist": r[5],
                    "is_active": r[6]
                })
    except Exception:
        pass
    return result

def add_user_playlist(user_id: int, emotion: str, title: str, source_input: str, artist: str = "My Playlist"):
    emotion = emotion.strip().lower()
    title = title.strip() or "Custom Playlist"
    artist = artist.strip() or "Custom Artist"
    source_input = source_input.strip()

    source_id = source_input
    source_type = "playlist"
    
    if "list=" in source_input:
        source_id = source_input.split("list=")[1].split("&")[0]
        source_type = "playlist"
    elif "v=" in source_input:
        source_id = source_input.split("v=")[1].split("&")[0]
        source_type = "video"
    elif "youtu.be/" in source_input:
        source_id = source_input.split("youtu.be/")[1].split("?")[0]
        source_type = "video"

    try:
        _execute("""
            INSERT INTO user_playlists (user_id, emotion, title, source_type, source_id, artist)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, emotion, title, source_type, source_id, artist))
        return True, "Playlist added successfully!"
    except Exception as e:
        return False, f"Error saving playlist: {str(e)}"

def delete_user_playlist(user_id: int, playlist_id: int):
    try:
        _execute("DELETE FROM user_playlists WHERE id = ? AND user_id = ?", (playlist_id, user_id))
        return True
    except Exception:
        return False
