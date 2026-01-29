"""
KNN Face Verifier - Wrapper for Face Recognition Project
Uses the KNN model from face_recognition_project-main
Handles face registration and verification
"""

import cv2
import pickle
import numpy as np
import os
from sklearn.neighbors import KNeighborsClassifier


class KNNFaceVerifier:
    def __init__(self):
        """Initialize KNN Face Verifier"""
        # Paths to data files (relative to project root)
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.project_root, "face_recognition_project-main", "data")
        
        # File paths
        self.names_file = os.path.join(self.data_dir, "names.pkl")
        self.faces_file = os.path.join(self.data_dir, "faces_data.pkl")
        self.cascade_file = os.path.join(self.data_dir, "haarcascade_frontalface_default.xml")
        
        # Load face cascade
        self.face_cascade = None
        self._load_cascade()
        
        # KNN model
        self.knn = None
        self.names = []
        self.faces_data = None
        self.model_loaded = False
        
        # Load existing model if available
        self._load_model()
    
    def _load_cascade(self):
        """Load Haar Cascade for face detection"""
        try:
            if os.path.exists(self.cascade_file):
                self.face_cascade = cv2.CascadeClassifier(self.cascade_file)
            else:
                # Fallback to OpenCV's built-in cascade
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
            print("Face cascade loaded for KNN verifier!")
        except Exception as e:
            print(f"Error loading face cascade: {e}")
    
    def _load_model(self):
        """Load existing KNN model and data"""
        try:
            if os.path.exists(self.names_file) and os.path.exists(self.faces_file):
                # Load names
                with open(self.names_file, 'rb') as f:
                    self.names = pickle.load(f)
                
                # Load faces data
                with open(self.faces_file, 'rb') as f:
                    self.faces_data = pickle.load(f)
                
                # Train KNN model
                if len(self.names) > 0 and self.faces_data is not None:
                    self.knn = KNeighborsClassifier(n_neighbors=5)
                    self.knn.fit(self.faces_data, self.names)
                    self.model_loaded = True
                    
                    # Get unique names
                    unique_names = list(set(self.names))
                    print(f"KNN model loaded! {len(unique_names)} persons registered: {unique_names}")
                else:
                    print("No face data found. Please register faces first.")
            else:
                print("No existing face database found. Please register faces first.")
                
        except Exception as e:
            print(f"Error loading KNN model: {e}")
            self.model_loaded = False
    
    def _save_data(self):
        """Save names and faces data to disk"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            with open(self.names_file, 'wb') as f:
                pickle.dump(self.names, f)
            
            with open(self.faces_file, 'wb') as f:
                pickle.dump(self.faces_data, f)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
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
        return list(faces)
    
    def extract_face_features(self, frame, face_bbox):
        """
        Extract face features for KNN
        
        Args:
            frame: BGR image
            face_bbox: (x, y, w, h) bounding box
            
        Returns:
            Flattened face feature array (2500,) or None
        """
        try:
            x, y, w, h = face_bbox
            
            # Crop face
            crop_img = frame[y:y+h, x:x+w]
            
            # Convert to grayscale
            crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
            
            # Resize to 50x50 and flatten
            resized_img = cv2.resize(crop_img_gray, (50, 50))
            features = resized_img.flatten()
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def verify_face(self, frame, face_bbox=None):
        """
        Verify face against registered database
        
        Args:
            frame: BGR image
            face_bbox: (x, y, w, h) face bounding box (optional, will detect if None)
            
        Returns:
            (name, confidence, is_known, bbox)
            - name: Person name or "Unknown"
            - confidence: 0-100 confidence score
            - is_known: True if person is registered
            - bbox: Face bounding box used
        """
        if not self.model_loaded:
            return "No Model", 0, False, None
        
        # Detect face if bbox not provided
        if face_bbox is None:
            faces = self.detect_faces(frame)
            if len(faces) == 0:
                return "No Face", 0, False, None
            face_bbox = tuple(faces[0])
        
        # Extract features
        features = self.extract_face_features(frame, face_bbox)
        if features is None:
            return "Error", 0, False, face_bbox
        
        try:
            # Reshape for prediction
            features = features.reshape(1, -1)
            
            # Get prediction and probabilities
            prediction = self.knn.predict(features)[0]
            
            # Get distances to all neighbors
            distances, indices = self.knn.kneighbors(features, n_neighbors=5)
            avg_distance = np.mean(distances)
            
            # Calculate confidence (lower distance = higher confidence)
            # Normalize distance to confidence score
            # Typical distances range from 0 (perfect match) to ~5000+ (no match)
            max_distance = 3000  # Threshold for "unknown"
            
            if avg_distance < max_distance:
                confidence = max(0, 100 - (avg_distance / max_distance * 100))
                is_known = confidence > 40  # Confidence threshold
            else:
                confidence = 0
                is_known = False
            
            if is_known:
                return prediction, confidence, True, face_bbox
            else:
                return "Unknown", confidence, False, face_bbox
                
        except Exception as e:
            print(f"Error in verification: {e}")
            return "Error", 0, False, face_bbox
    
    def process_frame(self, frame):
        """
        Process frame and verify all faces
        
        Args:
            frame: BGR image
            
        Returns:
            List of (bbox, name, confidence, is_known) for each face
        """
        results = []
        faces = self.detect_faces(frame)
        
        for face_bbox in faces:
            name, confidence, is_known, _ = self.verify_face(frame, tuple(face_bbox))
            results.append((tuple(face_bbox), name, confidence, is_known))
        
        return results
    
    def get_registered_persons(self):
        """Get list of registered person names"""
        if self.names:
            return list(set(self.names))
        return []
    
    def register_face(self, frame, person_id, num_augmentations=10):
        """
        Register a face from a single frame (for API use)
        
        Args:
            frame: BGR image
            person_id: Person's name
            num_augmentations: Number of augmented samples to create
            
        Returns:
            (success, message)
        """
        try:
            # Detect face in frame
            faces = self.detect_faces(frame)
            if len(faces) == 0:
                return False, "No face detected in image"
            
            # Get the largest face
            face_bbox = max(faces, key=lambda f: f[2] * f[3])
            face_bbox = tuple(face_bbox)
            
            # Extract features
            features = self.extract_face_features(frame, face_bbox)
            if features is None:
                return False, "Could not extract face features"
            
            # Create augmented samples by slightly varying the face crop
            x, y, w, h = face_bbox
            faces_data = [features]
            
            for i in range(num_augmentations - 1):
                # Slight random variations
                dx = np.random.randint(-5, 6)
                dy = np.random.randint(-5, 6)
                
                new_x = max(0, x + dx)
                new_y = max(0, y + dy)
                
                aug_features = self.extract_face_features(frame, (new_x, new_y, w, h))
                if aug_features is not None:
                    faces_data.append(aug_features)
            
            # Convert to numpy array
            new_faces = np.array(faces_data)
            new_names = [person_id] * len(faces_data)
            
            # Add to existing data
            if self.faces_data is not None:
                self.faces_data = np.append(self.faces_data, new_faces, axis=0)
                self.names = self.names + new_names
            else:
                self.faces_data = new_faces
                self.names = new_names
            
            # Save and retrain
            self._save_data()
            
            # Retrain KNN
            self.knn = KNeighborsClassifier(n_neighbors=5)
            self.knn.fit(self.faces_data, self.names)
            self.model_loaded = True
            
            return True, f"Successfully registered {person_id} with {len(faces_data)} samples"
            
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def register_face_interactive(self, name, num_samples=100, camera_index=0):
        """
        Interactive face registration (similar to add_faces.py)
        
        Args:
            name: Person's name
            num_samples: Number of face samples to capture (default 100)
            camera_index: Camera to use (default 0)
            
        Returns:
            (success, message)
        """
        print(f"Registering face for: {name}")
        print(f"Capturing {num_samples} samples...")
        print("Press 'q' to cancel")
        
        video = cv2.VideoCapture(camera_index)
        faces_data = []
        i = 0
        
        while True:
            ret, frame = video.read()
            if not ret:
                break
            
            faces = self.detect_faces(frame)
            
            for (x, y, w, h) in faces:
                # Extract and process face
                features = self.extract_face_features(frame, (x, y, w, h))
                
                if features is not None and len(faces_data) < num_samples and i % 10 == 0:
                    faces_data.append(features)
                
                i += 1
                
                # Draw progress
                cv2.putText(frame, f"Samples: {len(faces_data)}/{num_samples}", 
                           (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
            
            cv2.imshow("Face Registration", frame)
            
            k = cv2.waitKey(1)
            if k == ord('q') or len(faces_data) >= num_samples:
                break
        
        video.release()
        cv2.destroyAllWindows()
        
        if len(faces_data) < num_samples:
            return False, f"Only captured {len(faces_data)} samples, need {num_samples}"
        
        # Convert to numpy array
        new_faces = np.array(faces_data)
        new_names = [name] * num_samples
        
        # Add to existing data
        if self.faces_data is not None:
            self.faces_data = np.append(self.faces_data, new_faces, axis=0)
            self.names = self.names + new_names
        else:
            self.faces_data = new_faces
            self.names = new_names
        
        # Save and retrain
        self._save_data()
        
        # Retrain KNN
        self.knn = KNeighborsClassifier(n_neighbors=5)
        self.knn.fit(self.faces_data, self.names)
        self.model_loaded = True
        
        return True, f"Successfully registered {name} with {num_samples} samples"


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("KNN Face Verifier Test")
    print("=" * 60)
    
    verifier = KNNFaceVerifier()
    
    print(f"\nRegistered persons: {verifier.get_registered_persons()}")
    
    if not verifier.model_loaded:
        print("\nNo faces registered. Would you like to register a face? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            name = input("Enter name: ").strip()
            success, msg = verifier.register_face_interactive(name)
            print(msg)
    
    print("\nStarting camera for face verification...")
    print("Press 'q' to quit")
    print("=" * 60)
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        results = verifier.process_frame(frame)
        
        for (x, y, w, h), name, confidence, is_known in results:
            # Set color based on result
            if is_known:
                color = (0, 255, 0)  # Green
                text = f"{name} ({confidence:.1f}%)"
            else:
                color = (0, 255, 255)  # Yellow
                text = f"Unknown ({confidence:.1f}%)"
            
            # Draw rectangle and label
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        cv2.imshow("KNN Face Verifier Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
