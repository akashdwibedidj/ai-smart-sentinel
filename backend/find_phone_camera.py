"""
Camera Finder Tool
Scans for available cameras and lets you test each one.
Useful for finding external cameras or phone cameras connected via USB/WiFi.
"""

import cv2
import time

def list_cameras():
    print("="*60)
    print("Scanning for available cameras...")
    print("="*60)
    
    available_cameras = []
    
    # Check first 5 indices
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"Index {i}: Found ✓ ({w}x{h})")
                available_cameras.append(i)
            else:
                print(f"Index {i}: Failed to read frame")
            cap.release()
        else:
            print(f"Index {i}: Not found")
            
    return available_cameras

def test_camera(index):
    print(f"\nOpening Camera Index {index}...")
    print("Press 'q' again to close detection.")
    
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"Could not open camera {index}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        cv2.putText(frame, f"Camera Index: {index}", (30, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to close", (30, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                   
        cv2.imshow(f"Testing Camera {index}", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

def main():
    cameras = list_cameras()
    
    if not cameras:
        print("\n❌ No cameras found!")
        return
        
    print(f"\nFound cameras at indices: {cameras}")
    
    while True:
        print("\nWhich camera do you want to test?")
        try:
            selection = input(f"Enter index ({'/'.join(map(str, cameras))}) or 'x' to exit: ")
            if selection.lower() == 'x':
                break
                
            idx = int(selection)
            if idx in cameras:
                test_camera(idx)
            else:
                print("Invalid index")
        except ValueError:
            print("Invalid input")

if __name__ == "__main__":
    main()
