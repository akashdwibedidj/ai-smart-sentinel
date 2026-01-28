"""
Video File Testing - AI Smart Sentinel
Test the complete system with a pre-recorded video file
Keeps ESP32-CAM and laptop camera tests unchanged
"""

import cv2
import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from liveness_detector import LivenessDetector
from face_verifier import FaceVerifier

def main():
    print("="*70)
    print("VIDEO FILE TESTING - AI Smart Sentinel")
    print("="*70)
    print("Test with a pre-recorded video file")
    print()
    
    # Get video file path
    video_path = input("Enter video file path (or press Enter for default): ").strip()
    
    if not video_path:
        # Default: Look for test videos in project
        possible_paths = [
            "test_video.mp4",
            "test_video.avi",
            "../test_video.mp4",
            "videos/test.mp4"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                video_path = path
                break
        
        if not video_path:
            print("\n❌ No video file found!")
            print("\nPlease provide a video file path, or place a video file in:")
            print("  - test_video.mp4")
            print("  - test_video.avi")
            print("\nYou can use any video with a face in it.")
            return
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"\n❌ Video file not found: {video_path}")
        return
    
    print(f"\n✓ Using video: {video_path}")
    print()
    
    # Initialize systems
    print("Initializing systems...")
    
    # Disable rPPG for video (usually too low FPS)
    liveness_detector = LivenessDetector(mode='passive', enable_rppg=False)
    
    # Adjust thresholds for video files (more lenient to avoid false positives from compression)
    liveness_detector.texture_threshold = 10  # Very lenient (video compression affects texture)
    liveness_detector.motion_threshold = 0.2  # Very lenient (allow more motion)
    liveness_detector.moire_threshold = 0.5   # Less sensitive (video compression creates patterns)
    liveness_detector.screen_glow_threshold = 0.6  # Less sensitive (video has uniform areas)
    liveness_detector.color_uniformity_threshold = 0.7  # Less sensitive
    liveness_detector.edge_sharpness_threshold = 0.8  # Less sensitive (compression affects edges)
    
    print("⚠️  Note: Thresholds adjusted for video file testing")
    print("   (Video compression can trigger false spoof detection)")
    print()
    
    face_verifier = FaceVerifier()
    
    # Check registered faces
    if not face_verifier.database:
        print("\n⚠️  WARNING: No faces registered in database!")
        print("   Face verification will be skipped.")
        use_face_verification = False
    else:
        print(f"✓ Found {len(face_verifier.database)} registered face(s):")
        for name in face_verifier.database.keys():
            print(f"  - {name}")
        use_face_verification = True
    
    print()
    print("System ready!")
    print()
    print("Controls:")
    print("  'q' - Quit")
    print("  'r' - Reset detection")
    print("  'p' - Pause/Resume")
    print("  SPACE - Step frame (when paused)")
    print("="*70)
    
    # Open video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"\n❌ Failed to open video file: {video_path}")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"\nVideo Info:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"  Total Frames: {total_frames}")
    print(f"  Duration: {total_frames/fps:.1f} seconds")
    print()
    
    # Face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # State
    frame_count = 0
    paused = False
    liveness_passed = False
    face_verified = False
    verified_name = None
    final_decision = None
    decision_time = None
    
    print("Starting playback...\n")
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("\n✓ Video ended. Press 'q' to quit or 'r' to restart.")
                paused = True
                continue
            
            frame_count += 1
        else:
            # Use last frame when paused
            ret = True
        
        # Detect face
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Liveness detection
        is_real, liveness_confidence, liveness_details = liveness_detector.hybrid_liveness_check(frame)
        
        # Draw face bbox
        if len(faces) > 0:
            x, y, w, h = faces[0]
            bbox_color = (0, 255, 0) if is_real else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), bbox_color, 2)
        
        # Face verification
        if is_real and use_face_verification and len(faces) > 0 and not liveness_passed:
            liveness_passed = True
            
            x, y, w, h = faces[0]
            face_roi = frame[y:y+h, x:x+w]
            
            # verify_face returns 4 values: (matched, similarity, person_id, details)
            match_found, similarity, match_name, details = face_verifier.verify_face(face_roi)
            
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
            liveness_passed = True
            final_decision = "ACCESS_GRANTED"
            decision_time = time.time()
        
        if not is_real and not final_decision:
            final_decision = "SPOOF_DETECTED"
        
        # Display
        y_pos = 30
        
        # Header
        cv2.putText(frame, "VIDEO TEST - AI SMART SENTINEL", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_pos += 30
        
        # Liveness result
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
        
        # Spoof reasons
        if not is_real and 'reasons' in liveness_details:
            reasons = liveness_details.get('reasons', [])
            if reasons:
                cv2.putText(frame, f"Reason: {reasons[0][:25]}", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 100, 100), 1)
                y_pos += 25
        
        y_pos += 5
        
        # Face verification
        if use_face_verification:
            if liveness_passed and face_verified:
                # Get person name if available
                display_name = face_verifier.names_database.get(verified_name, verified_name)
                cv2.putText(frame, f"PHASE 2: VERIFIED - {display_name}", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            elif liveness_passed and not face_verified:
                cv2.putText(frame, "PHASE 2: UNKNOWN PERSON", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "PHASE 2: Waiting...", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
            y_pos += 35
        
        # Final decision
        if final_decision:
            if final_decision == "ACCESS_GRANTED":
                decision_text = "ACCESS GRANTED"
                decision_color = (0, 255, 0)
            else:
                decision_text = "ACCESS DENIED"
                decision_color = (0, 0, 255)
            
            cv2.putText(frame, decision_text, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, decision_color, 2)
            
            # Auto-reset after 3 seconds
            if decision_time and (time.time() - decision_time > 3):
                liveness_passed = False
                face_verified = False
                verified_name = None
                final_decision = None
                decision_time = None
        
        # Video progress
        progress_text = f"Frame: {frame_count}/{total_frames}"
        cv2.putText(frame, progress_text, (frame.shape[1]-200, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Pause indicator
        if paused:
            cv2.putText(frame, "PAUSED", (frame.shape[1]//2 - 50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
        cv2.imshow("Video Test - AI Smart Sentinel", frame)
        
        # Handle keys
        wait_time = 1 if paused else max(1, int(1000/fps))
        key = cv2.waitKey(wait_time) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Reset
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_count = 0
            liveness_passed = False
            face_verified = False
            verified_name = None
            final_decision = None
            decision_time = None
            paused = False
            print("Video restarted")
        elif key == ord('p'):
            paused = not paused
            print("Paused" if paused else "Resumed")
        elif key == ord(' ') and paused:
            # Step one frame
            ret, frame = cap.read()
            if ret:
                frame_count += 1
        
        if cv2.getWindowProperty("Video Test - AI Smart Sentinel", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nTest completed.")
    print(f"Processed {frame_count} frames")

if __name__ == "__main__":
    main()
