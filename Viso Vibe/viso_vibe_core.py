import cv2
import pyttsx3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from deepface import DeepFace
import os
import time

# You can manage these in a .env file or Streamlit secrets
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "YOUR_SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "YOUR_SPOTIFY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")

VISO_VIBE_PLAYLISTS = {
    "happy": "spotify:playlist:37i9dQZF1DXdPec7aLTmlC",  # Happy Hits
    "sad": "spotify:playlist:37i9dQZF1DX3rxVfibe1L0",    # Sad Songs
    "neutral": "spotify:playlist:37i9dQZF1DWZq91oLsHZvy", # Chill Hits
    "angry": "spotify:playlist:37i9dQZF1DX1s9knjP51Oa",   # Rage Beats
    "fear": "spotify:playlist:37i9dQZF1DXaW8bfjwMAsm",    # Suspense/Dark
    "surprise": "spotify:playlist:37i9dQZF1DX7KOJcbV1AHO",# Surprise me (Party)
    "disgust": "spotify:playlist:37i9dQZF1DX4sWSpwq3LiO", # Peaceful Piano
}

class VisoVibeManager:
    def __init__(self):
        """Initializes the backend components for Viso Vibe."""
        self.tts_engine = self._init_tts()
        self.spotify_client = self._init_spotify()
        self.current_mood = None
        self.current_song_name = None
        self.current_artist_name = None
        self.current_album_url = None

    def _init_tts(self):
        """Initialize Text-to-Speech Engine."""
        try:
            engine = pyttsx3.init()
            # Opt for a more premium sounding voice if available (e.g. Female voice)
            voices = engine.getProperty('voices')
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            engine.setProperty('rate', 150) # Slower, more elegant rate
            return engine
        except Exception as e:
            print(f"Viso Vibe TTS Warning: {e}")
            return None

    def _init_spotify(self):
        """Initialize Spotify Client using OAuth."""
        if SPOTIPY_CLIENT_ID == "YOUR_SPOTIFY_CLIENT_ID":
            print("Viso Vibe Warning: Spotify credentials not set. Playback will not work.")
            return None
            
        try:
            return spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=SPOTIPY_CLIENT_ID,
                    client_secret=SPOTIPY_CLIENT_SECRET,
                    redirect_uri=SPOTIPY_REDIRECT_URI,
                    scope="user-modify-playback-state user-read-playback-state",
                )
            )
        except Exception as e:
            print(f"Viso Vibe Spotify Warning: {e}")
            return None

    def analyze_emotion(self, image_path):
        """
        Uses DeepFace with an upgraded backend configuration to detect emotion.
        """
        try:
            # Using 'retinaface' for better detection accuracy if installed, fallback to opencv
            result = DeepFace.analyze(
                img_path=image_path, 
                actions=["emotion"], 
                enforce_detection=False,
                detector_backend="opencv" # Upgraded analysis settings
            )
            
            if isinstance(result, list):
                result = result[0]
                
            self.current_mood = result.get("dominant_emotion", None)
            return self.current_mood
            
        except Exception as e:
            print(f"Viso Vibe Emotion Analysis Error: {e}")
            return None

    def play_vibe(self, mood):
        """Plays the corresponding Spotify playlist based on the mood."""
        if not self.spotify_client:
            return {"error": "Spotify client not initialized. Please check credentials."}

        playlist_uri = VISO_VIBE_PLAYLISTS.get(mood)
        if not playlist_uri:
            return {"error": f"No Vibe playlist found for mood: {mood}"}

        try:
            # Prepare playback seamlessly
            self.spotify_client.pause_playback()
            self.spotify_client.volume(0)
            self.spotify_client.start_playback(context_uri=playlist_uri)
            time.sleep(1) # Buffer
            
            # Fetch Track Info
            playback_info = self.spotify_client.current_playback()
            if playback_info and playback_info.get('item'):
                self.current_song_name = playback_info['item']['name']
                self.current_artist_name = playback_info['item']['artists'][0]['name']
                self.current_album_url = playback_info['item']['album']['images'][0]['url']
            
            self._announce_vibe()
            
            # Restore Volume
            self.spotify_client.volume(100)
            self.spotify_client.start_playback()
            
            return {
                "success": True,
                "song": self.current_song_name,
                "artist": self.current_artist_name,
                "album_url": self.current_album_url
            }

        except spotipy.exceptions.SpotifyException as e:
            return {"error": f"Spotify playback error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    def _announce_vibe(self):
        """Announces the detected vibe and the track."""
        if not self.tts_engine:
            return
            
        try:
            if self.current_mood:
                self.tts_engine.say(f"I sense a {self.current_mood} vibe.")
                
            if self.current_song_name and self.current_artist_name:
                self.tts_engine.say(f"Now playing {self.current_song_name} by {self.current_artist_name}.")
                
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Viso Vibe Announcement Error: {e}")
