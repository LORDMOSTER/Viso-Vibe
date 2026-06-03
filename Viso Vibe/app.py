import streamlit as st
import os
from PIL import Image
from viso_vibe_core import VisoVibeManager

# Configure Streamlit page
st.set_page_config(
    page_title="Viso Vibe",
    page_icon="🎶",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load Premium CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css("style.css")
except FileNotFoundError:
    pass

# Initialize Backend Manager in Session State
if 'vibe_manager' not in st.session_state:
    st.session_state.vibe_manager = VisoVibeManager()

# UI Layout
st.markdown("<h1 class='main-title'>Viso Vibe</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Discover your aesthetic. Feel the rhythm. 🎧</p>", unsafe_allow_html=True)

# Main Glass Container
st.markdown("<div class='glass-container'>", unsafe_allow_html=True)

# Camera Input
captured_image = st.camera_input("Capture your vibe")

if captured_image is not None:
    # Save the captured image temporarily for DeepFace
    temp_image_path = "temp_capture.jpg"
    with open(temp_image_path, "wb") as f:
        f.write(captured_image.getbuffer())

    with st.spinner("Analyzing your aesthetic... 🌌"):
        # Analyze Emotion
        mood = st.session_state.vibe_manager.analyze_emotion(temp_image_path)
        
        if mood:
            st.success(f"Vibe Detected: **{mood.capitalize()}** ⚡")
            
            # Play Vibe Music
            with st.spinner("Tuning into your frequency... 🎵"):
                result = st.session_state.vibe_manager.play_vibe(mood)
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.markdown("<hr style='border:1px solid rgba(255,20,147,0.3);'>", unsafe_allow_html=True)
                    
                    # Display Song Info beautifully
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if result.get("album_url"):
                            st.image(result["album_url"], use_container_width=True)
                    
                    with col2:
                        st.markdown(f"### Now Playing")
                        st.markdown(f"**{result['song']}**")
                        st.markdown(f"*{result['artist']}*")
        else:
            st.error("Could not capture a clear vibe. Please try again.")
            
    # Clean up temp image
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 0.8rem; margin-top: 50px;'>"
    "Viso Vibe by yourusername. Connect your Spotify to ride the wave."
    "</p>",
    unsafe_allow_html=True
)
