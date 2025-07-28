VibeTune: Multi-Modal Emotion-Based Music Recommender 🎵
 <!-- Replace with your live app URL -->

VibeTune is an intelligent web application that analyzes a user's emotional state through three different modalities—face, voice, and text—and provides personalized music recommendations from Spotify to match their current vibe.

<!-- TODO: Replace with a GIF of your app in action -->

✨ Features
Multi-Modal Emotion Detection:

👤 Face Analysis: Utilizes a ResNet50 deep learning model fine-tuned on the RAF-DB dataset to recognize 7 different emotions from a user's webcam or an uploaded image.

📝 Text Analysis: Employs a DistilRoBERTa-based transformer model from Hugging Face to understand the emotional sentiment of user-provided text.

🎤 Voice Analysis: Leverages a Wav2Vec2 model to detect emotions directly from a user's speech, either from a recorded clip or an uploaded audio file.

Real-Time Spotify Integration: Connects with the Spotify API to fetch a curated list of songs that match the detected emotion, complete with album art and 30-second audio previews.

Interactive & User-Friendly Interface: Built with Streamlit, the application provides a clean, intuitive, and responsive user experience with a professional tabbed layout.

🛠️ Tech Stack
Backend & ML: Python, TensorFlow, Keras, Transformers (Hugging Face), Librosa, Pydub

Frontend: Streamlit

API Integration: Spotipy (Spotify API wrapper)

Core Libraries: OpenCV, Scikit-learn, NumPy, SoundDevice

🚀 Setup and Installation
Follow these steps to set up and run the project on your local machine.

1. Prerequisites
Python 3.9+

Git

FFMPEG: This is a crucial dependency for processing audio files.

Windows: Download from FFMPEG's official site, unzip it, and add the bin folder to your system's PATH environment variable.

macOS (using Homebrew): brew install ffmpeg

Linux (using apt): sudo apt update && sudo apt install ffmpeg

2. Clone the Repository
git clone https://github.com/reeth-07/emotion-music-recommender.git
cd emotion-music-recommender

3. Set Up a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.

# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

4. Install Dependencies
Install all the required Python packages using the requirements.txt file.

pip install -r requirements.txt

5. Set Up Spotify API Credentials
The application requires Spotify API keys to function.

Go to the Spotify Developer Dashboard and create a new application.

Create a file named .env in the root of the project directory.

Add your credentials to the .env file like this:

SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID_HERE'
SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET_HERE'
SPOTIPY_REDIRECT_URI='http://localhost:8501'

In your Spotify Developer Dashboard settings, make sure you add http://localhost:8501 as an authorized Redirect URI.

6. Run the Application
Once everything is set up, you can run the Streamlit app with the following command:

streamlit run main.py

The application should now be running and accessible in your web browser at http://localhost:8501.

📂 Project Structure
├── assets/
│   └── logo.png              # App logo
├── data/
│   └── RAF-DB/               # Dataset for facial emotion model
├── models/
│   └── face_emotion_resnet50.h5 # Trained deep learning model
├── modules/
│   ├── face_emotion.py       # Logic for face analysis
│   ├── recommendation.py     # Logic for Spotify API calls
│   ├── text_emotion.py       # Logic for text analysis
│   ├── voice_emotion.py      # Logic for voice analysis
│   └── voice_record.py       # Helper for audio recording
├── .env                      # Stores secret API keys (not in Git)
├── .gitignore                # Specifies files for Git to ignore
├── main.py                   # Main Streamlit application script
├── README.md                 # You are here!
└── requirements.txt          # List of Python dependencies

🧠 Models Used
Facial Emotion Recognition: ResNet50 pre-trained on ImageNet and fine-tuned on the RAF-DB (Real-world Affective Faces) dataset, achieving 74% validation accuracy.

Text Emotion Recognition: j-hartmann/emotion-english-distilroberta-base, a fine-tuned DistilRoBERTa model from the Hugging Face Hub.

Voice Emotion Recognition: ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition, a fine-tuned Wav2Vec2 model from the Hugging Face Hub.