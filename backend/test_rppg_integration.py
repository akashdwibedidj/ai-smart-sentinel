"""
Test Script for Phase 3 rPPG Heartbeat Detection
Tests the integrated liveness detector with rPPG
"""

import cv2
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from liveness_detector import LivenessDetector

def main():
    print("="*70)
    print("Phase 3 rPPG Heartbeat Detection - Integration Test")
    print("="*70)
    print("This test demonstrates the full liveness detection system")
    print("including Phase 1, 2, and 3 features.")
    print()
    print("Phase 1: Moiré patterns, motion, texture")
    print("Phase 2: Screen glow, color uniformity, edge sharpness")
    print("Phase 3: rPPG heartbeat detection (PRIMARY)")
    print()
    print("Instructions:")
    print("1. Position your face in the frame")
    print("2. Stay still for 5-10 seconds")
    print("3. The system will detect your heartbeat")
    print("4. Try with a photo/phone screen to see spoof detection")
    print()
    print("Press 'q' to quit")
    print("="*70)
    
    # Initialize detector with rPPG enabled
    detector = LivenessDetector(mode='passive', enable_rppg=True)
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Simple face detector for bbox
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Detect face for rPPG ROI
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Run hybrid liveness check
        is_real, confidence, details = detector.hybrid_liveness_check(frame)
        
        # Draw face and ROI if detected
        if len(faces) > 0:
            x, y, w, h = faces[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Draw rPPG ROI (forehead)
            roi_y = y + int(h * 0.1)
            roi_h = int(h * 0.3)
            roi_x = x + int(w * 0.2)
            roi_w = int(w * 0.6)
            cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h),
                         (0, 255, 255), 2)
            cv2.putText(frame, "rPPG ROI", (roi_x, roi_y-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Display main result
        if is_real:
            status = "✓ REAL FACE"
            color = (0, 255, 0)
        else:
            status = f"✗ {details.get('decision', 'SPOOF')}"
            color = (0, 0, 255)
        
        cv2.putText(frame, status, (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, f"Confidence: {confidence:.1f}%", (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Display heartbeat info
        y_offset = 120
        if 'heartbeat' in details:
            hb_details = details['heartbeat']
            
            if hb_details.get('status') == 'collecting_data':
                progress = hb_details.get('progress', 0)
                cv2.putText(frame, f"♥ Collecting: {progress:.0f}%", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            elif hb_details.get('detected'):
                bpm = hb_details.get('bpm', 0)
                cv2.putText(frame, f"♥ {bpm:.0f} BPM", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                y_offset += 35
                snr = hb_details.get('snr', 0)
                cv2.putText(frame, f"SNR: {snr:.1f}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            else:
                cv2.putText(frame, "♥ No heartbeat", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Display spoof indicators
        y_offset += 40
        if 'reasons' in details and details['reasons']:
            cv2.putText(frame, "Indicators:", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_offset += 25
            for reason in details['reasons'][:4]:  # Show max 4
                cv2.putText(frame, f"- {reason}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y_offset += 20
        
        # Display frame count
        cv2.putText(frame, f"Frame: {frame_count}", (frame.shape[1]-150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        cv2.imshow("Phase 3 rPPG Liveness Detection", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        if cv2.getWindowProperty("Phase 3 rPPG Liveness Detection", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nTest completed.")
    print(f"Total frames processed: {frame_count}")

if __name__ == "__main__":
    main()
