import cv2
import numpy as np
from tensorflow.keras.models import load_model
import os

# This label mapping is correct for the RAF-DB dataset structure.
emotion_labels = ['Surprise', 'Fear', 'Disgust', 'Happy', 'Sad', 'Anger', 'Neutral']

# Load the model and face detector
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'face_emotion_resnet50.h5')
model = load_model(model_path)
face_cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(face_cascade_path)

def preprocess_face(image_path):
    # Read the original color image
    image = cv2.imread(image_path)
    if image is None:
        return None, "Error loading image"
    
    # Create a grayscale version *only for the face detection* as it's more efficient
    gray_for_detection = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_for_detection, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None, "No face detected"
    
    # Use the largest face found
    (x, y, w, h) = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
    
    # --- THIS IS THE KEY CHANGE ---
    # Crop the face from the original *color* image
    roi_color = image[y:y+h, x:x+w]
    
    # Resize the color ROI to the model's expected input size
    roi_resized = cv2.resize(roi_color, (224, 224))
    
    # Convert color from BGR (OpenCV's default) to RGB (model's expected format)
    roi_rgb = cv2.cvtColor(roi_resized, cv2.COLOR_BGR2RGB)
    
    # Normalize pixel values
    roi_normalized = roi_rgb / 255.0
    
    # Expand dimensions to create a batch of 1
    roi_final = np.expand_dims(roi_normalized, axis=0)
    
    return roi_final, None

def detect_emotion_from_face(image_path):
    roi, error = preprocess_face(image_path)
    if error:
        return error
        
    prediction = model.predict(roi)[0]
    top_prob = np.max(prediction)
    
    if top_prob < 0.4: # Confidence threshold
        return "Uncertain"
        
    emotion_index = np.argmax(prediction)
    detected_emotion = emotion_labels[emotion_index]
    
    return detected_emotion