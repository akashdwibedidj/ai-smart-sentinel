"""
ESP32-CAM Integration Test for Phase 3 rPPG Heartbeat Detection
Tests the liveness detector with ESP32-CAM MJPEG stream
"""

import cv2
import sys
import os
import time
import requests

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from liveness_detector import LivenessDetector

# ESP32-CAM Configuration
ESP32_CAM_IP = "192.168.1.11"
STREAM_URL = f"http://{ESP32_CAM_IP}:81/stream"  # Port 81 for stream
CAPTURE_URL = f"http://{ESP32_CAM_IP}/capture"   # Port 80 for capture

def check_camera_connection():
    """Verify ESP32-CAM is accessible"""
    try:
        response = requests.get(CAPTURE_URL, timeout=5)
        if response.status_code == 200:
            print(f"✓ ESP32-CAM connected at {ESP32_CAM_IP}")
            return True
        else:
            print(f"✗ ESP32-CAM responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to ESP32-CAM: {e}")
        print(f"  Make sure ESP32-CAM is powered on and connected to WiFi")
        print(f"  Try accessing {STREAM_URL} in your browser")
        return False

def main():
    print("="*70)
    print("ESP32-CAM + Phase 3 rPPG Heartbeat Detection")
    print("="*70)
    print(f"Camera IP: {ESP32_CAM_IP}")
    print(f"Stream URL: {STREAM_URL}")
    print()
    
    # Check connection
    if not check_camera_connection():
        print("\nPlease check:")
        print("1. ESP32-CAM is powered on")
        print("2. ESP32-CAM is connected to WiFi")
        print("3. IP address is correct (192.168.1.11)")
        print("4. You can access the stream in browser")
        return
    
    print()
    print("This test demonstrates:")
    print("Phase 1: Moiré patterns, motion, texture")
    print("Phase 2: Screen glow, color uniformity, edge sharpness")
    print("Phase 3: rPPG heartbeat detection (PRIMARY)")
    print()
    print("Instructions:")
    print("1. Position your face in front of ESP32-CAM")
    print("2. Stay still for 10 seconds")
    print("3. The system will detect your heartbeat")
    print("4. Try with a photo/phone screen to see spoof detection")
    print()
    print("Press 'q' to quit")
    print("="*70)
    
    # Initialize detector with rPPG enabled
    detector = LivenessDetector(mode='passive', enable_rppg=True)
    
    # Connect to ESP32-CAM stream
    print(f"\nConnecting to ESP32-CAM stream...")
    cap = cv2.VideoCapture(STREAM_URL)
    
    # Set buffer size to reduce latency
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("✗ Failed to open ESP32-CAM stream")
        print(f"  Try accessing {STREAM_URL} in your browser first")
        return
    
    print("✓ Connected to ESP32-CAM stream")
    
    # Simple face detector for bbox
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    frame_count = 0
    start_time = time.time()
    fps_counter = 0
    fps = 0
    
    print("\nStarting detection... (Press 'q' to quit)\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Warning: Failed to grab frame from ESP32-CAM")
            time.sleep(0.1)
            continue
        
        frame_count += 1
        fps_counter += 1
        
        # Calculate FPS every second
        if time.time() - start_time >= 1.0:
            fps = fps_counter
            fps_counter = 0
            start_time = time.time()
        
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
            status = "REAL FACE"
            color = (0, 255, 0)
        else:
            status = f"{details.get('decision', 'SPOOF')}"
            color = (0, 0, 255)
        
        # Add ESP32-CAM indicator
        cv2.putText(frame, "ESP32-CAM", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, status, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        cv2.putText(frame, f"Confidence: {confidence:.1f}%", (10, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Display heartbeat info
        y_offset = 130
        if 'heartbeat' in details:
            hb_details = details['heartbeat']
            
            if hb_details.get('status') == 'collecting_data':
                progress = hb_details.get('progress', 0)
                cv2.putText(frame, f"Collecting: {progress:.0f}%", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            elif hb_details.get('detected'):
                bpm = hb_details.get('bpm', 0)
                cv2.putText(frame, f"BPM: {bpm:.0f}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                y_offset += 30
                snr = hb_details.get('snr', 0)
                cv2.putText(frame, f"SNR: {snr:.1f}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            else:
                cv2.putText(frame, "No heartbeat", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Display spoof indicators
        y_offset += 35
        if 'reasons' in details and details['reasons']:
            cv2.putText(frame, "Indicators:", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 20
            for reason in details['reasons'][:3]:  # Show max 3
                cv2.putText(frame, f"- {reason[:25]}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                y_offset += 18
        
        # Display FPS and frame count
        cv2.putText(frame, f"FPS: {fps}", (frame.shape[1]-100, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"Frame: {frame_count}", (frame.shape[1]-120, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        cv2.imshow("ESP32-CAM + Phase 3 rPPG Detection", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        if cv2.getWindowProperty("ESP32-CAM + Phase 3 rPPG Detection", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nTest completed.")
    print(f"Total frames processed: {frame_count}")
    print(f"Average FPS: {frame_count / (time.time() - start_time):.1f}")

if __name__ == "__main__":
    main()
