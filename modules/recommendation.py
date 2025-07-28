# modules/recommendation.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import random
import streamlit as st

@st.cache_resource
def connect_to_spotify():
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=None
    )
    return spotipy.Spotify(auth_manager=auth_manager)

sp = connect_to_spotify()

emotion_queries = {
    "Happy": ["upbeat", "feel good", "party", "happy vibes", "energetic"],
    "Sad": ["sad", "melancholy", "emotional", "heartbreak", "sad bollywood"],
    "Angry": ["aggressive", "rage", "hard beats", "angry rap", "workout"],
    "Calm": ["chill", "ambient", "instrumental calm", "lo-fi chillhop", "meditation"],
    "Fearful": ["dark ambient", "eerie", "haunting", "mystery", "suspenseful"],
    "Disgust": ["intense", "chaotic", "experimental hip hop", "noise rock"],
    "Surprised": ["unexpected", "creative", "experimental pop", "synth surprise"],
    "Neutral": ["chill study beats", "lo-fi", "background music", "easy listening"]
}

def get_tracks_for_emotion(emotion, limit=10):
    queries = emotion_queries.get(emotion, ["mood"])
    random.shuffle(queries)
    
    all_tracks = []
    
    try:
        market = sp.me()['country']
    except Exception:
        market = "IN"

    try:
        for query in queries:
            results = sp.search(q=query, type='track', limit=50, market=market)
            tracks_from_query = results['tracks']['items']
            
            for item in tracks_from_query:
                if item:
                    # --- KEY CHANGE: Get the album art URL ---
                    album_art_url = None
                    if item['album']['images']:
                        album_art_url = item['album']['images'][1]['url'] # Get 300x300 image

                    all_tracks.append({
                        'name': item['name'],
                        'artist': item['artists'][0]['name'],
                        'preview_url': item.get('preview_url'),
                        'spotify_url': item['external_urls']['spotify'],
                        'album_art_url': album_art_url # Add it to the dictionary
                    })
            
            if len(all_tracks) >= limit:
                break
                
    except Exception as e:
        st.error(f"Could not connect to Spotify.")
        print(f"SPOTIFY API ERROR: {e}")
        return []

    random.shuffle(all_tracks)
    return all_tracks[:limit]