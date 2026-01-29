"""
Combined System - AI Smart Sentinel
Unified face detection with Anti-Spoofing and Face Recognition

Flow:
1. Capture frame from camera
2. Detect faces
3. For each face:
   a. Run anti-spoofing check (real/spoof)
   b. Run face recognition (name/unknown)
4. Display results with colored rectangles and labels

Labels:
- Green: Known person + Real face → "Name ✓"
- Red: Spoof detected → "Name - SPOOF!" or "Unknown - SPOOF!"
- Yellow: Unknown person + Real face → "Unknown"
"""

import cv2
import numpy as np
import os
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from antispoofing_detector import AntiSpoofingDetector
from knn_face_verifier import KNNFaceVerifier

# Optional: Import injection detector if available
try:
    from injection_detector import InjectionDetector
    INJECTION_DETECTOR_AVAILABLE = True
except ImportError:
    INJECTION_DETECTOR_AVAILABLE = False
    print("Note: Injection detector not available")


class CombinedSystem:
    def __init__(self, camera_index=0):
        """
        Initialize Combined System
        
        Args:
            camera_index: Camera to use (0 for default webcam)
        """
        self.camera_index = camera_index
        
        # Initialize detectors
        print("=" * 60)
        print("AI Smart Sentinel - Combined System")
        print("=" * 60)
        
        print("\n[1/3] Loading Anti-Spoofing Detector...")
        self.spoof_detector = AntiSpoofingDetector()
        
        print("\n[2/3] Loading Face Verifier...")
        self.face_verifier = KNNFaceVerifier()
        
        print("\n[3/3] Loading Injection Detector...")
        if INJECTION_DETECTOR_AVAILABLE:
            self.injection_detector = InjectionDetector()
        else:
            self.injection_detector = None
        
        print("\n" + "=" * 60)
        print("System Ready!")
        print("=" * 60)
    
    def process_frame(self, frame):
        """
        Process a single frame through all detection stages
        
        Args:
            frame: BGR image
            
        Returns:
            List of detection results, each containing:
            {
                'bbox': (x, y, w, h),
                'is_real': bool,
                'is_known': bool,
                'name': str,
                'spoof_confidence': float,
                'identity_confidence': float,
                'label': str,
                'color': (B, G, R)
            }
        """
        results = []
        
        # Detect all faces using spoof detector's cascade
        faces = self.spoof_detector.detect_faces(frame)
        
        for face_bbox in faces:
            face_bbox = tuple(face_bbox)
            
            # Stage 1: Anti-spoofing check
            is_real, spoof_conf, spoof_label, _ = self.spoof_detector.detect_spoof(frame, face_bbox)
            
            # Stage 2: Face recognition
            name, id_conf, is_known, _ = self.face_verifier.verify_face(frame, face_bbox)
            
            # Determine label and color
            if is_real and is_known:
                # Known + Real → Green
                label = f"{name} ({id_conf:.0f}%)"
                color = (0, 255, 0)  # Green
            elif is_real and not is_known:
                # Unknown + Real → Treat as SPOOF (red)
                label = "SPOOF!"
                color = (0, 0, 255)  # Red
            elif not is_real and is_known:
                # Known + Spoof → Red
                label = f"{name} - SPOOF!"
                color = (0, 0, 255)  # Red
            else:
                # Unknown + Spoof → Red
                label = "Unknown - SPOOF!"
                color = (0, 0, 255)  # Red
            
            results.append({
                'bbox': face_bbox,
                'is_real': is_real,
                'is_known': is_known,
                'name': name if is_known else "Unknown",
                'spoof_confidence': spoof_conf,
                'identity_confidence': id_conf,
                'label': label,
                'color': color
            })
        
        return results
    
    def draw_results(self, frame, results):
        """
        Draw detection results on frame
        
        Args:
            frame: BGR image (will be modified in place)
            results: List of detection results from process_frame()
            
        Returns:
            Modified frame
        """
        for result in results:
            x, y, w, h = result['bbox']
            color = result['color']
            label = result['label']
            
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label background
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(frame, (x, y - label_size[1] - 10), 
                         (x + label_size[0] + 5, y), color, -1)
            
            # Draw label text
            cv2.putText(frame, label, (x + 2, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def run(self):
        """
        Run the combined system with camera feed
        """
        print("\n" + "=" * 60)
        print("Starting Camera...")
        print("Press 'q' to quit")
        print("Press 'r' to register a new face")
        print("=" * 60)
        
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Process frame
            results = self.process_frame(frame)
            
            # Draw results
            frame = self.draw_results(frame, results)
            
            # Add system info
            cv2.putText(frame, "AI Smart Sentinel", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Faces: {len(results)}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.putText(frame, "Press 'r' to register | 'q' to quit", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
            
            # Show frame
            cv2.imshow("AI Smart Sentinel", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Register new face
                cap.release()
                cv2.destroyAllWindows()
                
                name = input("\nEnter name for new face: ").strip()
                if name:
                    print(f"Registering {name}...")
                    success, msg = self.face_verifier.register_face_interactive(name)
                    print(msg)
                else:
                    print("Registration cancelled")
                
                # Reopen camera
                cap = cv2.VideoCapture(self.camera_index)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        cap.release()
        cv2.destroyAllWindows()
        print("\nCamera closed.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Smart Sentinel - Combined Face Detection System")
    parser.add_argument('-c', '--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    parser.add_argument('--register', type=str, default=None,
                       help='Register a new face with given name')
    
    args = parser.parse_args()
    
    # Create system
    system = CombinedSystem(camera_index=args.camera)
    
    # Check if registering
    if args.register:
        print(f"\nRegistering face for: {args.register}")
        success, msg = system.face_verifier.register_face_interactive(args.register)
        print(msg)
    else:
        # Run main loop
        system.run()


if __name__ == "__main__":
    main()
