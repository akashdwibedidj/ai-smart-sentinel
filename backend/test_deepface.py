"""
DeepFace Integration Test - AI Smart Sentinel
Tests liveness detection + DeepFace face recognition
More accurate than histogram comparison
"""

import cv2
import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from liveness_detector import LivenessDetector

# Try to import DeepFace
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️  DeepFace not installed. Install with: pip install deepface")

def main():
    if not DEEPFACE_AVAILABLE:
        print("\n❌ DeepFace is required for this test")
        print("Install it with: pip install deepface")
        return
    
    print("="*70)
    print("DEEPFACE INTEGRATION TEST - AI Smart Sentinel")
    print("="*70)
    print("Testing: Liveness Detection + DeepFace Recognition")
    print()
    
    # Get video file path
    video_path = input("Enter video file path (or press Enter for default): ").strip()
    
    if not video_path:
        video_path = "test_video.mp4"
        if not os.path.exists(video_path):
            print(f"\n❌ Video file not found: {video_path}")
            return
    
    if not os.path.exists(video_path):
        print(f"\n❌ Video file not found: {video_path}")
        return
    
    print(f"✓ Using video: {video_path}")
    print()
    
    # Database directory
    db_dir = "data/faces"
    if not os.path.exists(db_dir):
        print(f"❌ Database directory not found: {db_dir}")
        return
    
    # Check for registered faces
    registered_faces = []
    for person_id in os.listdir(db_dir):
        person_dir = os.path.join(db_dir, person_id)
        if os.path.isdir(person_dir):
            # Load ALL images for this person
            person_images = []
            for img_file in os.listdir(person_dir):
                if img_file.endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(person_dir, img_file)
                    person_images.append(img_path)
            
            if person_images:
                registered_faces.append({
                    'id': person_id,
                    'images': person_images  # Multiple images per person
                })
    
    if not registered_faces:
        print("❌ No registered faces found in database")
        return
    
    print(f"✓ Found {len(registered_faces)} registered person(s):")
    for face in registered_faces:
        print(f"  - {face['id']}: {len(face['images'])} photo(s)")
    print()
    
    # Initialize liveness detector
    print("Initializing liveness detector...")
    liveness_detector = LivenessDetector(mode='passive', enable_rppg=False)
    
    # Adjust thresholds for video
    liveness_detector.texture_threshold = 10
    liveness_detector.motion_threshold = 0.2
    liveness_detector.moire_threshold = 0.5
    liveness_detector.screen_glow_threshold = 0.6
    liveness_detector.color_uniformity_threshold = 0.7
    liveness_detector.edge_sharpness_threshold = 0.8
    
    print("✓ System ready!")
    print()
    print("DeepFace Models Available:")
    print("  - VGG-Face (default)")
    print("  - Facenet")
    print("  - OpenFace")
    print("  - DeepFace")
    print()
    print("Controls:")
    print("  'q' - Quit")
    print("  'r' - Reset")
    print("  'p' - Pause/Resume")
    print("="*70)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Failed to open video: {video_path}")
        return
    
    # Video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"\nVideo: {total_frames} frames @ {fps} FPS")
    print("Starting playback...\n")
    
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
    temp_face_path = "temp_face.jpg"
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("\n✓ Video ended")
                paused = True
                continue
            frame_count += 1
        else:
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
        
        # DeepFace verification (only if liveness passed)
        if is_real and len(faces) > 0 and not liveness_passed:
            liveness_passed = True
            
            # Extract face
            x, y, w, h = faces[0]
            face_roi = frame[y:y+h, x:x+w]
            
            # Save temp face
            cv2.imwrite(temp_face_path, face_roi)
            
            # Compare with registered faces using DeepFace
            best_match = None
            best_distance = float('inf')
            
            print(f"\n[Frame {frame_count}] Verifying with DeepFace...")
            
            for registered in registered_faces:
                person_id = registered['id']
                person_images = registered['images']
                
                # Compare against ALL images for this person
                person_best_distance = float('inf')
                person_verified = False
                
                for img_path in person_images:
                    try:
                        result = DeepFace.verify(
                            img1_path=temp_face_path,
                            img2_path=img_path,
                            model_name='VGG-Face',
                            enforce_detection=False
                        )
                        
                        distance = result['distance']
                        verified = result['verified']
                        
                        # Keep best match for this person
                        if distance < person_best_distance:
                            person_best_distance = distance
                            person_verified = verified
                    
                    except Exception as e:
                        pass  # Skip failed comparisons
                
                # Report best result for this person
                print(f"  {person_id}: distance={person_best_distance:.4f}, verified={person_verified}")
                
                # Keep overall best match
                if person_verified and person_best_distance < best_distance:
                    best_distance = person_best_distance
                    best_match = person_id
            
            if best_match:
                face_verified = True
                verified_name = best_match
                final_decision = "ACCESS_GRANTED"
                print(f"  ✓ MATCH: {best_match} (distance: {best_distance:.4f})")
            else:
                face_verified = False
                verified_name = None
                final_decision = "FACE_MISMATCH"
                print(f"  ✗ NO MATCH")
            
            decision_time = time.time()
        
        elif is_real and not liveness_passed:
            # No face verification needed
            pass
        
        if not is_real and not final_decision:
            final_decision = "SPOOF_DETECTED"
        
        # Display
        y_pos = 30
        
        # Header
        cv2.putText(frame, "DEEPFACE TEST - AI SMART SENTINEL", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_pos += 30
        
        # Liveness
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
        y_pos += 35
        
        # Face verification
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
        
        # Progress
        cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", 
                   (frame.shape[1]-200, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        if paused:
            cv2.putText(frame, "PAUSED", (frame.shape[1]//2 - 50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
        cv2.imshow("DeepFace Test - AI Smart Sentinel", frame)
        
        # Keys
        wait_time = 1 if paused else max(1, int(1000/fps))
        key = cv2.waitKey(wait_time) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('r'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_count = 0
            liveness_passed = False
            face_verified = False
            verified_name = None
            final_decision = None
            decision_time = None
            paused = False
        elif key == ord('p'):
            paused = not paused
        
        if cv2.getWindowProperty("DeepFace Test - AI Smart Sentinel", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    if os.path.exists(temp_face_path):
        os.remove(temp_face_path)
    
    print(f"\nTest completed. Processed {frame_count} frames")

if __name__ == "__main__":
    main()
