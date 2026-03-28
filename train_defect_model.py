"""
Train Defect Detection Model using Transfer Learning (MobileNetV2)
Simple, clean implementation

Run: python train_defect_model.py
"""

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
import os

# Configuration
DATASET_PATH = "data/datasets/NEU-DET/train/images"
MODEL_SAVE_PATH = "models/defect_model.h5"
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 15

# Defect classes
CLASSES = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']

def train_model():
    """Train the defect detection model"""
    
    print("=" * 60)
    print("Training Defect Detection Model")
    print("=" * 60)
    
    # Check dataset exists
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Dataset not found at {DATASET_PATH}")
        print("Please organize your dataset as:")
        print(f"{DATASET_PATH}/")
        print("  ├─ crazing/")
        print("  ├─ inclusion/")
        print("  ├─ patches/")
        print("  ├─ pitted_surface/")
        print("  ├─ rolled-in_scale/")
        print("  └─ scratches/")
        return
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Data augmentation
    print("\n✓ Setting up data augmentation...")
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        validation_split=0.2
    )
    
    # Load training data
    print("✓ Loading training data...")
    train = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        subset="training",
        classes=CLASSES
    )
    
    # Load validation data
    print("✓ Loading validation data...")
    val = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        subset="validation",
        classes=CLASSES
    )
    
    # Build model (Transfer Learning)
    print("\n✓ Building model (MobileNetV2 Transfer Learning)...")
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Add custom top layers
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    output = Dense(6, activation='softmax')(x)  # 6 defect classes
    
    model = Model(inputs=base_model.input, outputs=output)
    
    # Compile
    print("✓ Compiling model...")
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Print model summary
    print("\n" + "=" * 60)
    print("Model Summary:")
    print("=" * 60)
    model.summary()
    
    # Train
    print("\n" + "=" * 60)
    print("Training starting...")
    print("=" * 60)
    
    history = model.fit(
        train,
        validation_data=val,
        epochs=EPOCHS,
        verbose=1
    )
    
    # Save model
    print(f"\n✓ Saving model to {MODEL_SAVE_PATH}...")
    model.save(MODEL_SAVE_PATH)
    
    # Print results
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Final Training Accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"Final Validation Accuracy: {history.history['val_accuracy'][-1]:.4f}")
    print(f"Model saved to: {MODEL_SAVE_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    train_model()
