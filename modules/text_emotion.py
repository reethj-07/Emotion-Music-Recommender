# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# from transformers import pipeline

# # Use VADER to get quick positive/negative/neutral sentiment
# # Use BERT to classify deeper emotions (joy, anger, sadness, etc.)

# #| Tool                     | Purpose                                          |
# #| ------------------------ | ------------------------------------------------ |
# #| **VADER**                | Quick lexicon-based polarity (positive/negative) |
# #| **BERT (DistilRoBERTa)** | Emotion label (joy, anger, sadness, etc.)        |


# # Load VADER sentiment analyzer
# vader_analyzer = SentimentIntensityAnalyzer()

# # Load BERT emotion classification model from Hugging Face
# bert_emotion_classifier = pipeline("text-classification", 
#                                    model="j-hartmann/emotion-english-distilroberta-base", 
#                                    return_all_scores=True)

# def get_vader_sentiment(text: str) -> str:
#     scores = vader_analyzer.polarity_scores(text)
#     compound = scores['compound']
    
#     if compound >= 0.05:
#         return "Positive"
#     elif compound <= -0.05:
#         return "Negative"
#     else:
#         return "Neutral"

# def get_bert_emotion(text: str) -> str:
#     result = bert_emotion_classifier(text)[0]
#     top = max(result, key=lambda x: x['score'])
#     return f"{top['label']} ({round(top['score'] * 100, 2)}%)"


# modules/text_emotion.py
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import streamlit as st

# --- Improvement: Cache the model so it only loads once ---
@st.cache_resource
def load_bert_model():
    """Loads the BERT model and caches it."""
    return pipeline("text-classification", 
                    model="j-hartmann/emotion-english-distilroberta-base")

# Load analyzers
vader_analyzer = SentimentIntensityAnalyzer()
bert_emotion_classifier = load_bert_model()

# --- Improvement: Map BERT outputs to a standard set of emotions ---
EMOTION_MAP = {
    "joy": "Happy",
    "sadness": "Sad",
    "anger": "Angry",
    "fear": "Fearful",
    "surprise": "Surprised",
    "disgust": "Disgust",
    "neutral": "Neutral"
}

def get_vader_sentiment(text: str) -> str:
    # This function is good as is.
    scores = vader_analyzer.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def get_bert_emotion(text: str) -> str:
    """Returns only the standardized emotion label now."""
    if not text.strip():
        return "Uncertain"
    
    try:
        results = bert_emotion_classifier(text, top_k=1)
        top_label = results[0]['label']
        # Use the mapping to return a consistent, capitalized emotion label
        return EMOTION_MAP.get(top_label, "Neutral")
    except Exception as e:
        st.error(f"Text analysis failed: {e}")
        return "Error"
