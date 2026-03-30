"""
Simple Flask Backend for Defect Detection
Minimal, clean, production-ready
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
import hashlib
import secrets
from datetime import datetime
from predict import get_predictor

app = Flask(__name__, template_folder='frontend', static_folder='frontend', static_url_path='')
CORS(app)

# Simple in-memory user storage
USERS_FILE = 'users.json'
DETECTIONS_FILE = 'detections.json'
TOKENS = {}  # token -> username mapping

def load_users():
    """Load users from file or return empty dict"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_detections():
    """Load detection history from file"""
    if os.path.exists(DETECTIONS_FILE):
        try:
            with open(DETECTIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_detections(detections):
    """Save detection history to file"""
    with open(DETECTIONS_FILE, 'w') as f:
        json.dump(detections, f)

def add_detection(username, detection_data):
    """Add a detection record for a user"""
    detections = load_detections()
    
    if username not in detections:
        detections[username] = []
    
    # Add timestamp if not present
    if 'created_at' not in detection_data:
        detection_data['created_at'] = datetime.now().isoformat()
    
    detections[username].append(detection_data)
    save_detections(detections)

def get_user_detections(username):
    """Get all detections for a user"""
    detections = load_detections()
    return detections.get(username, [])

def hash_password(password):
    """Hash password with random salt"""
    salt = secrets.token_hex(8)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${password_hash.hex()}"

def verify_password(password, hash_pwd):
    """Verify password against hash"""
    try:
        salt, password_hash = hash_pwd.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == password_hash
    except:
        return False

def generate_token():
    """Generate a secure token"""
    return secrets.token_urlsafe(32)

def get_current_user(token):
    """Get username from token"""
    return TOKENS.get(token)

# Create upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ====== AUTHENTICATION ENDPOINTS ======

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'status': 'error', 'message': 'Username must be at least 3 characters'}), 400
        
        if not email or '@' not in email:
            return jsonify({'status': 'error', 'message': 'Valid email required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'}), 400
        
        users = load_users()
        
        # Check if user exists
        if username in users:
            return jsonify({'status': 'error', 'message': 'Username already exists'}), 400
        
        # Create user
        users[username] = {
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat()
        }
        
        save_users(users)
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user and return token"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password required'}), 400
        
        users = load_users()
        
        # Check if user exists
        if username not in users:
            return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401
        
        # Verify password
        user = users[username]
        if not verify_password(password, user['password']):
            return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401
        
        # Generate token
        token = generate_token()
        TOKENS[token] = username
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'access_token': token,
                'username': username,
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user (remove token)"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if token in TOKENS:
                del TOKENS[token]
        
        return jsonify({'status': 'success', 'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    try:
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        if not token or token not in TOKENS:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
        username = TOKENS[token]
        users = load_users()
        
        if username not in users:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        user = users[username]
        
        return jsonify({
            'status': 'success',
            'data': {
                'username': username,
                'email': user['email'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ====== PREDICTION ENDPOINTS ======

@app.route('/')
def index():
    """Serve frontend"""
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict_defect():
    """
    Predict defect from uploaded image
    
    POST /api/predict
    Body: multipart/form-data with 'image' file
    
    Response:
    {
        "status": "success",
        "defect_type": "scratches",
        "confidence": 94.2,
        "severity": "low",
        "predicted_cost": 720.50,
        "defect_area": 15.3,
        "all_predictions": { ... }
    }
    """
    
    # Check if image in request
    if 'image' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No image file provided'
        }), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No file selected'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': 'File type not allowed. Use: jpg, jpeg, png'
        }), 400
    
    try:
        # Save file
        filename = f"temp_{int(__import__('time').time() * 1000)}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Make prediction
        predictor = get_predictor()
        result = predictor.predict(filepath)
        
        # Clean up
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/defect/detect', methods=['POST'])
def detect_defect():
    """
    Defect detection with production parameters
    Accepts: image + machine_time + labor_cost + material_cost
    Returns: defect_type + confidence + severity + defect_area + predicted_cost
    """
    # Check if image in request
    if 'image' not in request.files:
        return jsonify({
            'status': 'error',
            'data': None
        }), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'data': None
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'data': None
        }), 400
    
    try:
        # Extract production parameters from request
        machine_time = float(request.form.get('machine_time', 2.0))
        labor_cost = float(request.form.get('labor_cost', 300))
        material_cost = float(request.form.get('material_cost', 200))
        
        # Validate ranges
        machine_time = max(0.5, min(10, machine_time))
        labor_cost = max(50, min(1000, labor_cost))
        material_cost = max(50, min(2000, material_cost))
        
        # Save file
        filename = f"temp_{int(__import__('time').time() * 1000)}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Make prediction with production parameters
        predictor = get_predictor()
        result = predictor.predict(
            filepath,
            machine_time=machine_time,
            labor_cost=labor_cost,
            material_cost=material_cost
        )
        
        # Clean up
        try:
            os.remove(filepath)
        except:
            pass
        
        # Wrap in frontend-expected format
        if result['status'] == 'success':
            # Convert probabilities dict to array format
            all_preds = result.get('all_predictions', {})
            probabilities_array = [
                {'class': class_name, 'confidence': float(conf)}
                for class_name, conf in all_preds.items()
            ]
            
            detection_result = {
                'defect_type': result.get('defect_type'),
                'confidence': result.get('confidence'),
                'severity': result.get('severity'),
                'predicted_cost': result.get('predicted_cost'),
                'defect_area': result.get('defect_area'),
                'probabilities': probabilities_array,
                'created_at': datetime.now().isoformat()
            }
            
            # Save detection to history
            try:
                current_user = get_current_user(request.headers.get('Authorization', '').replace('Bearer ', ''))
                if current_user:
                    add_detection(current_user, detection_result)
            except:
                pass
            
            return jsonify({
                'status': 'success',
                'success': True,
                'data': detection_result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'success': False,
                'error': result.get('error', 'Prediction failed')
            }), 400
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/defect/history', methods=['GET'])
def get_detection_history():
    """Get user's detection history"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        current_user = get_current_user(token)
        
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized'
            }), 401
        
        # Get user's detections (sorted by newest first)
        detections = get_user_detections(current_user)
        detections.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'status': 'success',
            'data': detections
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/defect/history/delete', methods=['DELETE'])
def delete_detection_history():
    """Delete all user's detection history"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        current_user = get_current_user(token)
        
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized'
            }), 401
        
        # Load and delete user's detections
        detections = load_detections()
        if current_user in detections:
            del detections[current_user]
            save_detections(detections)
        
        return jsonify({
            'status': 'success',
            'message': 'History deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/cost/predict', methods=['POST'])
def predict_cost():
    """
    Predict production cost based on parameters
    
    POST /api/cost/predict
    Body: {
        "material_cost": 200-500 (₹),
        "labor_cost": 100-400 (₹),
        "machine_time": 1-4 (hours),
        "energy_consumption": 50-150 (kWh),
        "defect_rate": 0-5 (%)
    }
    
    Response: {
        "status": "success",
        "success": true,
        "data": {
            "predicted_cost": 1234.56,
            "breakdown": {...},
            "confidence_interval": {...},
            "optimization_suggestions": [...]
        }
    }
    """
    try:
        data = request.get_json()
        
        # Extract input parameters
        material_cost = float(data.get('material_cost', 300))
        labor_cost = float(data.get('labor_cost', 250))
        machine_time = float(data.get('machine_time', 2))
        energy_consumption = float(data.get('energy_consumption', 100))
        defect_rate = float(data.get('defect_rate', 2))
        
        # Get cost prediction model
        predictor = get_predictor()
        if predictor.cost_model is None:
            return jsonify({
                'status': 'error',
                'success': False,
                'error': 'Cost model not loaded'
            }), 500
        
        # Convert inputs to model features
        # Model expects: defect_type, defect_area, severity, machine_time, labor_cost, material_cost
        # We'll estimate these from available data
        
        defect_type = 0  # Neutral defect type
        defect_area = min(40, max(5, defect_rate * 8))  # Convert defect_rate to area (5-40%)
        severity = 1 if defect_rate < 1.5 else (2 if defect_rate < 3 else 3)  # 1=low, 2=med, 3=high
        
        # Prepare features for model
        features = [[defect_type, defect_area, severity, machine_time, labor_cost, material_cost]]
        
        # Make prediction
        predicted_cost = predictor.cost_model.predict(features)[0]
        
        # Calculate breakdown
        base_cost = material_cost + labor_cost
        machine_cost = machine_time * 75  # ₹75 per hour
        energy_cost = energy_consumption * 3  # ₹3 per kWh
        defect_penalty = (base_cost * defect_rate) / 100
        
        breakdown = {
            'material': float(material_cost),
            'labor': float(labor_cost),
            'machine': float(machine_cost),
            'energy': float(energy_cost),
            'defect_penalty': float(defect_penalty),
            'total': float(predicted_cost)
        }
        
        # Calculate confidence interval (±5%)
        confidence_interval = {
            'lower': float(predicted_cost * 0.95),
            'upper': float(predicted_cost * 1.05),
            'confidence': 95
        }
        
        # Generate optimization suggestions
        suggestions = []
        if material_cost > 350:
            savings = material_cost * 0.1
            suggestions.append(f'Reduce material waste by 10% to save ₹{savings:.0f}')
        if machine_time > 3:
            suggestions.append('Optimize machine scheduling to reduce time')
        if defect_rate > 2:
            suggestions.append('Implement defect prevention measures to reduce defects')
        if energy_consumption > 120:
            suggestions.append('Review energy consumption patterns for efficiency')
        if len(suggestions) == 0:
            suggestions.append('Current production parameters are efficient')
        
        # Save cost prediction to history
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            current_user = get_current_user(token)
            if current_user:
                # Save as a cost prediction record
                cost_prediction_record = {
                    'defect_type': 'Cost Prediction',
                    'confidence': 95,  # Confidence level
                    'severity': ['low', 'medium', 'high'][severity - 1],
                    'predicted_cost': round(predicted_cost, 2),
                    'defect_area': defect_area,
                    'probabilities': [],
                    'created_at': datetime.now().isoformat(),
                    'input_parameters': {
                        'material_cost': material_cost,
                        'labor_cost': labor_cost,
                        'machine_time': machine_time,
                        'energy_consumption': energy_consumption,
                        'defect_rate': defect_rate
                    }
                }
                add_detection(current_user, cost_prediction_record)
        except:
            pass
        
        return jsonify({
            'status': 'success',
            'success': True,
            'data': {
                'predicted_cost': round(predicted_cost, 2),
                'breakdown': breakdown,
                'confidence_interval': confidence_interval,
                'optimization_suggestions': suggestions,
                'input_parameters': {
                    'material_cost': material_cost,
                    'labor_cost': labor_cost,
                    'machine_time': machine_time,
                    'energy_consumption': energy_consumption,
                    'defect_rate': defect_rate
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cost/history', methods=['GET'])
def get_cost_history():
    """Get cost prediction history (returns empty for simplified version)"""
    return jsonify({
        'status': 'success',
        'data': []
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Server is running'
    }), 200

@app.route('/api/models', methods=['GET'])
def check_models():
    """Check if models are loaded"""
    predictor = get_predictor()
    
    return jsonify({
        'defect_model_loaded': predictor.cnn_model is not None,
        'cost_model_loaded': predictor.cost_model is not None,
        'defect_model_path': 'models/defect_model.h5',
        'cost_model_path': 'models/cost_model.pkl'
    }), 200

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'status': 'error', 'message': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'status': 'error', 'message': 'Server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Defect Detection Backend")
    print("=" * 60)
    print("Starting Defect Detection Backend")
    print("=" * 60)
    
    # Initialize models on startup
    print("\nLoading ML models...")
    predictor = get_predictor()
    print()
    
    print("=" * 60)
    print("Flask server running on http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /                - Frontend")
    print("  POST /api/predict     - Predict defect from image")
    print("  GET  /api/health      - Health check")
    print("  GET  /api/models      - Check if models loaded")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
