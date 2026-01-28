"""
Multi-Shot Face Registration - AI Smart Sentinel
Captures multiple photos from different angles for better recognition
Works with webcam, ESP32-CAM, or video file
"""

import cv2
import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("="*70)
    print("MULTI-SHOT FACE REGISTRATION")
    print("="*70)
    print("Capture 5-10 photos from different angles for better recognition")
    print()
    
    # Get person details
    person_id = input("Enter Person ID (e.g., '01', 'akash'): ").strip()
    if not person_id:
        print("Error: Person ID required!")
        return
    
    person_name = input("Enter Person Name (e.g., 'Akash DJ'): ").strip()
    
    # Choose camera source
    print("\nCamera Source:")
    print("1. Laptop webcam")
    print("2. ESP32-CAM")
    print("3. Video file")
    choice = input("Choose (1/2/3): ").strip()
    
    if choice == "1":
        source = 0  # Laptop webcam
        source_type = "webcam"
    elif choice == "2":
        esp32_ip = input("Enter ESP32-CAM IP (default: 192.168.1.11): ").strip()
        if not esp32_ip:
            esp32_ip = "192.168.1.11"
        source = f"http://{esp32_ip}:81/stream"
        source_type = "esp32"
    elif choice == "3":
        source = input("Enter video file path: ").strip()
        if not source or not os.path.exists(source):
            print("Error: Video file not found!")
            return
        source_type = "video"
    else:
        print("Invalid choice!")
        return
    
    print(f"\n✓ Using {source_type}")
    print()
    
    # Create person directory
    person_dir = os.path.join("data", "faces", person_id)
    os.makedirs(person_dir, exist_ok=True)
    
    # Open camera/video
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"❌ Failed to open {source_type}")
        return
    
    print("✓ Camera opened")
    print()
    print("INSTRUCTIONS:")
    print("  - Position your face in the frame")
    print("  - Press SPACE to capture (5-10 photos)")
    print("  - Move your head slightly between captures:")
    print("    * Front view")
    print("    * Slight left turn")
    print("    * Slight right turn")
    print("    * Slight up tilt")
    print("    * Slight down tilt")
    print("  - Press 'q' when done (minimum 3 photos)")
    print()
    
    # Face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    captured_count = 0
    target_count = 5
    
    while True:
        ret, frame = cap.read()
        if not ret:
            if source_type == "video":
                # Loop video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                print("❌ Failed to read frame")
                break
        
        # Detect face
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Draw face box
        display_frame = frame.copy()
        if len(faces) > 0:
            x, y, w, h = faces[0]
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Show face quality
            face_size = w * h
            if face_size > 10000:
                quality = "Good"
                quality_color = (0, 255, 0)
            elif face_size > 5000:
                quality = "OK"
                quality_color = (0, 255, 255)
            else:
                quality = "Too small"
                quality_color = (0, 0, 255)
            
            cv2.putText(display_frame, f"Quality: {quality}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, quality_color, 2)
        else:
            cv2.putText(display_frame, "No face detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show progress
        cv2.putText(display_frame, f"Captured: {captured_count}/{target_count}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if captured_count >= target_count:
            cv2.putText(display_frame, "Press 'q' to finish", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame, "Press SPACE to capture", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Multi-Shot Registration", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space to capture
            if len(faces) > 0:
                # Save full frame
                filename = f"{person_id}_{captured_count+1:02d}.jpg"
                filepath = os.path.join(person_dir, filename)
                cv2.imwrite(filepath, frame)
                
                captured_count += 1
                print(f"✓ Captured {captured_count}/{target_count}: {filename}")
                
                # Visual feedback
                time.sleep(0.3)
            else:
                print("✗ No face detected - try again")
        
        elif key == ord('q'):
            if captured_count >= 3:
                break
            else:
                print(f"⚠️  Need at least 3 photos (have {captured_count})")
        
        if cv2.getWindowProperty("Multi-Shot Registration", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if captured_count < 3:
        print("\n❌ Registration cancelled - not enough photos")
        return
    
    # Save metadata
    print(f"\n✓ Registration complete!")
    print(f"  Person ID: {person_id}")
    if person_name:
        print(f"  Name: {person_name}")
    print(f"  Photos captured: {captured_count}")
    print(f"  Saved to: {person_dir}")
    
    # Save name to database
    if person_name:
        try:
            import pickle
            names_file = "data/faces/names_database.pkl"
            
            # Load existing names
            if os.path.exists(names_file):
                with open(names_file, 'rb') as f:
                    names_db = pickle.load(f)
            else:
                names_db = {}
            
            # Add new name
            names_db[person_id] = person_name
            
            # Save
            with open(names_file, 'wb') as f:
                pickle.dump(names_db, f)
            
            print(f"  ✓ Name saved to database")
        except Exception as e:
            print(f"  ⚠️  Could not save name: {e}")
    
    print("\n✅ Ready for testing!")
    print(f"   Run: py backend\\test_deepface.py")

if __name__ == "__main__":
    main()
