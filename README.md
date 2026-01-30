# AI Smart Sentinel

**Advanced Multi-Layer Security System with Face Recognition, Anti-Spoofing, and Injection Attack Detection**

AI Smart Sentinel is a comprehensive security solution that combines cutting-edge computer vision, machine learning, and anti-spoofing technologies to provide robust access control and threat detection. The system features real-time video streaming, face recognition, liveness detection, and injection attack prevention.

---

## 🌟 Key Features

### Core Security Capabilities
- **Multi-Layer Face Verification**: KNN-based face recognition with high accuracy
- **Anti-Spoofing Detection**: Detects photo/video replay attacks and 3D mask attempts
- **Injection Attack Detection**: Identifies digital injection attacks and manipulated video streams
- **Real-Time Liveness Detection**: Ensures the person is physically present
- **Decision Engine**: Intelligent threat assessment and access control logic

### User Interface
- **Live Video Streaming**: Real-time camera feed with detection overlays
- **Interactive Dashboard**: Monitor system status, metrics, and analytics
- **Threat Detection Alerts**: Visual and audio notifications for security events
- **Analytics Dashboard**: Historical data, statistics, and incident reports
- **User Profile Management**: Register and manage authorized users
- **Settings Panel**: Configure detection thresholds and system parameters

---

## 📁 Project Structure

```
ai-smart-sentinel/
├── backend/                          # Python backend with Flask API
│   ├── combined_system.py           # Main unified detection system
│   ├── main.py                      # Flask server with video streaming
│   ├── antispoofing_detector.py     # Anti-spoofing detection module
│   ├── injection_detector.py        # Injection attack detection
│   ├── knn_face_verifier.py         # KNN-based face recognition
│   ├── decision_engine.py           # Access control logic & logging
│   ├── register_from_image.py       # Face registration utility
│   ├── test_complete_system.py      # System integration tests
│   ├── test_esp32_connection.py     # ESP32 camera testing
│   ├── test_liveness_phone.py       # Phone camera liveness tests
│   ├── test_video_file.py           # Video file testing utility
│   ├── find_phone_camera.py         # Phone camera discovery
│   └── utils.py                     # Utility functions
│
├── frontend/                         # Web-based user interface
│   ├── index.html                   # Landing page
│   ├── main-dashboard.html          # Main monitoring dashboard
│   ├── camera-view.html             # Live camera feed view
│   ├── analytics-dashboard.html     # Analytics and statistics
│   ├── settings.html                # System configuration
│   ├── profile.html                 # User profile management
│   ├── threat-detected.html         # Threat alert page
│   ├── verification-process.html    # Verification flow
│   ├── verification-success.html    # Success confirmation
│   ├── incident-modal.html          # Incident details modal
│   │
│   ├── css/                         # Stylesheets
│   │   ├── styles.css               # Global styles
│   │   ├── dashboard.css            # Dashboard styles
│   │   ├── camera-view.css          # Camera view styles
│   │   ├── analytics.css            # Analytics page styles
│   │   ├── settings.css             # Settings page styles
│   │   ├── profile.css              # Profile page styles
│   │   ├── threat-detected.css      # Threat alert styles
│   │   ├── verification.css         # Verification flow styles
│   │   └── incident-modal.css       # Modal styles
│   │
│   └── js/                          # JavaScript modules
│       ├── app.js                   # Main application logic
│       ├── main-dashboard.js        # Dashboard functionality
│       ├── camera-view.js           # Camera view controls
│       ├── analytics.js             # Analytics data handling
│       ├── settings.js              # Settings management
│       ├── profile.js               # Profile management
│       ├── threat-detected.js       # Threat handling
│       ├── verification.js          # Verification flow logic
│       └── incident-modal.js        # Modal interactions
│
├── data/                            # Application data storage
│   ├── faces/                       # Registered face encodings
│   │   ├── encodings.pkl            # Serialized face encodings
│   │   └── names.pkl                # Associated person names
│   └── logs/                        # System logs
│       └── access_log.json          # Access attempts and events
│
├── Face_Antispoofing_System-main/   # Anti-spoofing model & training
│   ├── models/                      # Pre-trained models
│   ├── datasets/                    # Training datasets
│   └── training/                    # Training scripts
│
├── face_recognition_project-main/   # Face recognition implementation
│   ├── knn_classifier/              # KNN model files
│   ├── training_data/               # Training images
│   └── utils/                       # Helper utilities
│
├── Face-Liveness-Detection/         # Liveness detection module
│   ├── models/                      # Liveness detection models
│   └── detection_scripts/           # Detection algorithms
│
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Camera**: Webcam or IP camera (ESP32-CAM supported)
- **RAM**: Minimum 4GB (8GB recommended)
- **GPU**: Optional (CUDA-compatible GPU for faster processing)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-smart-sentinel.git
cd ai-smart-sentinel
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note for Windows Users**: Installing `dlib` requires CMake and Visual Studio C++ Build Tools. If you encounter issues:
> 1. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
> 2. Install [CMake](https://cmake.org/download/)
> 3. Then run: `pip install dlib`

#### 4. Verify Installation
```bash
cd backend
python -c "import cv2, tensorflow, dlib, flask; print('All dependencies installed successfully!')"
```

---

## 💻 Usage

### Starting the System

#### 1. Start the Backend Server
```bash
cd backend
python main.py
```

The Flask server will start on `http://localhost:5000`

#### 2. Access the Web Interface
Open your browser and navigate to:
```
http://localhost:5000
```

### Registering Users

#### Method 1: Using the Web Interface
1. Navigate to the **Profile** page
2. Click **"Register New Face"**
3. Enter the person's name
4. Capture or upload a clear photo
5. Click **"Register"**

#### Method 2: Using Command Line
```bash
cd backend
python register_from_image.py --name "John Doe" --image path/to/image.jpg
```

### Running Detection Tests

#### Test Complete System
```bash
cd backend
python test_complete_system.py
```

#### Test with Video File
```bash
python test_video_file.py --video path/to/video.mp4
```

#### Test ESP32 Camera Connection
```bash
python test_esp32_connection.py --ip 192.168.1.100
```

#### Test Phone Camera
```bash
python find_phone_camera.py
python test_liveness_phone.py --camera 1
```

---

## 🔧 Configuration

### Camera Settings
Edit `backend/combined_system.py`:
```python
# Change camera source
system = CombinedSystem(camera_index=0)  # 0 for default webcam

# For IP camera (ESP32-CAM)
system = CombinedSystem(camera_index="http://192.168.1.100:81/stream")
```

### Detection Thresholds
Edit `backend/decision_engine.py`:
```python
# Adjust sensitivity
LIVENESS_THRESHOLD = 0.7      # Anti-spoofing confidence
FACE_MATCH_THRESHOLD = 0.6    # Face recognition threshold
INJECTION_THRESHOLD = 0.8     # Injection detection threshold
```

### Server Configuration
Edit `backend/main.py`:
```python
# Change host/port
app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
```

---

## 🧪 Testing

### Unit Tests
```bash
# Test individual components
cd backend
python -m pytest tests/
```

### Integration Tests
```bash
# Test complete system workflow
python test_complete_system.py
```

### Performance Benchmarking
```bash
# Measure FPS and detection accuracy
python benchmark.py --duration 60
```

---

## 📊 API Endpoints

### Video Streaming
- **GET** `/video_feed` - Real-time video stream with detection overlays

### Metrics & Status
- **GET** `/api/current_metrics` - Latest detection metrics
- **GET** `/api/health` - System health check
- **GET** `/api/statistics` - Overall system statistics

### Face Management
- **POST** `/api/register` - Register a new face
  ```json
  {
    "person_id": "John Doe",
    "image": "base64_encoded_image"
  }
  ```
- **GET** `/api/registered-faces` - List all registered faces

### Logging & Analytics
- **GET** `/api/logs?count=10` - Recent access logs
- **POST** `/api/reset` - Clear all logs

---

## 🛡️ Security Features

### Anti-Spoofing Detection
- **Photo Attack Detection**: Identifies printed photos
- **Video Replay Detection**: Detects video playback attempts
- **3D Mask Detection**: Recognizes physical masks
- **Screen Detection**: Identifies faces displayed on screens

### Injection Attack Prevention
- **Digital Injection Detection**: Detects manipulated video streams
- **Frame Consistency Analysis**: Validates temporal coherence
- **Metadata Verification**: Checks for tampering indicators

### Access Control
- **Multi-Factor Verification**: Combines liveness + face recognition
- **Confidence Scoring**: Probabilistic threat assessment
- **Audit Logging**: Complete access history with timestamps
- **Real-Time Alerts**: Immediate notification of threats

---

## 🎨 Technologies Used

### Backend
- **Flask**: Web framework and API server
- **OpenCV**: Computer vision and image processing
- **TensorFlow/Keras**: Deep learning models
- **dlib**: Face detection and recognition
- **scikit-learn**: KNN classifier for face matching
- **NumPy/SciPy**: Numerical computing

### Frontend
- **HTML5/CSS3**: Modern web interface
- **Vanilla JavaScript**: Client-side logic
- **WebRTC**: Real-time video streaming
- **Chart.js**: Analytics visualization (if applicable)

### Machine Learning Models
- **Anti-Spoofing**: Custom CNN trained on NUAA/CASIA datasets
- **Face Recognition**: KNN with dlib face encodings
- **Injection Detection**: Temporal consistency analysis
- **Liveness Detection**: Multi-frame analysis

---

## 📈 Performance

### Typical Metrics
- **FPS**: 15-30 frames per second (depending on hardware)
- **Detection Latency**: <100ms per frame
- **Face Recognition Accuracy**: >95% (with good lighting)
- **Anti-Spoofing Accuracy**: >90% (on test datasets)
- **False Positive Rate**: <5%

### Optimization Tips
- Use GPU acceleration for TensorFlow models
- Reduce camera resolution for faster processing
- Adjust detection frequency (skip frames)
- Use multi-threading for parallel processing

---

## 🐛 Troubleshooting

### Common Issues

#### Camera Not Detected
```bash
# List available cameras
python backend/find_phone_camera.py
```

#### Module Import Errors
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Low FPS / Performance Issues
- Reduce camera resolution in `combined_system.py`
- Disable debug mode in `main.py`
- Close other resource-intensive applications
- Consider using GPU acceleration

#### Face Recognition Not Working
- Ensure good lighting conditions
- Register multiple angles of the same person
- Adjust `FACE_MATCH_THRESHOLD` in `decision_engine.py`
- Verify face encodings exist in `data/faces/`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Akash Dwibedi**

- GitHub: [@akashdwibedidj](https://github.com/akashdwibedidj)
- Project Repository: [ai-smart-sentinel](https://github.com/akashdwibedidj/ai-smart-sentinel)

---

## 🙏 Acknowledgments

- Face Anti-Spoofing research papers and datasets
- OpenCV and dlib communities
- TensorFlow/Keras documentation
- Flask framework developers

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub Issues](https://github.com/akashdwibedidj/ai-smart-sentinel/issues)
- Contact: your.email@example.com

---

## 🔮 Future Enhancements

- [ ] Multi-camera support
- [ ] Cloud deployment (AWS/Azure)
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Email/SMS notifications
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Docker containerization
- [ ] Kubernetes orchestration
- [ ] Enhanced AI models with transfer learning
- [ ] Multi-language support

---

**Made with ❤️ for Enhanced Security**
