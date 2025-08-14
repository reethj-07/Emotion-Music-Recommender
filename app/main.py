# main.py
import sys
import os
from dotenv import load_dotenv
import streamlit as st
import tempfile
import gc
import psutil

# --- Memory Management Setup ---
@st.cache_resource(max_entries=1)
def load_emotion_models():
    """Load all emotion detection models with memory limits"""
    # Your models will be loaded here with caching
    return True

# Emergency memory management
if 'memory_cleanup_counter' not in st.session_state:
    st.session_state.memory_cleanup_counter = 0

st.session_state.memory_cleanup_counter += 1

# Force cleanup every 3 interactions
if st.session_state.memory_cleanup_counter % 3 == 0:
    gc.collect()
    st.cache_data.clear()

# Memory cleanup function
def cleanup_memory():
    """Force garbage collection to free memory"""
    gc.collect()
    st.cache_data.clear()

# --- UI Configuration & Custom CSS ---
st.set_page_config(
    page_title="VibeTune 🎵",
    page_icon="🎧",
    layout="wide"
)

# Load environment variables and set path
load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import your improved modules
from modules.face_emotion import detect_emotion_from_face
from modules.text_emotion import get_bert_emotion
from modules.voice_record import record_audio
from modules.voice_emotion import detect_emotion_from_voice
from modules.recommendation import get_tracks_for_emotion

# Custom CSS for a more polished look
st.markdown("""
<style>
/* Your existing CSS styles here */
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("assets/logo.png", width=100)
    st.title("VibeTune")
    st.markdown("---")
    st.markdown("Detect your emotion and get personalized music recommendations from Spotify.")
    st.markdown("---")
    
    # Memory management controls
    if st.button("🧹 Clear Memory", help="Free up memory to prevent resource limits"):
        cleanup_memory()
        st.success("Memory cleared!")
        st.rerun()
    
    # Show current memory status
    try:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        st.caption(f"Memory Usage: {memory_mb:.1f} MB")
        if memory_mb > 2000:  # Warning if approaching 2GB limit
            st.warning("⚠️ High memory usage detected")
    except:
        pass
    
    # Test Spotify connection
    if st.button("🔗 Test Spotify Connection"):
        from modules.recommendation import sp
        if sp:
            try:
                result = sp.search(q="test", limit=1)
                st.success("✅ Spotify connection working!")
            except Exception as e:
                st.error(f"❌ Spotify error: {e}")
        else:
            st.error("❌ Spotify not connected")
    
    st.markdown("---")
    st.markdown("Built by [Reeth Jain](https://github.com/reethj-07) 👨💻")
    st.markdown("🔗 [GitHub Repo](https://github.com/reethj-07/emotion-music-recommender)")

# --- Header ---
st.title("Emotion-Based Music Recommender")
st.markdown("Select a detection method below to analyze your emotion and discover music that matches your vibe.")
st.markdown("---")

# Initialize session state
if "detected_emotions" not in st.session_state:
    st.session_state.detected_emotions = {}
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None

# --- Tabs for Emotion Detection ---
tab1, tab2, tab3 = st.tabs(["👤 Face Emotion", "📝 Text Emotion", "🎤 Voice Emotion"])

with tab1:
    st.subheader("Analyze Emotion From Your Face")
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        face_option = st.radio("Choose face input:", ["Upload Image", "Use Webcam"], key="face_radio", horizontal=True)
        image_file = None
        
        if face_option == "Upload Image":
            uploaded_img = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="face_uploader")
            if uploaded_img: 
                image_file = uploaded_img
        else:
            camera_image = st.camera_input("Take a picture", key="face_camera")
            if camera_image: 
                image_file = camera_image
    
    with col2:
        if image_file:
            st.image(image_file, caption="Your Image", width=250)
            
            if st.button("Analyze Face", key="face_analyze"):
                with st.spinner("Analyzing..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(image_file.getvalue())
                        emotion = detect_emotion_from_face(tmp.name)
                        
                        if emotion and emotion not in ["No face detected", "Uncertain", "Error"]:
                            st.success(f"Emotion Detected: **{emotion}**")
                            st.session_state.detected_emotions["Face"] = emotion
                        else:
                            st.warning(emotion)
                    
                    # Clean up temporary file and memory
                    os.unlink(tmp.name)
                    gc.collect()

with tab2:
    st.subheader("Analyze Emotion From Your Words")
    user_input = st.text_area("How are you feeling today?", key="text_input", height=200, 
                             placeholder="e.g., I had a wonderful day and I'm feeling on top of the world!")
    
    if st.button("Analyze Text", key="text_button"):
        if user_input.strip():
            with st.spinner("Analyzing..."):
                emotion = get_bert_emotion(user_input)
                
                if emotion and emotion not in ["Uncertain", "Error"]:
                    st.success(f"Emotion Detected: **{emotion}**")
                    st.session_state.detected_emotions["Text"] = emotion
                else:
                    st.warning(emotion)
                
                # Clean up memory after text processing
                gc.collect()
        else:
            st.warning("Please enter some text.")

with tab3:
    st.subheader("Analyze Emotion From Your Voice")
    voice_option = st.radio("Choose voice input:", ["Upload Audio", "Record Audio"], key="voice_radio", horizontal=True)
    audio_file_to_process = None
    
    if voice_option == "Upload Audio":
        uploaded_audio = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"], key="voice_uploader")
        if uploaded_audio:
            st.audio(uploaded_audio)
            audio_file_to_process = uploaded_audio
    else:  # Record Audio
        if st.button("Start Recording (5s)", key="voice_record"):
            with st.spinner("Recording..."):
                st.session_state.audio_path = record_audio(duration=5)
                st.success("Recording complete!")
        
        # Always check session state for a recorded file
        if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
            st.write("Your last recording:")
            with open(st.session_state.audio_path, "rb") as f:
                st.audio(f.read())
            audio_file_to_process = st.session_state.audio_path
    
    if audio_file_to_process:
        if st.button("Analyze Voice", key="voice_analyze"):
            with st.spinner("Analyzing..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    if isinstance(audio_file_to_process, str):  # Path from recording
                        with open(audio_file_to_process, 'rb') as f: 
                            tmp.write(f.read())
                    else:  # Uploaded file object
                        tmp.write(audio_file_to_process.getvalue())
                    
                    emotion = detect_emotion_from_voice(tmp.name)
                    
                    if emotion and "Error" not in emotion and "failed" not in emotion and "silent" not in emotion:
                        st.success(f"Emotion Detected: **{emotion}**")
                        st.session_state.detected_emotions["Voice"] = emotion
                    else:
                        st.warning(emotion)
                
                # Clean up temporary file and memory
                os.unlink(tmp.name)
                gc.collect()

# --- Music Recommendations ---
st.markdown("---")
st.header("🎵 Your VibeTune Playlist")

if not st.session_state.detected_emotions:
    st.info("Analyze your emotion using one of the methods above to get music recommendations.")
else:
    st.markdown("Choose an emotion source to generate your playlist:")
    emotion_options = {f"{source} ({emotion})": emotion for source, emotion in st.session_state.detected_emotions.items()}
    selected_option = st.radio("Source:", list(emotion_options.keys()), horizontal=True)
    selected_emotion = emotion_options[selected_option]
    
    if st.button(f"Get Songs for '{selected_emotion}'", key="get_songs"):
        with st.spinner(f"Finding songs on Spotify for a '{selected_emotion}' vibe..."):
            tracks = get_tracks_for_emotion(selected_emotion)
            
            if not tracks:
                st.warning("Could not find any songs. This might be due to regional availability or a temporary Spotify issue. Please try a different emotion.")
            else:
                st.success(f"Here are some tracks for you:")
                
                for track in tracks:
                    col_art, col_info, col_player = st.columns([1, 4, 2])
                    
                    with col_art:
                        if track['album_art_url']:
                            st.image(track['album_art_url'], width=100)
                    
                    with col_info:
                        st.markdown(f"**{track['name']}**")
                        st.markdown(f"*{track['artist']}*")
                        st.markdown(f"[Open on Spotify]({track['spotify_url']})")
                    
                    if track['preview_url']:
                        with col_player:
                            st.audio(track['preview_url'], format="audio/mp3")
                    
                    st.divider()
            
            # Clean up memory after song recommendations
            gc.collect()
