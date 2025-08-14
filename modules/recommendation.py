# modules/recommendation.py
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import random
import streamlit as st

@st.cache_resource(max_entries=1, ttl=3600)  # Cache for 1 hour, max 1 instance
def connect_to_spotify():
    """Connect to Spotify using Client Credentials (no user auth required)"""
    try:
        # Try to get credentials from Streamlit secrets first, then environment
        try:
            client_id = st.secrets["SPOTIPY_CLIENT_ID"]
            client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"]
        except:
            client_id = os.getenv("SPOTIPY_CLIENT_ID")
            client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            st.error("❌ Spotify credentials not found. Please check your secrets configuration.")
            return None
            
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test the connection
        sp.search(q="test", limit=1)
        return sp
        
    except Exception as e:
        st.error(f"❌ Spotify connection failed: {e}")
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
    if sp is None:
        st.error("❌ Spotify connection not available. Please check your API credentials.")
        return []
    
    queries = emotion_queries.get(emotion, ["mood"])
    random.shuffle(queries)
    all_tracks = []
    
    try:
        market = "US"  # Default market
        
        for query in queries:
            results = sp.search(q=query, type='track', limit=50, market=market)
            tracks_from_query = results['tracks']['items']
            
            for item in tracks_from_query:
                if item:
                    # Get album art URL
                    album_art_url = None
                    if item['album']['images']:
                        album_art_url = item['album']['images'][1]['url'] if len(item['album']['images']) > 1 else item['album']['images'][0]['url']
                    
                    all_tracks.append({
                        'name': item['name'],
                        'artist': item['artists'][0]['name'],
                        'preview_url': item.get('preview_url'),
                        'spotify_url': item['external_urls']['spotify'],
                        'album_art_url': album_art_url
                    })
                    
                    if len(all_tracks) >= limit:
                        break
            
            if len(all_tracks) >= limit:
                break
                
    except Exception as e:
        st.error(f"❌ Could not fetch songs from Spotify: {e}")
        return []
    
    random.shuffle(all_tracks)
    return all_tracks[:limit]
