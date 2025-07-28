import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import os

# --- Model & Data Parameters ---
IMG_SIZE = 224
BATCH_SIZE = 32
NUM_CLASSES = 7 # RAF-DB has 7 emotion classes

def get_data_generators(train_dir, val_dir):
    # Set up data augmentation for the training data
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=25,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.15,
        zoom_range=0.15,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # IMPORTANT: The validation generator should ONLY rescale the images, not augment them.
    val_datagen = ImageDataGenerator(rescale=1./255)

    train_gen = train_datagen.flow_from_directory(
        train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        color_mode='rgb',
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )

    val_gen = val_datagen.flow_from_directory(
        val_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        color_mode='rgb',
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    return train_gen, val_gen

def build_model():
    # Load ResNet50 pre-trained on ImageNet, without the final classification layer
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    
    # Freeze the layers of the base model so they aren't trained initially
    base_model.trainable = False
    
    # Add custom layers on top for our specific task
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x) # Use dropout for regularization to prevent overfitting
    x = Dense(512, activation='relu')(x)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    return model, base_model

if __name__ == "__main__":
    # --- CRITICAL: Update these paths to point to your new dataset ---
    train_dir = "data/RAF-DB/train"
    val_dir = "data/RAF-DB/test" # Note: The validation folder is named 'test'
    
    train_gen, val_gen = get_data_generators(train_dir, val_dir)

    model, base_model = build_model()
    
    # Compile the model for the first stage of training
    model.compile(optimizer=Adam(learning_rate=1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    # Compute class weights to help the model handle the imbalanced dataset
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_gen.classes),
        y=train_gen.classes
    )
    class_weights_dict = dict(enumerate(class_weights))
    print(f"\nCalculated Class Weights: {class_weights_dict}\n")

    # --- BEST PRACTICE: Use Callbacks for smarter training ---
    # Save only the best model found during training
    checkpoint = ModelCheckpoint("models/face_emotion_resnet50.h5", monitor='val_accuracy', save_best_only=True, mode='max', verbose=1)
    # Stop training early if the model stops improving
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1)
    # Reduce learning rate when performance plateaus
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=1e-6, verbose=1)
    
    # --- Stage 1: Initial Training (only top layers) ---
    print("--- Starting Initial Training of Top Layers ---")
    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=30, # Train for more epochs, EarlyStopping will handle the rest
        class_weight=class_weights_dict,
        callbacks=[checkpoint, early_stopping, reduce_lr]
    )

    # --- Stage 2: Fine-Tuning (unfreeze all layers with a tiny learning rate) ---
    print("\n--- Starting Fine-Tuning of Full Model ---")
    base_model.trainable = True # Unfreeze the entire base model

    # Re-compile with a very low learning rate for fine-tuning
    model.compile(optimizer=Adam(learning_rate=1e-5), loss='categorical_crossentropy', metrics=['accuracy'])
    
    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=20, # Fine-tune for additional epochs
        class_weight=class_weights_dict,
        callbacks=[checkpoint, early_stopping, reduce_lr]
    )

    print("\nTraining complete. Best model saved as 'face_emotion_resnet50.h5' in the 'models' directory.")

