"""
Anti-Spoofing Detector - Wrapper for MobileNet Model
Uses the trained model from Face_Antispoofing_System-main
Detects if a face is real or a spoof (photo/screen)
"""

import cv2
import numpy as np
import os

# TensorFlow imports
try:
    from tensorflow.keras.models import model_from_json
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. Anti-spoofing detection disabled.")


class AntiSpoofingDetector:
    def __init__(self):
        """Initialize Anti-Spoofing Detector with MobileNet model"""
        self.model = None
        self.face_cascade = None
        self.model_loaded = False
        
        # Paths to model files (relative to project root)
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_dir = os.path.join(self.project_root, "Face_Antispoofing_System-main", "antispoofing_models")
        self.cascade_dir = os.path.join(self.project_root, "Face_Antispoofing_System-main", "models")
        
        # Load model
        self._load_model()
        self._load_face_cascade()
    
    def _load_model(self):
        """Load the MobileNet anti-spoofing model"""
        if not TENSORFLOW_AVAILABLE:
            print("TensorFlow not available, skipping model load")
            return
        
        # Save current directory and change to the antispoofing folder
        # This mimics how the original livelines_net.py works
        original_cwd = os.getcwd()
        antispoofing_dir = os.path.join(self.project_root, "Face_Antispoofing_System-main")
        
        try:
            os.chdir(antispoofing_dir)
            
            # Load exactly like the original livelines_net.py
            json_file = open('antispoofing_models/finalyearproject_antispoofing_model_mobilenet.json', 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            
            self.model = model_from_json(loaded_model_json)
            self.model.load_weights('antispoofing_models/finalyearproject_antispoofing_model_99-0.949474.weights.h5')
            
            self.model_loaded = True
            print("Anti-spoofing model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading anti-spoofing model: {e}")
            self.model_loaded = False
        finally:
            # Always restore original directory
            os.chdir(original_cwd)
    
    def _load_face_cascade(self):
        """Load Haar Cascade for face detection"""
        try:
            cascade_path = os.path.join(self.cascade_dir, "haarcascade_frontalface_default.xml")
            if os.path.exists(cascade_path):
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
            else:
                # Fallback to OpenCV's built-in cascade
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
            print("Face cascade loaded successfully!")
        except Exception as e:
            print(f"Error loading face cascade: {e}")
    
    def detect_faces(self, frame):
        """
        Detect faces in frame
        
        Args:
            frame: BGR image
            
        Returns:
            List of (x, y, w, h) bounding boxes
        """
        if self.face_cascade is None:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return faces
    
    def detect_spoof(self, frame, face_bbox=None):
        """
        Detect if face is real or spoof
        
        Args:
            frame: BGR image
            face_bbox: (x, y, w, h) face bounding box (optional, will detect if None)
            
        Returns:
            (is_real, confidence, label, bbox)
            - is_real: True if real face, False if spoof
            - confidence: 0-100 confidence score
            - label: "real" or "spoof"
            - bbox: Face bounding box used
        """
        if not self.model_loaded:
            return True, 0, "unknown", None
        
        # Detect face if bbox not provided
        if face_bbox is None:
            faces = self.detect_faces(frame)
            if len(faces) == 0:
                return True, 0, "no_face", None
            face_bbox = faces[0]
        
        x, y, w, h = face_bbox
        
        try:
            # Extract face region with padding
            y1 = max(0, y - 5)
            y2 = min(frame.shape[0], y + h + 5)
            x1 = max(0, x - 5)
            x2 = min(frame.shape[1], x + w + 5)
            
            face = frame[y1:y2, x1:x2]
            
            if face.size == 0:
                return True, 0, "invalid_face", face_bbox
            
            # Preprocess for model
            resized_face = cv2.resize(face, (160, 160))
            resized_face = resized_face.astype("float") / 255.0
            resized_face = np.expand_dims(resized_face, axis=0)
            
            # Get prediction
            prediction = self.model.predict(resized_face, verbose=0)[0][0]
            
            # Interpret result (model outputs: >0.5 = spoof, <0.5 = real)
            if prediction > 0.5:
                is_real = False
                label = "spoof"
                confidence = prediction * 100
            else:
                is_real = True
                label = "real"
                confidence = (1 - prediction) * 100
            
            return is_real, confidence, label, face_bbox
            
        except Exception as e:
            print(f"Error in spoof detection: {e}")
            return True, 0, "error", face_bbox
    
    def process_frame(self, frame):
        """
        Process frame and detect all faces with spoof status
        
        Args:
            frame: BGR image
            
        Returns:
            List of (bbox, is_real, confidence, label) for each face
        """
        results = []
        faces = self.detect_faces(frame)
        
        for face_bbox in faces:
            is_real, confidence, label, _ = self.detect_spoof(frame, face_bbox)
            results.append((face_bbox, is_real, confidence, label))
        
        return results


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("Anti-Spoofing Detector Test")
    print("=" * 60)
    
    detector = AntiSpoofingDetector()
    
    if not detector.model_loaded:
        print("Model not loaded. Exiting.")
        exit(1)
    
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit")
    print("=" * 60)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        results = detector.process_frame(frame)
        
        for (x, y, w, h), is_real, confidence, label in results:
            # Set color based on result
            if is_real:
                color = (0, 255, 0)  # Green
                text = f"REAL ({confidence:.1f}%)"
            else:
                color = (0, 0, 255)  # Red
                text = f"SPOOF ({confidence:.1f}%)"
            
            # Draw rectangle and label
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        cv2.imshow("Anti-Spoofing Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
