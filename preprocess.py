"""
Simple Image Preprocessing for Defect Detection
"""

import cv2
import numpy as np

def preprocess_image(path, size=(224, 224)):
    """
    Load and preprocess image
    
    Args:
        path: Image file path
        size: Target size (width, height)
    
    Returns:
        Preprocessed image as numpy array
    """
    # Read image
    img = cv2.imread(path)
    
    if img is None:
        raise ValueError(f"Could not load image: {path}")
    
    # Resize to target size
    img = cv2.resize(img, size)
    
    # Normalize pixel values to 0-1
    img = img / 255.0
    
    return np.array(img)

def defect_area_percentage(image):
    """
    Calculate defect area as percentage
    
    Used for cost prediction
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Binary threshold
    thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)[1]
    
    # Calculate defect pixels
    defect_pixels = np.sum(thresh == 255)
    total_pixels = thresh.size
    
    # Area percentage
    area = (defect_pixels / total_pixels) * 100
    
    return area
