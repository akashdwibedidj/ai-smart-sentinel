"""
Liveness Detector Test - Phone Camera (Index 2)
Runs the liveness detector exclusively using the connected phone camera.
"""

import cv2
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from liveness_detector import LivenessDetector

def main():
    CAMERA_INDEX = 2  # Hardcoded for your phone
    
    print("="*60)
    print(f"Liveness Detection Test - Camera {CAMERA_INDEX} (Phone)")
    print("="*60)
    print("Instructions:")
    print("1. Point camera at your face -> Should say 'REAL FACE' (Green)")
    print("2. Point at a photo/screen -> Should say 'SPOOF' (Red)")
    print("Press 'q' to quit")
    print("="*60)
    
    print(f"Opening Camera {CAMERA_INDEX}...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    # Set high resolution for better texture analysis
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print(f"❌ Could not open camera {CAMERA_INDEX}. Is it connected?")
        print("Try running 'py backend/find_phone_camera.py' again to check index.")
        return

    detector = LivenessDetector()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        
        # Run liveness check
        is_real, confidence, details = detector.hybrid_liveness_check(frame)
        
        # Display results
        if is_real:
            status = "REAL FACE"
            color = (0, 255, 0)
        else:
            status = f"SPOOF: {details['decision']}"
            color = (0, 0, 255)
        
        # Draw main status
        cv2.putText(frame, status, (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, f"Conf: {confidence:.1f}%", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Show specific reasons if spoof
        if not is_real and 'reasons' in details:
            y_pos = 130
            for reason in details['reasons'][:2]:
                cv2.putText(frame, f"- {reason}", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y_pos += 25
                
        cv2.imshow(f"Liveness Test (Camera {CAMERA_INDEX})", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
