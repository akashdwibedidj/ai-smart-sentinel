"""
Injection Attack Detector
Detects virtual cameras and video injection attempts
"""

import cv2
import numpy as np
import platform
import subprocess
import time

class InjectionDetector:
    def __init__(self):
        self.baseline_noise = None
        self.frame_count = 0
        
        # Cache for virtual camera detection (expensive operation)
        self.virtual_camera_cache = None
        self.virtual_camera_cache_time = 0
        self.virtual_camera_check_interval = 30  # Check every 30 seconds
        
    def detect_virtual_camera(self):
        """
        Detect if a virtual camera software is running
        Checks for: OBS, ManyCam, XSplit, etc.
        Uses caching to avoid expensive checks on every frame
        """
        current_time = time.time()
        
        # Return cached result if still valid
        if (self.virtual_camera_cache is not None and 
            current_time - self.virtual_camera_cache_time < self.virtual_camera_check_interval):
            return self.virtual_camera_cache
        
        # Perform the actual check
        system = platform.system()
        
        if system == "Windows":
            virtual_cam_processes = [
                "obs64.exe", "obs32.exe",
                "ManyCam.exe",
                "XSplit.Core.exe",
                "CamTwist.exe",
                "vMix64.exe"
            ]
            
            try:
                # Get list of running processes (EXPENSIVE OPERATION)
                output = subprocess.check_output("tasklist", shell=True).decode()
                
                for process in virtual_cam_processes:
                    if process.lower() in output.lower():
                        result = (True, f"Virtual camera detected: {process}")
                        # Cache the result
                        self.virtual_camera_cache = result
                        self.virtual_camera_cache_time = current_time
                        return result
                        
            except Exception as e:
                print(f"Process check error: {e}")
        
        # No virtual camera detected
        result = (False, "No virtual camera detected")
        self.virtual_camera_cache = result
        self.virtual_camera_cache_time = current_time
        return result
    
    def analyze_sensor_noise(self, frame):
        """
        Real cameras have sensor noise, injected videos are too clean
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate noise level using standard deviation of Laplacian
        noise_level = cv2.Laplacian(gray, cv2.CV_64F).std()
        
        # Initialize baseline on first few frames
        if self.frame_count < 10:
            if self.baseline_noise is None:
                self.baseline_noise = noise_level
            else:
                self.baseline_noise = (self.baseline_noise + noise_level) / 2
            self.frame_count += 1
            return False, noise_level
        
        # Injected videos have suspiciously low or zero noise
        if noise_level < 1.0:
            return True, noise_level
            
        return False, noise_level
    
    def detect_perfect_stability(self, frame, prev_frame):
        """
        Real cameras have micro-movements, injected feeds are too stable
        """
        if prev_frame is None:
            return False, 0
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate frame difference
        diff = cv2.absdiff(gray1, gray2)
        movement_score = np.mean(diff)
        
        # Suspiciously zero movement (frozen or looped video)
        if movement_score < 0.5:
            return True, movement_score
            
        return False, movement_score
    
    def check_metadata_anomalies(self, cap):
        """
        Check camera metadata for anomalies
        Virtual cameras often report perfect FPS values
        """
        if cap is None:
            return False, "No capture object provided"
        
        try:
            backend = cap.getBackendName()
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Virtual cameras often report suspiciously perfect FPS
            # Real cameras have slight variations (29.97, 30.01, etc.)
            perfect_fps_values = [25.0, 30.0, 60.0, 120.0]
            
            if fps in perfect_fps_values:
                return True, f"Suspicious perfect FPS: {fps} (Backend: {backend})"
            
            return False, f"FPS: {fps:.2f}, Backend: {backend}"
            
        except Exception as e:
            return False, f"Metadata check error: {e}"
    
    def full_injection_check(self, frame, prev_frame=None, cap=None):
        """
        Comprehensive injection attack detection
        Returns: (is_injection, confidence, details)
        """
        results = {
            'virtual_camera': False,
            'sensor_noise': False,
            'stability': False,
            'metadata': False,
            'details': {}
        }
        
        # Check 1: Virtual camera software
        vc_detected, vc_msg = self.detect_virtual_camera()
        results['virtual_camera'] = vc_detected
        results['details']['virtual_camera'] = vc_msg
        
        # Check 2: Sensor noise analysis
        noise_suspicious, noise_level = self.analyze_sensor_noise(frame)
        results['sensor_noise'] = noise_suspicious
        results['details']['noise_level'] = noise_level
        
        # Check 3: Frame stability (only if prev_frame available)
        if prev_frame is not None:
            stability_suspicious, movement = self.detect_perfect_stability(frame, prev_frame)
            results['stability'] = stability_suspicious
            results['details']['movement_score'] = movement
        
        # Check 4: Metadata anomalies (if cap provided)
        if cap is not None:
            metadata_suspicious, metadata_msg = self.check_metadata_anomalies(cap)
            results['metadata'] = metadata_suspicious
            results['details']['metadata'] = metadata_msg
        
        # Calculate overall injection confidence
        injection_score = 0
        if results['virtual_camera']:
            injection_score += 60  # Strong indicator
        if results['sensor_noise']:
            injection_score += 15
        if results['stability']:
            injection_score += 10
        if results['metadata']:
            injection_score += 15
            
        is_injection = injection_score > 50
        
        return is_injection, injection_score, results

# Quick test
if __name__ == "__main__":
    detector = InjectionDetector()
    cap = cv2.VideoCapture(0)
    
    prev_frame = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        is_injection, confidence, details = detector.full_injection_check(
            frame, prev_frame, cap
        )
        
        # SECURITY: If injection detected, immediately block camera access
        if is_injection:
            # Create error screen
            error_frame = np.zeros_like(frame)
            
            # Add error messages
            cv2.putText(error_frame, "SECURITY ALERT", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            cv2.putText(error_frame, "INJECTION ATTACK DETECTED", (50, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            cv2.putText(error_frame, f"Confidence: {confidence}%", (50, 210),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Show which checks failed
            y_offset = 260
            cv2.putText(error_frame, "Failed Checks:", (50, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_offset += 40
            
            if details['virtual_camera']:
                cv2.putText(error_frame, "- Virtual Camera Software Detected", (70, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                y_offset += 30
            if details['sensor_noise']:
                cv2.putText(error_frame, "- Suspicious Low Sensor Noise", (70, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                y_offset += 30
            if details['stability']:
                cv2.putText(error_frame, "- Unnaturally Stable Frames", (70, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                y_offset += 30
            if details.get('metadata', False):
                cv2.putText(error_frame, "- Suspicious Metadata (Perfect FPS)", (70, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                y_offset += 30
            
            cv2.putText(error_frame, "Camera access blocked for security.", (50, y_offset + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(error_frame, "Closing in 3 seconds...", (50, y_offset + 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            
            # Show error screen
            cv2.imshow("Injection Detection Test", error_frame)
            cv2.waitKey(3000)  # Show for 3 seconds
            
            # Close everything
            cap.release()
            cv2.destroyAllWindows()
            print("\n" + "="*60)
            print("INJECTION ATTACK DETECTED - Camera access blocked!")
            print(f"Confidence: {confidence}%")
            print("="*60)
            break  # Exit the loop
        
        # Display results with clear feedback (only if no injection)
        color = (0, 255, 0)  # Green
        status = "NO INJECTION - CAMERA SECURE"
        
        # Main status
        cv2.putText(frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"Confidence: {confidence}%", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Detailed checks
        y_offset = 90
        cv2.putText(frame, "Checks:", (10, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 25
        
        # Virtual camera check
        vc_status = "PASS"
        vc_color = (0, 255, 0)
        cv2.putText(frame, f"Virtual Cam: {vc_status}", (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, vc_color, 1)
        y_offset += 20
        
        # Noise check
        noise_val = details['details'].get('noise_level', 0)
        noise_status = "PASS"
        noise_color = (0, 255, 0)
        cv2.putText(frame, f"Noise: {noise_status} ({noise_val:.2f})", (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, noise_color, 1)
        y_offset += 20
        
        # Stability check
        if 'movement_score' in details['details']:
            move_val = details['details']['movement_score']
            stab_status = "PASS"
            stab_color = (0, 255, 0)
            cv2.putText(frame, f"Stability: {stab_status} ({move_val:.2f})", (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, stab_color, 1)
            y_offset += 20
        
        # Metadata check
        if 'metadata' in details['details']:
            meta_status = "PASS"
            meta_color = (0, 255, 0)
            cv2.putText(frame, f"Metadata: {meta_status}", (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, meta_color, 1)
        
                
        cv2.imshow("Injection Detection Test", frame)
        
        prev_frame = frame.copy()
        
        # Check for 'q' key press OR window close button
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        # Check if window was closed (user clicked X button)
        if cv2.getWindowProperty("Injection Detection Test", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nCamera closed successfully.")