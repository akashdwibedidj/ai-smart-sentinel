from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
import json
import threading
import time
from datetime import datetime

from combined_system import CombinedSystem
from injection_detector import InjectionDetector
from decision_engine import DecisionEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize components
print("Initializing AI Smart Sentinel Backend...")
combined_system = CombinedSystem(camera_index=0)
injection_detector = InjectionDetector()
decision_engine = DecisionEngine()

# Global state for camera and last result
class VideoState:
    def __init__(self):
        self.camera = None
        self.is_streaming = False
        self.last_metrics = {
            'injection_score': 0.0,
            'liveness_score': 0.0,
            'face_detected': False,
            'person_name': 'Unknown',
            'spoof_detected': False,
            'access_granted': False,
            'timestamp': None
        }
        self.lock = threading.Lock()

video_state = VideoState()

def get_camera():
    if video_state.camera is None or not video_state.camera.isOpened():
        video_state.camera = cv2.VideoCapture(0)
        # Set resolution
        video_state.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        video_state.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return video_state.camera

def release_camera():
    if video_state.camera is not None:
        video_state.camera.release()
        video_state.camera = None

def generate_frames():
    camera = get_camera()
    
    while True:
        success, frame = camera.read()
        if not success:
            # Try to reconnect
            camera.release()
            video_state.camera = None
            time.sleep(1)
            camera = get_camera()
            continue
            
        # Process frame with CombinedSystem
        # This draws the boxes and labels directly on the frame
        results = combined_system.process_frame(frame)
        frame = combined_system.draw_results(frame, results)
        
        # Update metrics for the UI side-panel
        with video_state.lock:
            if results:
                # Use the primary face (first result)
                r = results[0]
                video_state.last_metrics = {
                    'injection_score': 0.02, # Placeholder as injection is separate
                    'liveness_score': r.get('spoof_confidence', 0),
                    'face_detected': True,
                    'person_name': r.get('name', 'Unknown'),
                    'spoof_detected': not r.get('is_real', True),
                    'access_granted': r.get('is_real', False) and r.get('is_known', False),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Log significant events to decision engine occasionally or on change
                # (Logic can be added here)
            else:
                video_state.last_metrics['face_detected'] = False

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/current_metrics', methods=['GET'])
def get_current_metrics():
    """Get the latest detection metrics from the video stream"""
    with video_state.lock:
        return jsonify(video_state.last_metrics)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'components': {
            'combined_system': 'ready',
            'camera': 'active' if video_state.camera and video_state.camera.isOpened() else 'inactive'
        }
    })

# Kept for backward compatibility or direct API usage
@app.route('/api/verify', methods=['POST'])
def verify_access():
    # ... (Keep existing implementation if needed, but streaming is primary now)
    return jsonify({'message': 'Please use video streaming mode'}), 400

# ... (Keep register, logs, stats endpoints)

@app.route('/api/register', methods=['POST'])
def register_face():
    """Register a new face"""
    try:
        data = request.json
        image_data = data.get('image')
        person_id = data.get('person_id')
        
        if not image_data or not person_id:
            return jsonify({'error': 'Image and person_id required'}), 400
            
        # If we are streaming, we might need to pause or handle resource contention
        # For simplicity, we decode the sent image and register it.
        # Ideally, we could grab a frame from the stream if requested.
        
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        success, message = combined_system.face_verifier.register_face(frame, person_id)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/registered-faces', methods=['GET'])
def get_registered_faces():
    try:
        faces = combined_system.face_verifier.get_registered_persons()
        return jsonify({'registered_faces': faces, 'count': len(faces)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        count = request.args.get('count', 10, type=int)
        logs = decision_engine.get_recent_logs(count)
        return jsonify({'logs': logs, 'count': len(logs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        stats = decision_engine.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_logs():
    try:
        with open(decision_engine.log_file, 'w') as f:
            json.dump([], f)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("AI Smart Sentinel - Streaming Backend")
    print("=" * 50)
    print("Server starting on http://localhost:5000")
    
    # Run threaded to support streaming
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)