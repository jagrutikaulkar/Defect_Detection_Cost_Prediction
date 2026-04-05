"""
Prediction Module
Load and use both CNN and Cost models
"""

import tensorflow as tf
import joblib
import numpy as np
import cv2
import os
import warnings
from pathlib import Path
from preprocess import preprocess_image

# Suppress scikit-learn version warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Get the absolute path to the models directory
BASE_DIR = Path(__file__).parent.resolve()
MODELS_DIR = BASE_DIR / 'models'

# Defect classes (including normal for clean steel)
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
    
    def find_defect_region(self, image_path):
        """Find bounding box of defect region using improved morphological operations"""
        try:
            raw_img = cv2.imread(image_path)
            if raw_img is None:
                return None
            
            raw_img = cv2.resize(raw_img, (224, 224))
            gray = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
            
            # Create binary mask (defect = white pixels)
            thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)[1]
            
            # Apply morphological operations for better segmentation
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)  # Close small holes
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)   # Remove noise
            
            # Find contours of defect
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                return None
            
            # Get bounding box of largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Add padding (10% of dimensions)
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(224 - x, w + padding * 2)
            h = min(224 - y, h + padding * 2)
            
            return {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
        except:
            return None
    
    def predict(self, image_path, machine_time=2.0, labor_cost=300.0, material_cost=200.0, energy_consumption=100.0, production_volume=1000):
        """
        End-to-end prediction with production parameters
        
        Args:
            image_path: Path to image file
            machine_time: Time on production line (hours)
            labor_cost: Labor cost per hour (₹)
            material_cost: Material cost (₹)
            energy_consumption: Energy consumption (kWh) - default 100
            production_volume: Production batch volume (units) - default 1000
        
        Returns:
            Dictionary with defect_type, confidence, predicted_cost, bounding_box
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
            is_normal = (defect_type == 'normal')
            
            # Find defect region (bounding box) - do this first
            bounding_box = None if is_normal else self.find_defect_region(image_path)
            
            # Feature extraction for cost prediction
            raw_img = cv2.imread(image_path)
            raw_img = cv2.resize(raw_img, (224, 224))
            
            # Calculate defect area with improved segmentation
            if bounding_box and not is_normal:
                # Calculate area percentage from bounding box dimensions
                bbox_area = bounding_box['width'] * bounding_box['height']
                total_area = 224 * 224  # Image is resized to 224x224
                defect_area = (bbox_area / total_area) * 100
            else:
                # Fallback: use morphologically processed binary image
                gray = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)[1]
                # Apply morphological operations
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                defect_pixels = np.sum(thresh == 255)
                total_pixels = thresh.size
                defect_area = (defect_pixels / total_pixels) * 100
            
            # ✅ IMPROVED: Determine severity based on DEFECT AREA (industry standard)
            # This is more accurate than confidence-based severity
            if defect_area < 5:
                severity = 1  # LOW - minimal defect
            elif defect_area < 20:
                severity = 2  # MEDIUM - moderate defect
            else:
                severity = 3  # HIGH - severe defect
            
            # ✅ IMPROVED: Cost prediction features - Enhanced with 8 features
            # Create dataframe with proper feature names to avoid sklearn warnings
            import pandas as pd
            features_df = pd.DataFrame([[
                defect_id,              # defect_type (0-5)
                defect_area,            # defect_area (%)
                severity,               # severity (1-3: low/medium/high)
                machine_time,           # machine_time (hours)
                labor_cost,             # labor_cost_rate (₹/hour)
                material_cost,          # material_cost (₹)
                energy_consumption,     # energy_consumption (kWh)
                production_volume       # production_volume (units)
            ]], columns=[
                'defect_type', 'defect_area', 'severity',
                'machine_time', 'labor_cost_rate', 'material_cost',
                'energy_consumption', 'production_volume'
            ])
            
            # Predict cost
            if self.cost_model is None:
                print("⚠️  WARNING: Cost model is None, using default cost 0")
                predicted_cost = 0.0
            else:
                try:
                    predicted_cost = float(self.cost_model.predict(features_df)[0])
                except Exception as cost_error:
                    print(f"⚠️  Cost prediction failed: {cost_error}")
                    print(f"   Features: {features_df.values}")
                    predicted_cost = 0.0
            
            response = {
                'status': 'success',
                'defect_type': defect_type,
                'confidence': round(confidence, 2),
                'is_normal': is_normal,
                'all_predictions': {
                    DEFECT_CLASSES[i]: float(pred[0][i] * 100)
                    for i in range(len(DEFECT_CLASSES))
                }
            }
            
            # Only add defect-related fields if not normal
            if not is_normal:
                response.update({
                    'severity': ['low', 'medium', 'high'][severity - 1],
                    'defect_area': round(defect_area, 2),
                    'predicted_cost': round(predicted_cost, 2),
                    'bounding_box': bounding_box
                })
            
            return response
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'defect_type': None,
                'confidence': 0,
                'predicted_cost': 0
            }
    
    def process_video(self, video_path, output_folder, confidence_threshold=70, frame_interval=5, artificial_delay_ms=0):
        """
        Process video and detect defects in each frame
        
        Args:
            video_path: Path to video file
            output_folder: Folder to save detected frames
            confidence_threshold: Minimum confidence to save frame (0-100)
            frame_interval: Process every nth frame (e.g., 5 = process every 5th frame)
            artificial_delay_ms: Add artificial delay in milliseconds per frame (0 = no delay)
        
        Returns:
            Dictionary with analysis results
        """
        import time
        
        if self.cnn_model is None:
            return {
                'status': 'error',
                'error': 'CNN model not loaded'
            }
        
        try:
            start_time = time.time()
            
            # Create output folder
            os.makedirs(output_folder, exist_ok=True)
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {
                    'status': 'error',
                    'error': 'Could not open video file'
                }
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            frames_analyzed = 0
            defects_detected = 0
            detected_frames = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Process every nth frame
                if frame_count % frame_interval != 0:
                    continue
                
                frames_analyzed += 1
                frame_start_time = time.time()
                
                # Resize frame to model input size
                frame_resized = cv2.resize(frame, (224, 224))
                
                # Preprocess
                img_normalized = frame_resized.astype('float32') / 255.0
                img_batch = np.expand_dims(img_normalized, axis=0)
                
                # Predict
                pred = self.cnn_model.predict(img_batch, verbose=0)
                defect_id = np.argmax(pred[0])
                defect_type = DEFECT_CLASSES[defect_id]
                confidence = float(pred[0][defect_id] * 100)
                
                # Calculate processing time for this frame
                frame_processing_time = (time.time() - frame_start_time) * 1000  # Convert to milliseconds
                
                # Add artificial delay if specified (for testing/simulation)
                if artificial_delay_ms > 0:
                    time.sleep(artificial_delay_ms / 1000.0)  # Convert ms to seconds
                    frame_processing_time = (time.time() - frame_start_time) * 1000  # Recalculate with delay
                
                # Check if defect and confidence > threshold
                if defect_type != 'normal' and confidence >= confidence_threshold:
                    defects_detected += 1
                    
                    # Save frame
                    frame_filename = f'frame_{frame_count}_{defect_type}_{confidence:.1f}.jpg'
                    frame_path = os.path.join(output_folder, frame_filename)
                    cv2.imwrite(frame_path, frame)
                    
                    # Store frame info with timing
                    detected_frames.append({
                        'frame_number': frame_count,
                        'timestamp': round(frame_count / fps, 2),  # seconds
                        'filename': frame_filename,
                        'defect_type': defect_type,
                        'confidence': round(confidence, 2),
                        'processing_time_ms': round(frame_processing_time, 2)  # milliseconds
                    })
            
            cap.release()
            
            total_processing_time = (time.time() - start_time) * 1000  # milliseconds
            avg_time_per_frame = total_processing_time / frames_analyzed if frames_analyzed > 0 else 0
            avg_time_per_detection = total_processing_time / defects_detected if defects_detected > 0 else 0
            
            return {
                'status': 'success',
                'total_frames': total_frames,
                'frames_analyzed': frames_analyzed,
                'defects_detected': defects_detected,
                'detected_frames': detected_frames,
                'video_duration': round(total_frames / fps, 2),
                'fps': fps,
                'total_processing_time_ms': round(total_processing_time, 2),
                'avg_time_per_frame_ms': round(avg_time_per_frame, 2),
                'avg_time_per_detection_ms': round(avg_time_per_detection, 2)
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
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
