"""
Face Verifier - Hackathon Ready Version
Uses OpenCV face detection + simple face comparison
Fast, visual, works with low-quality webcams
"""

import cv2
import numpy as np
import os
import pickle

class FaceVerifier:
    def __init__(self, database_dir="data/faces"):
        self.database_dir = database_dir
        os.makedirs(database_dir, exist_ok=True)
        
        # Load face detector from Face-Liveness-Detection folder
        # Get absolute path to the models
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "..", "Face-Liveness-Detection")
        prototxt = os.path.join(model_path, "deploy.prototxt")
        caffemodel = os.path.join(model_path, "res10_300x300_ssd_iter_140000.caffemodel")
        
        self.face_net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
        
        # Confidence thresholds
        self.detection_confidence = 0.5
        self.match_threshold = 70  # Similarity percentage (0-100)
        
        # Load registered faces database
        self.database = self.load_database()
        
    def load_database(self):
        """Load registered face images"""
        db_file = os.path.join(self.database_dir, 'face_database.pkl')
        if os.path.exists(db_file):
            with open(db_file, 'rb') as f:
                return pickle.load(f)
        return {}
    
    def save_database(self):
        """Save face database to disk"""
        db_file = os.path.join(self.database_dir, 'face_database.pkl')
        with open(db_file, 'wb') as f:
            pickle.dump(self.database, f)
    
    def detect_face(self, frame):
        """
        Detect face in frame and return bounding box
        Returns: (face_detected, bbox, confidence)
        """
        (h, w) = frame.shape[:2]
        
        # Prepare image for face detection
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 
            1.0, 
            (300, 300),
            (104.0, 177.0, 123.0)
        )
        
        self.face_net.setInput(blob)
        detections = self.face_net.forward()
        
        # Find the detection with highest confidence
        best_confidence = 0
        best_box = None
        
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > self.detection_confidence and confidence > best_confidence:
                best_confidence = confidence
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                best_box = box.astype("int")
        
        if best_box is not None:
            return True, best_box, best_confidence
        
        return False, None, 0
    
    def extract_face_features(self, frame, bbox):
        """
        Extract face features using histogram comparison
        Simple but effective for hackathon demo
        """
        (startX, startY, endX, endY) = bbox
        
        # Ensure coordinates are within frame
        startX = max(0, startX)
        startY = max(0, startY)
        endX = min(frame.shape[1], endX)
        endY = min(frame.shape[0], endY)
        
        # Extract face ROI
        face = frame[startY:endY, startX:endX]
        
        if face.size == 0:
            return None
        
        # Resize to standard size
        face = cv2.resize(face, (100, 100))
        
        # Convert to grayscale
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        return {
            'face_image': face,
            'histogram': hist,
            'bbox': bbox
        }
    
    def compare_faces(self, features1, features2):
        """
        Compare two face features and return similarity percentage
        """
        # Compare histograms using correlation
        hist_similarity = cv2.compareHist(
            features1['histogram'],
            features2['histogram'],
            cv2.HISTCMP_CORREL
        )
        
        # Convert to percentage (correlation ranges from -1 to 1)
        similarity = (hist_similarity + 1) / 2 * 100
        
        # Also compare images directly using template matching
        img1 = cv2.cvtColor(features1['face_image'], cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(features2['face_image'], cv2.COLOR_BGR2GRAY)
        
        # Calculate structural similarity
        diff = cv2.absdiff(img1, img2)
        img_similarity = (1 - (np.mean(diff) / 255)) * 100
        
        # Weighted average
        final_similarity = (hist_similarity * 100 * 0.6) + (img_similarity * 0.4)
        
        return max(0, min(100, final_similarity))
    
    def register_face(self, frame, person_id):
        """
        Register a new face
        Returns: (success, message, bbox)
        """
        try:
            # Detect face
            detected, bbox, confidence = self.detect_face(frame)
            
            if not detected:
                return False, "No face detected in frame", None
            
            # Extract features
            features = self.extract_face_features(frame, bbox)
            
            if features is None:
                return False, "Could not extract face features", None
            
            # Save to database
            self.database[person_id] = features
            self.save_database()
            
            # Also save the full frame for reference
            person_dir = os.path.join(self.database_dir, person_id)
            os.makedirs(person_dir, exist_ok=True)
            cv2.imwrite(os.path.join(person_dir, f"{person_id}.jpg"), frame)
            
            return True, f"Face registered successfully for {person_id}", bbox
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None
    
    def verify_face(self, frame, person_id=None):
        """
        Verify face against registered database
        Returns: (matched, similarity, person_id, details)
        """
        try:
            # Detect face
            detected, bbox, det_confidence = self.detect_face(frame)
            
            if not detected:
                return False, 0, "unknown", {
                    "error": "No face detected",
                    "bbox": None,
                    "detection_confidence": 0
                }
            
            # Extract features
            features = self.extract_face_features(frame, bbox)
            
            if features is None:
                return False, 0, "unknown", {
                    "error": "Could not extract face features",
                    "bbox": bbox,
                    "detection_confidence": det_confidence * 100
                }
            
            # If no faces registered
            if len(self.database) == 0:
                return False, 0, "unknown", {
                    "error": "No registered faces in database",
                    "bbox": bbox,
                    "detection_confidence": det_confidence * 100
                }
            
            # Compare with registered faces
            best_match = None
            best_similarity = 0
            
            for pid, stored_features in self.database.items():
                # Skip if specific person_id provided and doesn't match
                if person_id and pid != person_id:
                    continue
                
                # Calculate similarity
                similarity = self.compare_faces(features, stored_features)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = pid
            
            # Determine if it's a match
            matched = best_similarity >= self.match_threshold
            
            return matched, best_similarity, best_match, {
                "bbox": bbox,
                "detection_confidence": det_confidence * 100,
                "method": "histogram_comparison"
            }
            
        except Exception as e:
            return False, 0, "unknown", {
                "error": str(e),
                "bbox": None
            }
    
    def get_registered_faces(self):
        """Get list of all registered person IDs"""
        return list(self.database.keys())


# Quick test
if __name__ == "__main__":
    verifier = FaceVerifier()
    cap = cv2.VideoCapture(0)
    
    print("="*60)
    print("AI Smart Sentinel - Face Verification Test")
    print("="*60)
    print("Controls:")
    print("  'r' - Register a new face")
    print("  'v' - Verify current face")
    print("  'l' - List registered faces")
    print("  'q' - Quit")
    print("="*60)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Always show face detection with bounding box
        detected, bbox, confidence = verifier.detect_face(frame)
        
        if detected:
            (startX, startY, endX, endY) = bbox
            # Draw green rectangle around face
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            # Show detection confidence
            cv2.putText(frame, f"Face Detected: {confidence*100:.1f}%", 
                       (startX, startY-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # Show "No face detected" message
            cv2.putText(frame, "No face detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show instructions
        cv2.putText(frame, "Press: r=Register | v=Verify | l=List | q=Quit", 
                   (10, frame.shape[0]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('r'):
            if detected:
                person_id = input("\nEnter Person ID to register: ")
                success, message, bbox = verifier.register_face(frame, person_id)
                print(f"{'✓' if success else '✗'} {message}")
            else:
                print("✗ No face detected. Please position your face in frame.")
        
        elif key == ord('v'):
            matched, similarity, person_id, details = verifier.verify_face(frame)
            print(f"\n{'='*60}")
            if matched:
                print(f"✓ ACCESS GRANTED")
                print(f"  Person: {person_id}")
                print(f"  Similarity: {similarity:.1f}%")
            else:
                print(f"✗ ACCESS DENIED")
                print(f"  Best Match: {person_id if person_id != 'unknown' else 'None'}")
                print(f"  Similarity: {similarity:.1f}%")
                print(f"  Threshold: {verifier.match_threshold}%")
            print(f"{'='*60}")
        
        elif key == ord('l'):
            faces = verifier.get_registered_faces()
            print(f"\nRegistered Faces ({len(faces)}):")
            for face in faces:
                print(f"  - {face}")
        
        elif key == ord('q'):
            break
        
        cv2.imshow("AI Smart Sentinel - Face Verification", frame)
        
        # Check if window was closed
        if cv2.getWindowProperty("AI Smart Sentinel - Face Verification", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nCamera closed successfully.")