"""
ESP32-CAM Connection Tester
Finds the correct stream endpoint for your ESP32-CAM
"""

import requests
import cv2

ESP32_IP = "192.168.1.11"

# Common ESP32-CAM stream endpoints
POSSIBLE_ENDPOINTS = [
    "/stream",
    "/mjpeg",
    "/video",
    ":81/stream",  # Some ESP32-CAM use port 81
    "/cam",
    "/live",
]

print("="*60)
print("ESP32-CAM Connection Tester")
print("="*60)
print(f"Testing ESP32-CAM at IP: {ESP32_IP}\n")

# Test basic connectivity
print("1. Testing basic connectivity...")
try:
    response = requests.get(f"http://{ESP32_IP}", timeout=3)
    print(f"   ✓ ESP32-CAM is reachable (Status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Cannot reach ESP32-CAM: {e}")
    print("\n   Please check:")
    print("   - ESP32-CAM is powered on")
    print("   - ESP32-CAM is connected to WiFi")
    print("   - IP address is correct")
    exit(1)

# Test /capture endpoint
print("\n2. Testing /capture endpoint...")
try:
    response = requests.get(f"http://{ESP32_IP}/capture", timeout=3)
    if response.status_code == 200:
        print(f"   ✓ /capture works (Image size: {len(response.content)} bytes)")
    else:
        print(f"   ✗ /capture returned status {response.status_code}")
except Exception as e:
    print(f"   ✗ /capture failed: {e}")

# Test stream endpoints
print("\n3. Testing stream endpoints...")
working_endpoint = None

for endpoint in POSSIBLE_ENDPOINTS:
    url = f"http://{ESP32_IP}{endpoint}"
    print(f"   Testing {url}...", end=" ")
    
    try:
        # Try with requests first
        response = requests.get(url, timeout=3, stream=True)
        if response.status_code == 200:
            print("✓ HTTP OK", end=" ")
            
            # Try with OpenCV
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✓ OpenCV OK (Frame: {frame.shape})")
                    working_endpoint = url
                    cap.release()
                    break
                else:
                    print("✗ OpenCV can't read frames")
                cap.release()
            else:
                print("✗ OpenCV can't open")
        else:
            print(f"✗ Status {response.status_code}")
    except Exception as e:
        print(f"✗ {type(e).__name__}")

print("\n" + "="*60)
if working_endpoint:
    print(f"✓ SUCCESS! Working stream URL found:")
    print(f"  {working_endpoint}")
    print("\nUpdate test_esp32_rppg.py with:")
    print(f'  STREAM_URL = "{working_endpoint}"')
else:
    print("✗ No working stream endpoint found")
    print("\nPlease check your ESP32-CAM code for the stream endpoint.")
    print("Common endpoints are: /stream, /mjpeg, :81/stream")
    print("\nYou can also try accessing these URLs in your browser:")
    for endpoint in POSSIBLE_ENDPOINTS:
        print(f"  http://{ESP32_IP}{endpoint}")

print("="*60)
