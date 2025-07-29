# modules/recommendation.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import random
import streamlit as st

# --- FINAL DIAGNOSTIC VERSION ---
@st.cache_resource
def connect_to_spotify():
    """
    Creates and caches a Spotipy client with extensive logging for debugging.
    """
    print("--- DEBUG: Attempting to connect to Spotify ---")
    
    # Print the environment variables to ensure they are loaded
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    
    print(f"DEBUG: Client ID loaded: {'Yes' if client_id else 'No'}")
    print(f"DEBUG: Redirect URI loaded: {redirect_uri}")

    try:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=None,
            cache_handler=spotipy.MemoryCacheHandler()
        )
        print("DEBUG: SpotifyOAuth manager created successfully.")
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        print("DEBUG: spotipy.Spotify client created successfully.")
        
        # Test the connection by fetching user info
        user = sp.me()
        print(f"DEBUG: Successfully authenticated as Spotify user: {user['display_name']}")
        
        return sp

    except Exception as e:
        print(f"--- FATAL ERROR in connect_to_spotify ---: {e}")
        st.error("A critical error occurred during Spotify authentication. Check the logs for details.")
        return None
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
                    album_art_url = None
                    if item['album']['images']:
                        album_art_url = item['album']['images'][1]['url']

                    all_tracks.append({
                        'name': item['name'],
                        'artist': item['artists'][0]['name'],
                        'preview_url': item.get('preview_url'),
                        'spotify_url': item['external_urls']['spotify'],
                        'album_art_url': album_art_url
                    })
            
            if len(all_tracks) >= limit:
                break
                
    except Exception as e:
        st.error(f"Could not connect to Spotify.")
        print(f"SPOTIFY API ERROR: {e}")
        return []

    random.shuffle(all_tracks)
    return all_tracks[:limit]
