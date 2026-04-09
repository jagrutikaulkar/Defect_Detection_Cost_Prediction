# 🏭 AI Industrial Quality Control System

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask 2.x](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![TensorFlow 2.10+](https://img.shields.io/badge/TensorFlow-2.10+-orange.svg)](https://tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent, fully responsive web application for real-time surface defect detection and production cost prediction using AI/ML. Designed for industrial quality control systems.

## 📸 Features

### Core Capabilities
- **🔍 AI Defect Detection** - 98%+ accuracy CNN model for detecting 6 types of steel surface defects
- **💰 Smart Cost Prediction** - RandomForest model predicting production costs with 97% variance explained
- **📱 Fully Responsive UI** - Mobile-first design, works seamlessly on all devices (320px to 4K)
- **👤 User Authentication** - Secure registration & login with password hashing
- **📊 Interactive Dashboard** - Real-time analytics and detection history tracking
- **⚡ Real-time Processing** - ML inference in <2 seconds per image
- **🎨 Modern Web Interface** - Clean, intuitive UI with smooth animations

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/industrial-defect-detection.git
cd industrial-defect-detection
```

2. **Create virtual environment**
```bash
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Access the app**
- Open browser: `http://localhost:5000`
- Register a new account
- Navigate to Defect Detection
- Upload an image and enter production parameters
- Get instant AI predictions!

## 📁 Project Structure

```
industrial-defect-detection/
├── app.py                      # Flask backend API server
├── predict.py                  # ML inference pipeline
├── preprocess.py               # Image preprocessing & validation
├── database.py                 # Database utilities
│
├── models/                     # Pre-trained ML models
│   ├── defect_model.h5         # CNN model (11 MB, 98% accurate)
│   └── cost_model.pkl          # RandomForest model (3 MB)
│
├── data/datasets/NEU-DET/      # Steel surface defect dataset
│   ├── train/                  # 1,440 training images
│   └── validation/             # 360 validation images
│
├── frontend/                   # Web user interface (fully responsive)
│   ├── index.html              # Homepage
│   ├── dashboard.html          # Analytics dashboard
│   ├── defect-detection.html   # Defect detection page
│   ├── cost-prediction.html    # Cost prediction page
│   ├── video-detection.html    # Video analysis
│   ├── analytics.html          # Analytics & reports
│   ├── css/                    # Responsive stylesheets
│   │   ├── main.css            # Global styles & media queries
│   │   ├── dashboard.css       # Dashboard styles
│   │   └── components.css      # Reusable components
│   └── js/                     # Frontend JavaScript
│       ├── main.js             # Core functionality & mobile menu
│       ├── dashboard.js        # Dashboard interactions
│       └── [other].js          # Feature-specific scripts
│
├── uploads/                    # Temporary file storage
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── Procfile                    # Heroku deployment config
└── README.md                   # This file
```

## 🤖 AI Models

### Defect Detection (CNN)
```
Model:          MobileNetV2 (Transfer Learning)
Training Acc:   98.44%
Validation Acc: 97.92%
Input:          224×224 RGB images
Output:         6 class probabilities
Classes:        Crazing, Inclusion, Patches, Pitted Surface, 
                Rolled-in Scale, Scratches
Speed:          ~500ms per image
```

### Cost Prediction (RandomForest)
```
Model:          Random Forest Regressor (200 trees)
Test R²:        0.9714 (97.14% variance explained)
MAE:            ₹21.88 per prediction
Features:       Defect type, area, severity, machine time, 
                labor cost, material cost
Speed:          <10ms per prediction
```

## 📊 Supported Defect Types

| Class | Description |
|-------|-------------|
| 🔗 **Crazing** | Fine hair-like surface cracks |
| 🧲 **Inclusion** | Foreign particles embedded in metal |
| 🎨 **Patches** | Uneven patches and discoloration |
| 🕳️ **Pitted Surface** | Deep pits and corrosion spots |
| 〰️ **Rolled-in Scale** | Oxide scale rolled into surface |
| ✂️ **Scratches** | Surface scratches and marks |

## 🎯 How It Works

### Defect Detection Pipeline
```
User uploads image
    ↓
Image preprocessing (resize 224×224, normalize)
    ↓
CPU Inference via MobileNetV2
    ↓
Get 6 class probability scores
    ↓
Return highest confidence defect type
    ↓
Display results with confidence & severity
```

### Cost Prediction Pipeline
```
Defect characteristics (from CNN)
    ↓
+ User enters production parameters:
  • Machine time (hours)
  • Labor cost (₹/hour)
  • Material cost (₹)
    ↓
Feed to RandomForest model
    ↓
Calculate total production cost
    ↓
Show cost breakdown & recommendations
```

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register              Register new user
POST   /api/auth/login                 User login
POST   /api/auth/logout                User logout
GET    /api/auth/profile               Get user profile
```

### Defect Detection
```
POST   /api/defect/detect              Upload image & get predictions
GET    /api/defect/history             View detection history
GET    /api/defect/stats               Get analytics statistics
```

### System Health
```
GET    /api/health                     Server status
GET    /api/models                     Model availability check
```

## 💻 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask 2.x, Python 3.9+ |
| **ML Models** | TensorFlow 2.10+, scikit-learn |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Image Processing** | OpenCV, Pillow |
| **Database** | MongoDB (optional), JSON (default) |
| **Deployment** | Docker, Heroku-ready |

## 🔐 Security Features

- ✅ **Password Hashing**: PBKDF2 with 100,000 iterations
- ✅ **Secure Tokens**: Cryptographically secure session tokens
- ✅ **CORS Enabled**: Safe cross-origin requests
- ✅ **File Validation**: JPG/PNG only, max 16MB
- ✅ **Input Sanitization**: All user inputs validated
- ⚠️ **Note**: For production, implement proper database (MongoDB/PostgreSQL)

## 📱 Responsive Design

This application is **fully responsive** and optimized for:
- ✅ Mobile phones (320px - 640px)
- ✅ Tablets (641px - 1024px)  
- ✅ Desktops (1025px+)
- ✅ Landscape orientation
- ✅ High-DPI displays

Features:
- Mobile hamburger navigation menu
- Collapsible sidebar on small screens
- Touch-friendly button sizes (44px minimum)
- Adaptive grid layouts
- Optimized performance

## 📈 Dataset Information

**NEU-DET** (Northeastern University Surface Defect Detection)

```
Total Images:    1,800
Training Set:    1,440 images (80%)
Validation Set:  360 images (20%)

Image Specs:
├─ Original: 200×200 pixels
├─ Processed: 224×224 pixels (resized for CNN)
└─ Format: RGB color images (JPG)

Defect Distribution:
├─ Crazing: 300 images
├─ Inclusion: 300 images
├─ Patches: 300 images
├─ Pitted Surface: 300 images
├─ Rolled-in Scale: 300 images
└─ Scratches: 300 images
```

## 💰 Cost Calculation Example

```
Raw Material Request:
- Defect Type: Scratches (3% area)
- Machine Time: 2.5 hours
- Labor Rate: ₹500/hour  
- Material Cost: ₹400

Calculation:
Base Cost = Material + Labor + Machine Time
          = 400 + (2.5 × 500) + (2.5 × 60)
          = 400 + 1250 + 150
          = ₹1,800

Defect Penalty = (Area × 5) + (Severity × 120)
               = (3 × 5) + (LOW × 120)
               = 15 + 40
               = ₹55

TOTAL COST = ₹1,855
```

## 🚀 Deployment

### Docker
```bash
docker build -t defect-detection .
docker run -p 5000:5000 defect-detection
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Railway / Render
Push to GitHub, connect repository, deploy automatically.

## 🧪 Testing

```bash
# Test API endpoints
curl http://localhost:5000/api/health

# Test model availability
curl http://localhost:5000/api/models
```

## 📝 Sample Usage

1. **Register Account**
   - Click "Register" on homepage
   - Enter username, password, email
   - Create account

2. **Login**
   - Use credentials on login form
   - Redirected to dashboard

3. **Run Detection**
   - Go to "Defect Detection" tab
   - Upload steel surface image
   - Enter production parameters
   - View AI predictions

4. **View Analytics**
   - Check "Dashboard" for statistics
   - View "Analytics" for detailed reports
   - Download detection history

## 📚 Documentation

For detailed documentation, see:
- [Installation Guide](./docs/INSTALL.md)
- [API Reference](./docs/API.md)
- [Model Training](./docs/TRAINING.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

## 👨‍💻 Author

Created by [Your Name/Team]

## 🙏 Acknowledgments

- **Dataset**: NEU-DET from Northeastern University
- **Framework**: Flask & TensorFlow
- **Icons**: Font Awesome
- **Community**: Open source contributors

## 📞 Support

For issues, questions, or suggestions:
- 🐛 [Report a bug](https://github.com/yourusername/industrial-defect-detection/issues)
- 💬 [Start a discussion](https://github.com/yourusername/industrial-defect-detection/discussions)
- 📧 Email: your.email@example.com

## 🔄 Version History

- **v1.0.0** (2026-04-09) - Initial release with core features
  - AI defect detection (6 classes)
  - Cost prediction model
  - Fully responsive web interface
  - User authentication

---

**Made with ❤️ for Industrial Quality Control**
    ↓
RandomForest Model
    ↓
Result: Predicted Cost (₹)
```

## 💰 Cost Calculation

**Formula:**
```
Cost = Material + Labor + (Machine_Time × 60) + Defect_Penalty

Where:
Defect_Penalty = (Defect_Area × 5) + (Severity × 120)
```

**Example:**
```
Same Defect (93% area, severity HIGH)

Premium Line:    Machine 2.5h, Labor ₹500/h, Material ₹400
                 → Cost: ₹1890 💰💰

Budget Line:     Machine 0.75h, Labor ₹120/h, Material ₹80
                 → Cost: ₹920 💵

Cost Difference: 67% (same defect!)
```

## 🤖 Defect Classes (6)

| Class | Description |
|-------|-------------|
| **Crazing** | Hair-like cracks on surface |
| **Inclusion** | Foreign particles embedded |
| **Patches** | Uneven patches/discoloration |
| **Pitted Surface** | Deep pits/corrosion spots |
| **Rolled-in Scale** | Oxide scale rolled into surface |
| **Scratches** | Surface scratches/marks |

## 📋 API Endpoints

### **User Management**
```
POST   /api/auth/register      # Create new account
POST   /api/auth/login         # User login
POST   /api/auth/logout        # User logout
GET    /api/auth/profile       # Get user info
```

### **Defect Detection**
```
POST   /api/defect/detect      # Upload image + parameters
GET    /api/defect/history     # View detection history
```

### **System Health**
```
GET    /api/health             # Server status
GET    /api/models             # Model status check
```

## 🎓 Dataset

**NEU-DET** (Northeastern University Surface Defect Detection)

```
1,800 images total
├─ Training:   1,440 (80%)
└─ Validation: 360 (20%)

6 Defect Classes
├─ 300 images per class
├─ 200×200 pixels (resized to 224×224)
└─ RGB color images
```

## 🔐 Security

- ✅ PBKDF2 password hashing (100,000 iterations)
- ✅ Secure token generation
- ✅ CORS enabled (frontend-backend communication)
- ✅ File validation (JPG/PNG, max 16MB)
- ⚠️ Note: Uses JSON storage (use database for production)

## 🛠️ Technology Stack

```
Backend:      Flask 2.x
ML Models:    TensorFlow 2.10+ (CNN)
              scikit-learn (RandomForest)
Frontend:     HTML5, CSS3, JavaScript
Database:     JSON (users.json)
Server:       Python development server
```

## 📝 Typical Usage Example

```python
# 1. User registers and logs in (web frontend)

# 2. User enters production parameters:
Machine Time:    2.0 hours
Labor Cost:      ₹300/hour
Material Cost:   ₹200

# 3. User uploads defect image

# 4. Backend processes:
- Image → CNN → Detects: "crazing" (99.86% confidence)
- Image analysis → Defect area: 93.77%
- Features + Parameters → RandomForest → Cost: ₹1447.23

# 5. Frontend displays results:
- Defect Type:     CRAZING
- Confidence:      99.86%
- Severity:        HIGH
- Defect Area:     93.77%
- Estimated Cost:  ₹1447.23 ← Based on user's parameters!
```

## 🚀 Production Deployment

For production use:

1. **Use WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Use Real Database**
   - Replace JSON with PostgreSQL/MySQL
   - Update `app.py` user management

3. **Setup HTTPS**
   - Use Nginx reverse proxy
   - Generate SSL certificates

4. **Add Monitoring**
   - Error tracking (Sentry)
   - Performance monitoring
   - Log aggregation

## 📚 Optional: Re-train Models

If you want to retrain from scratch:

```bash
# Train CNN (requires NEU-DET dataset)
python train_defect_model.py      # ~6 minutes

# Train RandomForest
python train_cost_model.py        # ~2 minutes
```

New models will overwrite existing ones in `models/` folder.

## 📊 Key Metrics

```
System Status:     ✅ Production Ready
Frontend Status:   ✅ Working
Backend Status:    ✅ Running
Models Status:     ✅ Loaded
Authentication:    ✅ Active
Database:          ✅ Ready (JSON)

Performance:
- Defect Detection Accuracy:  99.25% average
- Cost Prediction Accuracy:   R² = 0.9714
- API Response Time:          <500ms
```

## 🎯 Key Improvements

**Latest Update:**
- ✅ User-provided production parameters
- ✅ Flexible cost calculations
- ✅ Multiple scenario comparison
- ✅ Clean, modern UI
- ✅ Secure authentication
- ✅ Production-ready code

## 📞 File Reference

| File | Purpose |
|------|---------|
| `app.py` | Flask server + all API endpoints |
| `predict.py` | ML inference (CNN + RandomForest) |
| `preprocess.py` | Image preprocessing utilities |
| `train_defect_model.py` | CNN training script |
| `train_cost_model.py` | RandomForest training script |
| `requirements.txt` | Python dependencies |

## ✅ Status

**Version:** 1.0
**Status:** Production Ready
**Last Updated:** March 27, 2026
**Components:** Fully Functional ✅

---

**Questions?** Check the code comments in `app.py` and `predict.py` for detailed implementation notes.
