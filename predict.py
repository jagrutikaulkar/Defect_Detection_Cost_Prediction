"""
Prediction Module
Load and use both CNN and Cost models
"""

import tensorflow as tf
import joblib
import numpy as np
import cv2
import os
from pathlib import Path
from preprocess import preprocess_image

# Get the absolute path to the models directory
BASE_DIR = Path(__file__).parent.resolve()
MODELS_DIR = BASE_DIR / 'models'

# Defect classes (7 classes: 6 defects + normal)
DEFECT_CLASSES = [
    'crazing',
    'inclusion',
    'patches',
    'pitted_surface',
    'rolled-in_scale',
    'scratches',
    'normal'
]

# Load models (global)
class Predictor:
    def __init__(self):
        self.cnn_model = None
        self.cost_model = None
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        
        defect_model_path = MODELS_DIR / "defect_model.h5"
        cost_model_path = MODELS_DIR / "cost_model.pkl"
        
        # Load CNN model for defect detection
        try:
            if defect_model_path.exists():
                print(f"✓ Loading defect detection model from {defect_model_path}...")
                self.cnn_model = tf.keras.models.load_model(str(defect_model_path))
                print("✓ Defect model loaded successfully")
            else:
                print(f"❌ Defect model not found at {defect_model_path}")
                self.cnn_model = None
        except Exception as e:
            print(f"❌ Error loading defect model: {str(e)}")
            self.cnn_model = None
        
        # Load cost regression model
        try:
            if cost_model_path.exists():
                print(f"✓ Loading cost prediction model from {cost_model_path}...")
                self.cost_model = joblib.load(str(cost_model_path))
                print("✓ Cost model loaded successfully")
            else:
                print(f"❌ Cost model not found at {cost_model_path}")
                self.cost_model = None
        except Exception as e:
            print(f"❌ Error loading cost model: {str(e)}")
            self.cost_model = None
        
        # Report final status
        if self.cnn_model and self.cost_model:
            print("=" * 50)
            print("✓ Both models loaded successfully!")
            print("=" * 50)
        else:
            print("=" * 50)
            print("❌ WARNING: Some models failed to load!")
            print("=" * 50)
    
    def detect_defect_region(self, image_path):
        """
        Detect bounding box of defect region using image processing
        Returns list of bounding boxes: [x, y, w, h]
        """
        try:
            raw_img = cv2.imread(image_path)
            if raw_img is None:
                return []
            
            # Resize to original size for analysis
            h, w = raw_img.shape[:2]
            
            # Convert to grayscale and detect edges
            gray = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding for defect detection
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            bounding_boxes = []
            for contour in contours:
                area = cv2.contourArea(contour)
                # Filter by area to avoid noise
                if 100 < area < (w * h * 0.5):
                    x, y, cw, ch = cv2.boundingRect(contour)
                    # Normalize coordinates to percentage
                    bounding_boxes.append({
                        'x': round((x / w) * 100, 2),
                        'y': round((y / h) * 100, 2),
                        'width': round((cw / w) * 100, 2),
                        'height': round((ch / h) * 100, 2),
                        'pixel_x': int(x),
                        'pixel_y': int(y),
                        'pixel_width': int(cw),
                        'pixel_height': int(ch)
                    })
            
            return bounding_boxes[:5]  # Return top 5 bounding boxes
        except:
            return []
    
    def predict(self, image_path, machine_time=2.0, labor_cost=300.0, material_cost=200.0):
        """
        End-to-end prediction with production parameters
        
        Args:
            image_path: Path to image file
            machine_time: Time on production line (hours)
            labor_cost: Labor cost per hour (₹)
            material_cost: Material cost (₹)
        
        Returns:
            Dictionary with defect_type, confidence, predicted_cost, bounding_boxes
        """
        
        if self.cnn_model is None or self.cost_model is None:
            return {
                'error': 'Models not loaded',
                'defect_type': None,
                'confidence': 0,
                'predicted_cost': 0,
                'status': 'error',
                'bounding_boxes': []
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
            
            # Detect bounding boxes for defect region
            bounding_boxes = self.detect_defect_region(image_path)
            
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
                'bounding_boxes': bounding_boxes,
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
                'predicted_cost': 0,
                'bounding_boxes': []
            }

# Global predictor instance
predictor = None

def get_predictor():
    """Get or create predictor instance"""
    global predictor
    if predictor is None:
        predictor = Predictor()
    return predictor

# Update DEFECT_CLASSES export for compatibility
__all__ = ['get_predictor', 'DEFECT_CLASSES', 'Predictor']

if __name__ == "__main__":
    # Test
    p = get_predictor()
    print("\n" + "=" * 60)
    print("Predictor loaded and ready!")
    print("=" * 60)
