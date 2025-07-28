# import os
# import sys
# import torch
# import librosa
# import librosa.effects
# import sounddevice as sd
# import soundfile as sf
# from pydub import AudioSegment
# from transformers import logging
# from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
# from tqdm import tqdm

# # 🔇 Suppress tqdm progress bar (avoids WinError 6 on Windows terminals)
# tqdm.__init__ = lambda self, *args, **kwargs: None

# # 🛑 Suppress warnings
# logging.set_verbosity_error()

# # 🎧 Set ffmpeg path for pydub
# AudioSegment.converter = r"C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

# # 🔁 Load feature extractor and model only once
# try:
#     extractor = AutoFeatureExtractor.from_pretrained(
#         "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition", trust_remote_code=True
#     )
#     model = AutoModelForAudioClassification.from_pretrained(
#         "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition", trust_remote_code=True
#     )
# except Exception as e:
#     print(f"❌ Error loading model: {e}")
#     extractor, model = None, None

# # 🔤 Emotion categories from model
# EMOTION_LABELS = ['angry', 'calm', 'happy', 'sad', 'fearful', 'disgust', 'surprised', 'neutral']

# # 🔁 Convert to proper 16kHz mono wav if needed
# def convert_to_wav_if_needed(audio_path):
#     ext = os.path.splitext(audio_path)[-1].lower()
#     wav_path = audio_path.replace(ext, ".wav")

#     audio = AudioSegment.from_file(audio_path)
#     audio = audio.set_frame_rate(16000).set_channels(1)
#     audio.export(wav_path, format="wav")
#     return wav_path

# # 🔍 Voice Emotion Detection Function
# def detect_emotion_from_voice(audio_path):
#     if model is None or extractor is None:
#         return "❌ Model not loaded"

#     try:
#         audio_path = convert_to_wav_if_needed(audio_path)
#         speech, sr = librosa.load(audio_path, sr=16000)
#         speech, _ = librosa.effects.trim(speech)

#         inputs = extractor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
#         with torch.no_grad():
#             logits = model(**inputs).logits

#         predicted_class_id = torch.argmax(logits).item()
#         return EMOTION_LABELS[predicted_class_id]
#     except Exception as e:
#         return f"❌ Error during emotion detection: {str(e)}"


# modules/voice_emotion.py
import os
import torch
import librosa
import librosa.effects
from pydub import AudioSegment
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
import streamlit as st

# --- Improvement: Cache the model for efficiency ---
@st.cache_resource
def load_voice_model():
    """Loads the voice model and caches it."""
    try:
        extractor = AutoFeatureExtractor.from_pretrained("ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition", trust_remote_code=True)
        model = AutoModelForAudioClassification.from_pretrained("ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition", trust_remote_code=True)
        return extractor, model
    except Exception as e:
        st.error(f"Error loading voice model: {e}")
        return None, None

extractor, model = load_voice_model()

# --- Improvement: Standardized labels ---
EMOTION_LABELS = ['Angry', 'Calm', 'Happy', 'Sad', 'Fearful', 'Disgust', 'Surprised', 'Neutral']

# --- Improvement: Removed hardcoded FFMPEG path ---
# NOTE: User must have FFMPEG installed and in their system PATH.

def convert_to_wav_if_needed(audio_path):
    # This function is good, but improved error handling
    ext = os.path.splitext(audio_path)[-1].lower()
    if ext == ".wav":
        return audio_path
    
    wav_path = audio_path.replace(ext, ".wav")
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_path, format="wav")
        return wav_path
    except Exception as e:
        st.error(f"Error converting audio. Please ensure FFMPEG is installed and in your system's PATH. Error: {e}")
        return None

def detect_emotion_from_voice(audio_path):
    if model is None or extractor is None:
        return "Voice model not loaded."

    try:
        wav_path = convert_to_wav_if_needed(audio_path)
        if not wav_path: return "Audio conversion failed."

        speech, sr = librosa.load(wav_path, sr=16000)
        
        # Trim leading/trailing silence
        speech, _ = librosa.effects.trim(speech, top_db=25)
        if speech.size == 0: return "Audio is silent."

        inputs = extractor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits

        predicted_class_id = torch.argmax(logits).item()
        return EMOTION_LABELS[predicted_class_id]
    
    except Exception as e:
        return f"Error during voice analysis: {str(e)}"
