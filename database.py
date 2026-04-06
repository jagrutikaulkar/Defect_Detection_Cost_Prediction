"""
MongoDB Database Connection & Operations
Replace JSON file-based storage with MongoDB Atlas
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection String
MONGODB_URI = "mongodb+srv://jagrutikaulkar0_db_user:BQhtOOiB086fuxp1@cluster0.bcohx26.mongodb.net/defect_detection?retryWrites=true&w=majority"

# Initialize MongoDB Client (Non-blocking initialization)
db = None
try:
    print("⏳ Attempting MongoDB connection (non-blocking)...")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000, 
                         socketTimeoutMS=2000, retryWrites=False)
    db = client['defect_detection']
    # Don't call ping() - it blocks. Connection test happens on first use.
    print("✓ MongoDB client initialized (connection will be tested on first use)")
except Exception as e:
    print(f"⚠ MongoDB client initialization warning: {str(e)[:80]}")
    db = None

# Collections
detections_collection = db['detections'] if db is not None else None
analytics_collection = db['analytics'] if db is not None else None
users_collection = db['users'] if db is not None else None

# Create indexes for fast queries
if db is not None:
    try:
        detections_collection.create_index('username')
        detections_collection.create_index('created_at')
        detections_collection.create_index('defect_type')
        analytics_collection.create_index('username')
        analytics_collection.create_index('date')
        users_collection.create_index('username', unique=True)
        print("✓ Database indexes created")
    except Exception as e:
        print(f"⚠ Index creation warning: {e}")

def save_detection(username, detection_data):
    """Save detection to MongoDB"""
    if db is None:
        print("⚠ MongoDB unavailable, using JSON fallback")
        return False
    
    try:
        detection_data['username'] = username
        detection_data['created_at'] = datetime.now().isoformat() if 'created_at' not in detection_data else detection_data['created_at']
        result = detections_collection.insert_one(detection_data)
        return True
    except Exception as e:
        print(f"❌ Error saving detection: {e}")
        return False

def get_user_detections(username, limit=None):
    """Get all detections for a user"""
    if db is None:
        return []
    
    try:
        query = {'username': username}
        cursor = detections_collection.find(query).sort('created_at', -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    except Exception as e:
        print(f"❌ Error fetching detections: {e}")
        return []

def get_image_detections(username):
    """Get only image detections (filter out videos)"""
    if db is None:
        return []
    
    try:
        query = {
            'username': username,
            '$or': [
                {'type': {'$ne': 'video'}},
                {'type': {'$exists': False}}
            ]
        }
        cursor = detections_collection.find(query).sort('created_at', -1)
        return list(cursor)
    except Exception as e:
        print(f"❌ Error fetching image detections: {e}")
        return []

def get_video_detections(username):
    """Get only video detections"""
    if db is None:
        return []
    
    try:
        query = {'username': username, 'type': 'video'}
        cursor = detections_collection.find(query).sort('created_at', -1)
        return list(cursor)
    except Exception as e:
        print(f"❌ Error fetching video detections: {e}")
        return []

def delete_user_detections(username):
    """Delete all detections for a user"""
    if db is None:
        return False
    
    try:
        result = detections_collection.delete_many({'username': username})
        print(f"✓ Deleted {result.deleted_count} detections for user {username}")
        return True
    except Exception as e:
        print(f"❌ Error deleting detections: {e}")
        return False

def get_analytics(username, time_period='all'):
    """Get analytics for a user (aggregated data)"""
    if db is None:
        return {}
    
    try:
        # Get all detections for user
        detections = get_user_detections(username)
        
        if not detections:
            return {
                'total_inspections': 0,
                'defects_found': 0,
                'total_cost_loss': 0.0,
                'defect_distribution': {},
                'severity_distribution': {},
                'average_confidence': 0.0
            }
        
        # Calculate analytics
        total_inspections = len(detections)
        defects_found = sum(1 for d in detections if d.get('type') != 'video')
        total_cost_loss = sum(d.get('predicted_cost', 0) for d in detections if d.get('type') != 'video')
        
        # Defect type distribution
        defect_dist = {}
        for d in detections:
            if d.get('type') != 'video':
                dtype = d.get('defect_type', 'unknown')
                defect_dist[dtype] = defect_dist.get(dtype, 0) + 1
        
        # Severity distribution
        severity_dist = {}
        for d in detections:
            if d.get('type') != 'video':
                severity = d.get('severity', 'unknown')
                severity_dist[severity] = severity_dist.get(severity, 0) + 1
        
        # Average confidence
        confidences = [d.get('confidence', 0) for d in detections if d.get('type') != 'video']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'total_inspections': total_inspections,
            'defects_found': defects_found,
            'total_cost_loss': round(total_cost_loss, 2),
            'defect_distribution': defect_dist,
            'severity_distribution': severity_dist,
            'average_confidence': round(avg_confidence, 2),
            'time_period': time_period
        }
    except Exception as e:
        print(f"❌ Error calculating analytics: {e}")
        return {}

# ===== USER MANAGEMENT FUNCTIONS =====

def create_user(username, email, password_hash):
    """Create a new user in MongoDB"""
    if db is None:
        print(f"[DATABASE] ❌ DB is None - cannot create user")
        return False
    
    try:
        user_doc = {
            'username': username,
            'email': email,
            'password': password_hash,
            'created_at': datetime.now().isoformat()
        }
        users_collection.insert_one(user_doc)
        print(f"[DATABASE] ✓ User {username} created successfully in MongoDB")
        return True
    except Exception as e:
        print(f"[DATABASE] ❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_user(username):
    """Get user by username"""
    if db is None:
        return None
    
    try:
        user = users_collection.find_one({'username': username})
        return user
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None

def user_exists(username):
    """Check if user exists"""
    if db is None:
        return False
    
    try:
        return users_collection.find_one({'username': username}) is not None
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return False

def delete_user(username):
    """Delete a user and all their data"""
    if db is None:
        return False
    
    try:
        # Delete user
        users_collection.delete_one({'username': username})
        # Delete all detections
        detections_collection.delete_many({'username': username})
        # Delete analytics
        analytics_collection.delete_many({'username': username})
        print(f"✓ Deleted user {username} and all associated data")
        return True
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False

if __name__ == "__main__":
    print("Database module loaded successfully")
