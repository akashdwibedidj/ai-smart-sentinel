"""
Flask API Backend
Main server for AI Smart Sentinel system
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os

from injection_detector import InjectionDetector
from liveness_detector import LivenessDetector
from face_verifier import FaceVerifier
from decision_engine import DecisionEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize all components
injection_detector = InjectionDetector()
liveness_detector = LivenessDetector()
face_verifier = FaceVerifier()
decision_engine = DecisionEngine()

# Store previous frame for injection detection
prev_frame = None

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'components': {
            'injection_detector': 'ready',
            'liveness_detector': 'ready',
            'face_verifier': 'ready',
            'decision_engine': 'ready'
        }
    })

@app.route('/api/verify', methods=['POST'])
def verify_access():
    """
    Main verification endpoint
    Expects: base64 encoded image
    Returns: Access decision
    """
    global prev_frame
    
    try:
        data = request.json
        image_data = data.get('image')
        person_id = data.get('person_id', None)
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Run all checks
        # 1. Injection detection
        injection_result = injection_detector.full_injection_check(
            frame, prev_frame
        )
        
        # 2. Liveness detection
        liveness_result = liveness_detector.hybrid_liveness_check(frame)
        
        # 3. Face verification
        verification_result = face_verifier.verify_face(frame, person_id)
        
        # 4. Make decision
        decision = decision_engine.make_decision(
            injection_result,
            liveness_result,
            verification_result
        )
        
        # 5. Log decision
        decision_engine.log_decision(decision, frame)
        
        # Update previous frame
        prev_frame = frame.copy()
        
        return jsonify(decision)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_face():
    """
    Register a new face
    Expects: base64 image and person_id
    """
    try:
        data = request.json
        image_data = data.get('image')
        person_id = data.get('person_id')
        
        if not image_data or not person_id:
            return jsonify({'error': 'Image and person_id required'}), 400
        
        # Decode image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Register face
        success, message = face_verifier.register_face(frame, person_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'person_id': person_id
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/registered-faces', methods=['GET'])
def get_registered_faces():
    """Get list of all registered faces"""
    try:
        faces = face_verifier.get_registered_faces()
        return jsonify({
            'registered_faces': faces,
            'count': len(faces)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent access logs"""
    try:
        count = request.args.get('count', 10, type=int)
        logs = decision_engine.get_recent_logs(count)
        return jsonify({
            'logs': logs,
            'count': len(logs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get access statistics"""
    try:
        stats = decision_engine.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_logs():
    """Reset all logs (for demo purposes)"""
    try:
        log_file = decision_engine.log_file
        with open(log_file, 'w') as f:
            import json
            json.dump([], f)
        
        return jsonify({
            'success': True,
            'message': 'Logs reset successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("AI Smart Sentinel - Backend Server")
    print("=" * 50)
    print("Server starting on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)