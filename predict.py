"""
Prediction Module
Load and use both CNN and Cost models
"""

import tensorflow as tf
import joblib
import numpy as np
import cv2
import os
from preprocess import preprocess_image

# Defect classes
DEFECT_CLASSES = [
    'crazing',
    'inclusion',
    'patches',
    'pitted_surface',
    'rolled-in_scale',
    'scratches'
]

# Load models (global)
class Predictor:
    def __init__(self):
        self.cnn_model = None
        self.cost_model = None
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        
        # Load CNN model for defect detection
        if os.path.exists("models/defect_model.h5"):
            print("✓ Loading defect detection model...")
            self.cnn_model = tf.keras.models.load_model("models/defect_model.h5")
        else:
            print("❌ Defect model not found at models/defect_model.h5")
            print("   Run: python train_defect_model.py")
        
        # Load cost regression model
        if os.path.exists("models/cost_model.pkl"):
            print("✓ Loading cost prediction model...")
            self.cost_model = joblib.load("models/cost_model.pkl")
        else:
            print("❌ Cost model not found at models/cost_model.pkl")
            print("   Run: python train_cost_model.py")
    
    def predict(self, image_path, machine_time=2.0, labor_cost=300.0, material_cost=200.0):
        """
        End-to-end prediction with production parameters
        
        Args:
            image_path: Path to image file
            machine_time: Time on production line (hours)
            labor_cost: Labor cost per hour (₹)
            material_cost: Material cost (₹)
        
        Returns:
            Dictionary with defect_type, confidence, predicted_cost
        """
        
        if self.cnn_model is None or self.cost_model is None:
            return {
                'error': 'Models not loaded',
                'defect_type': None,
                'confidence': 0,
                'predicted_cost': 0,
                'status': 'error'
            }
        
        try:
            # Load and preprocess image
            img = preprocess_image(image_path, size=(224, 224))
            img_batch = np.expand_dims(img, axis=0)
            
            # Defect detection
            pred = self.cnn_model.predict(img_batch, verbose=0)
            defect_id = np.argmax(pred[0])
            defect_type = DEFECT_CLASSES[defect_id]
            confidence = float(pred[0][defect_id] * 100)
            
            # Feature extraction for cost prediction
            raw_img = cv2.imread(image_path)
            raw_img = cv2.resize(raw_img, (224, 224))
            
            gray = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)[1]
            defect_pixels = np.sum(thresh == 255)
            total_pixels = thresh.size
            defect_area = (defect_pixels / total_pixels) * 100
            
            # Determine severity based on confidence
            if confidence > 85:
                severity = 3  # High
            elif confidence > 70:
                severity = 2  # Medium
            else:
                severity = 1  # Low
            
            # Cost prediction features - using provided parameters
            features = np.array([[
                defect_id,           # defect_type
                defect_area,         # defect_area
                severity,            # severity
                machine_time,        # machine_time (from user input)
                labor_cost,          # labor_cost (from user input)
                material_cost        # material_cost (from user input)
            ]])
            
            predicted_cost = float(self.cost_model.predict(features)[0])
            
            return {
                'status': 'success',
                'defect_type': defect_type,
                'confidence': round(confidence, 2),
                'severity': ['low', 'medium', 'high'][severity - 1],
                'defect_area': round(defect_area, 2),
                'predicted_cost': round(predicted_cost, 2),
                'all_predictions': {
                    DEFECT_CLASSES[i]: float(pred[0][i] * 100)
                    for i in range(len(DEFECT_CLASSES))
                }
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'defect_type': None,
                'confidence': 0,
                'predicted_cost': 0
            }

# Global predictor instance
predictor = None

def get_predictor():
    """Get or create predictor instance"""
    global predictor
    if predictor is None:
        predictor = Predictor()
    return predictor

if __name__ == "__main__":
    # Test
    p = get_predictor()
    print("\n" + "=" * 60)
    print("Predictor loaded and ready!")
    print("=" * 60)
