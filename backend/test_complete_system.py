"""
Complete System Test: ESP32-CAM + Liveness Detection + Face Verification
Tests the full pipeline from camera to access decision
"""

import cv2
import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from liveness_detector import LivenessDetector
from face_verifier import FaceVerifier

# ESP32-CAM Configuration
ESP32_CAM_IP = "192.168.1.11"
STREAM_URL = f"http://{ESP32_CAM_IP}:81/stream"

def main():
    print("="*70)
    print("COMPLETE SYSTEM TEST - AI Smart Sentinel")
    print("="*70)
    print("Testing: Liveness Detection + Face Verification")
    print(f"Camera: ESP32-CAM at {ESP32_CAM_IP}")
    print()
    
    # Initialize both systems
    print("Initializing systems...")
    
    # IMPORTANT: Disable rPPG for ESP32-CAM (too slow, low FPS)
    # ESP32-CAM typically runs at 5-15 FPS, rPPG needs 20+ FPS
    liveness_detector = LivenessDetector(mode='passive', enable_rppg=False)
    
    # Adjust thresholds for ESP32-CAM (lower quality)
    liveness_detector.texture_threshold = 15  # More lenient
    liveness_detector.motion_threshold = 0.3  # More lenient
    liveness_detector.moire_threshold = 0.7   # Less sensitive
    
    face_verifier = FaceVerifier()
    
    # Check if any faces are registered
    if not face_verifier.database:
        print("\n⚠️  WARNING: No faces registered in database!")
        print("   Face verification will be skipped.")
        print("   To register faces, run: py backend/face_verifier.py")
        print()
        use_face_verification = False
    else:
        print(f"✓ Found {len(face_verifier.database)} registered face(s):")
        for name in face_verifier.database.keys():
            print(f"  - {name}")
        print()
        use_face_verification = True
    
    print("System ready!")
    print()
    print("⚠️  NOTE: rPPG heartbeat detection is DISABLED for ESP32-CAM")
    print("   (ESP32-CAM FPS too low for accurate heartbeat detection)")
    print("   Using Phase 1 & 2 liveness checks only")
    print()
    print("TESTING PHASES:")
    print("1. Liveness Detection (instant)")
    print("   - Moiré patterns, motion, texture")
    print("   - Screen glow, color uniformity")
    print()
    if use_face_verification:
        print("2. Face Verification")
        print("   - Compare to registered faces")
        print("   - Calculate similarity score")
        print()
    print("3. Final Decision")
    print("   - GRANT or DENY access")
    print()
    print("Press 'q' to quit, 'r' to reset")
    print("="*70)
    
    # Connect to ESP32-CAM
    cap = cv2.VideoCapture(STREAM_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("✗ Failed to connect to ESP32-CAM")
        return
    
    print("\n✓ Connected to ESP32-CAM stream\n")
    
    # Face detector for bbox
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # State tracking
    frame_count = 0
    start_time = time.time()
    fps = 0
    fps_counter = 0
    flip_frame = False  # Set to True if image is mirrored
    
    # Decision state
    liveness_passed = False
    face_verified = False
    verified_name = None
    final_decision = None
    decision_time = None
    
    print("\n💡 TIP: If image is mirrored, press 'f' to flip")
    print("="*70)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
        
        # Flip frame if needed
        if flip_frame:
            frame = cv2.flip(frame, 1)
        
        frame_count += 1
        fps_counter += 1
        
        # Calculate FPS
        if time.time() - start_time >= 1.0:
            fps = fps_counter
            fps_counter = 0
            start_time = time.time()
        
        # Detect face
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # PHASE 1: Liveness Detection
        is_real, liveness_confidence, liveness_details = liveness_detector.hybrid_liveness_check(frame)
        
        # Draw face bbox
        if len(faces) > 0:
            x, y, w, h = faces[0]
            
            # Color based on liveness
            if is_real:
                bbox_color = (0, 255, 0)  # Green
            else:
                bbox_color = (0, 0, 255)  # Red
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), bbox_color, 2)
            
            # Draw rPPG ROI
            roi_y = y + int(h * 0.1)
            roi_h = int(h * 0.3)
            roi_x = x + int(w * 0.2)
            roi_w = int(w * 0.6)
            cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h),
                         (0, 255, 255), 1)
        
        # PHASE 2: Face Verification (only if liveness passed)
        if is_real and use_face_verification and len(faces) > 0 and not liveness_passed:
            # Without rPPG, we can verify immediately
            liveness_passed = True
            
            # Now verify face
            x, y, w, h = faces[0]
            face_roi = frame[y:y+h, x:x+w]
            
            match_found, match_name, similarity = face_verifier.verify_face(face_roi)
            
            if match_found:
                face_verified = True
                verified_name = match_name
                final_decision = "ACCESS_GRANTED"
            else:
                face_verified = False
                verified_name = None
                final_decision = "FACE_MISMATCH"
            
            decision_time = time.time()
        
        elif is_real and not use_face_verification and not liveness_passed:
            # No face verification, just liveness
            liveness_passed = True
            final_decision = "ACCESS_GRANTED"
            decision_time = time.time()
        
        # If liveness failed
        if not is_real and not final_decision:
            final_decision = "SPOOF_DETECTED"
        
        # Display results
        y_pos = 30
        
        # Header
        cv2.putText(frame, "AI SMART SENTINEL", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_pos += 35
        
        # Phase 1: Liveness
        if is_real:
            status_text = "PHASE 1: REAL FACE"
            status_color = (0, 255, 0)
        else:
            status_text = f"PHASE 1: {liveness_details.get('decision', 'SPOOF')}"
            status_color = (0, 0, 255)
        
        cv2.putText(frame, status_text, (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        y_pos += 25
        
        cv2.putText(frame, f"Confidence: {liveness_confidence:.1f}%", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
        y_pos += 30
        
        # Show spoof indicators if denied
        if not is_real and 'reasons' in liveness_details:
            reasons = liveness_details.get('reasons', [])
            if reasons:
                cv2.putText(frame, f"Reason: {reasons[0][:20]}", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 100, 100), 1)
                y_pos += 25
        
        y_pos += 5
        
        # Phase 2: Face Verification
        if use_face_verification:
            if liveness_passed and face_verified:
                cv2.putText(frame, f"PHASE 2: VERIFIED - {verified_name}", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            elif liveness_passed and not face_verified:
                cv2.putText(frame, "PHASE 2: UNKNOWN PERSON", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "PHASE 2: Waiting...", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
            y_pos += 35
        
        # Final Decision
        if final_decision:
            if final_decision == "ACCESS_GRANTED":
                decision_text = "ACCESS GRANTED"
                decision_color = (0, 255, 0)
            else:
                decision_text = "ACCESS DENIED"
                decision_color = (0, 0, 255)
            
            cv2.putText(frame, decision_text, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, decision_color, 2)
            
            # Show for 3 seconds then reset
            if decision_time and (time.time() - decision_time > 3):
                liveness_passed = False
                face_verified = False
                verified_name = None
                final_decision = None
                decision_time = None
        
        # FPS
        cv2.putText(frame, f"FPS: {fps}", (frame.shape[1]-100, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        cv2.imshow("AI Smart Sentinel - Complete System", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Reset
            liveness_passed = False
            face_verified = False
            verified_name = None
            final_decision = None
            decision_time = None
        elif key == ord('f'):
            # Flip frame
            flip_frame = not flip_frame
            print(f"Frame flip: {'ON' if flip_frame else 'OFF'}")
        
        if cv2.getWindowProperty("AI Smart Sentinel - Complete System", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nTest completed.")
    print(f"Total frames: {frame_count}")

if __name__ == "__main__":
    main()
