# Viso Vibe 🎶✨

**Viso Vibe** is a modern, beautifully designed web application that analyzes your facial expression to detect your current mood and automatically plays a matching Spotify playlist to elevate your vibe. 

Originally built as a basic desktop script, it has been completely reimagined into a sleek, web-based experience using Streamlit with advanced glassmorphism CSS, dynamic background animations, and an upgraded architectural backbone.

---

## 🚀 Features

- **Aesthetic UI**: Insane-level custom CSS featuring animated mesh gradients, glassmorphism containers, and vibrant typography.
- **Emotion Analysis**: Leverages `DeepFace` to accurately read your facial expressions directly from your browser.
- **Spotify Integration**: Connects to your Spotify account to seamlessly control playback, mute/unmute, and fetch track artwork.
- **Vibe Announcements**: Uses `pyttsx3` text-to-speech to announce your detected mood and the song that is currently playing.
- **Modular Codebase**: Cleanly separated frontend (`app.py`) and backend logic (`viso_vibe_core.py`).

## 🛠️ Prerequisites

Before you begin, ensure you have the following:
1. **Python 3.8+** installed on your machine.
2. A **Spotify Developer Account**.
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Create an app and get your `Client ID` and `Client Secret`.
   - Add `http://localhost:8888/callback` as a Redirect URI in your Spotify app settings.

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LORDMOSTER/Viso-Vibe.git
   cd Viso-Vibe
   ```

2. **Install the required dependencies:**
   ```bash
   pip install streamlit opencv-python pyttsx3 spotipy deepface pillow
   ```
   *(Note: DeepFace might install additional dependencies like TensorFlow/Keras on first run.)*

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory (or use Streamlit secrets) and add your Spotify credentials:
   ```env
   SPOTIPY_CLIENT_ID=your_client_id_here
   SPOTIPY_CLIENT_SECRET=your_client_secret_here
   SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
   ```

## 🎮 Usage

Run the Streamlit application from your terminal:

```bash
streamlit run app.py
```

- Allow your browser to access the camera.
- Click **Capture your vibe** to snap a photo.
- Watch as Viso Vibe detects your mood and tunes Spotify into the perfect frequency! 🎧

## 📂 Project Structure

- `app.py`: The main Streamlit entry point. Handles the UI layout, camera input, and state management.
- `viso_vibe_core.py`: The backend engine managing DeepFace inference, Spotify OAuth/playback, and TTS.
- `style.css`: Contains all the premium CSS styling (glassmorphism, gradients).
- `README.md`: Project documentation.

## 🤝 Contributing
Feel free to open an issue or submit a pull request if you want to improve the model accuracy, add new vibes, or enhance the UI!

---
*Created with aesthetic in mind.*
