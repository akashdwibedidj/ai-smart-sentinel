"""
rPPG (Remote Photoplethysmography) Heartbeat Detector
Detects live heartbeat through subtle facial color changes
This is the most powerful anti-spoofing method - photos/screens have no blood flow
"""

import cv2
import numpy as np
from scipy import signal
from scipy.fftpack import fft
from collections import deque
import time


class RPPGDetector:
    def __init__(self, fps=30, window_size=10):
        """
        Initialize rPPG detector
        
        Args:
            fps: Camera frame rate (default 30)
            window_size: Seconds of signal to analyze (default 10)
        """
        self.fps = fps
        self.window_size = window_size
        self.buffer_size = fps * window_size  # e.g., 300 frames for 10 seconds
        
        # Signal buffers
        self.green_values = deque(maxlen=self.buffer_size)
        self.timestamps = deque(maxlen=self.buffer_size)
        
        # Heart rate tracking
        self.current_bpm = 0
        self.bpm_history = deque(maxlen=5)
        self.signal_quality = 0
        
        # Bandpass filter parameters (42-240 BPM = 0.7-4 Hz)
        self.low_freq = 0.7   # 42 BPM
        self.high_freq = 4.0  # 240 BPM
        
        # Detection state
        self.heartbeat_detected = False
        self.last_detection_time = 0
        
    def extract_face_roi(self, frame, face_bbox):
        """
        Extract region of interest from face
        Focus on forehead (best pulse signal - thin skin, many capillaries)
        
        Args:
            frame: Input BGR frame
            face_bbox: (x, y, w, h) bounding box
            
        Returns:
            ROI image or None
        """
        if face_bbox is None or len(face_bbox) != 4:
            return None
            
        x, y, w, h = face_bbox
        
        # Validate bbox
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            return None
        
        # Extract forehead region (upper 30% of face, centered)
        forehead_y = y + int(h * 0.1)
        forehead_h = int(h * 0.3)
        forehead_x = x + int(w * 0.2)
        forehead_w = int(w * 0.6)
        
        # Ensure within frame bounds
        frame_h, frame_w = frame.shape[:2]
        if (forehead_y + forehead_h > frame_h or 
            forehead_x + forehead_w > frame_w):
            return None
        
        forehead = frame[forehead_y:forehead_y+forehead_h, 
                        forehead_x:forehead_x+forehead_w]
        
        return forehead
    
    def calculate_green_channel_avg(self, roi):
        """
        Calculate average green channel value in ROI
        Green channel has strongest pulse signal (hemoglobin absorbs green light)
        
        Args:
            roi: Region of interest image (BGR)
            
        Returns:
            Average green value or None
        """
        if roi is None or roi.size == 0:
            return None
        
        # Extract green channel (index 1 in BGR)
        green_channel = roi[:, :, 1]
        
        # Calculate mean value
        avg_green = np.mean(green_channel)
        
        return avg_green
    
    def apply_bandpass_filter(self, signal_data):
        """
        Apply bandpass filter to isolate heart rate frequencies
        Filters out noise and keeps only heart rate range (0.7-4 Hz)
        
        Args:
            signal_data: Raw signal array
            
        Returns:
            Filtered signal
        """
        if len(signal_data) < 10:
            return signal_data
        
        # Design Butterworth bandpass filter
        nyquist_freq = self.fps / 2.0
        low = self.low_freq / nyquist_freq
        high = self.high_freq / nyquist_freq
        
        # Ensure valid frequency range
        low = max(0.01, min(0.99, low))
        high = max(0.01, min(0.99, high))
        
        if low >= high:
            return signal_data
        
        try:
            b, a = signal.butter(3, [low, high], btype='band')
            # Apply filter (forward and backward to avoid phase shift)
            filtered_signal = signal.filtfilt(b, a, signal_data)
            return filtered_signal
        except Exception as e:
            # If filtering fails, return original signal
            return signal_data
    
    def calculate_heart_rate(self, signal_data):
        """
        Calculate heart rate using FFT (Fast Fourier Transform)
        Finds dominant frequency in the signal and converts to BPM
        
        Args:
            signal_data: Filtered signal array
            
        Returns:
            (bpm, snr) - Heart rate in BPM and Signal-to-Noise Ratio
        """
        if len(signal_data) < self.fps * 3:  # Need at least 3 seconds
            return 0, 0
        
        # Detrend signal (remove DC component and linear trends)
        detrended = signal.detrend(signal_data)
        
        # Apply Hamming window to reduce spectral leakage
        windowed = detrended * np.hamming(len(detrended))
        
        # Perform FFT
        fft_data = np.abs(fft(windowed))
        
        # Get frequencies
        freqs = np.fft.fftfreq(len(windowed), 1.0 / self.fps)
        
        # Only look at positive frequencies in heart rate range
        valid_idx = np.where((freqs >= self.low_freq) & (freqs <= self.high_freq))
        valid_freqs = freqs[valid_idx]
        valid_fft = fft_data[valid_idx]
        
        # Find dominant frequency
        if len(valid_fft) == 0:
            return 0, 0
        
        peak_idx = np.argmax(valid_fft)
        dominant_freq = valid_freqs[peak_idx]
        
        # Convert to BPM
        bpm = dominant_freq * 60
        
        # Calculate signal quality (SNR - Signal to Noise Ratio)
        signal_power = valid_fft[peak_idx]
        noise_power = np.mean(valid_fft)
        snr = signal_power / (noise_power + 1e-6)
        
        return bpm, snr
    
    def calculate_signal_quality(self, signal_data):
        """
        Assess signal quality (0-100)
        Higher quality = clearer pulse signal
        
        Args:
            signal_data: Signal array
            
        Returns:
            Quality score (0-100)
        """
        if len(signal_data) < 10:
            return 0
        
        # Calculate signal variance (good signal has clear oscillations)
        signal_std = np.std(signal_data)
        signal_mean = np.mean(signal_data)
        
        # Coefficient of variation
        cv = (signal_std / (signal_mean + 1e-6)) * 100
        
        # Good signal has CV between 1-10
        quality = min(100, max(0, cv * 10))
        
        return quality
    
    def process_frame(self, frame, face_bbox, timestamp=None):
        """
        Process single frame and update heart rate
        
        Args:
            frame: BGR frame
            face_bbox: (x, y, w, h) face bounding box
            timestamp: Frame timestamp (optional, uses current time if None)
            
        Returns:
            (has_heartbeat, bpm, confidence, details)
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Extract ROI
        roi = self.extract_face_roi(frame, face_bbox)
        
        # Calculate green channel average
        green_avg = self.calculate_green_channel_avg(roi)
        
        if green_avg is None:
            return False, 0, 0, {"error": "no_roi"}
        
        # Add to buffer
        self.green_values.append(green_avg)
        self.timestamps.append(timestamp)
        
        # Need minimum buffer size (5 seconds)
        min_frames = self.fps * 5
        if len(self.green_values) < min_frames:
            progress = len(self.green_values) / min_frames * 100
            return False, 0, 0, {
                "status": "collecting_data",
                "progress": progress,
                "frames_collected": len(self.green_values),
                "frames_needed": min_frames
            }
        
        # Convert to numpy array
        signal_data = np.array(self.green_values)
        
        # Apply bandpass filter
        filtered_signal = self.apply_bandpass_filter(signal_data)
        
        # Calculate heart rate
        bpm, snr = self.calculate_heart_rate(filtered_signal)
        
        # Calculate signal quality
        quality = self.calculate_signal_quality(filtered_signal)
        
        # Validate BPM (normal resting range: 50-120 BPM)
        # Also require good SNR (> 2.0 means signal is 2x stronger than noise)
        is_valid = 50 <= bpm <= 120 and snr > 2.0
        
        if is_valid:
            self.bpm_history.append(bpm)
            # Use median to reduce noise
            self.current_bpm = np.median(self.bpm_history)
            self.heartbeat_detected = True
            self.last_detection_time = timestamp
            confidence = min(100, quality * (snr / 10))
        else:
            confidence = 0
            self.heartbeat_detected = False
        
        details = {
            "status": "analyzing" if is_valid else "no_heartbeat",
            "bpm": float(bpm),
            "bpm_smoothed": float(self.current_bpm),
            "snr": float(snr),
            "quality": float(quality),
            "buffer_size": len(self.green_values),
            "filtered_signal_std": float(np.std(filtered_signal)),
            "is_valid_range": 50 <= bpm <= 120,
            "is_good_snr": snr > 2.0
        }
        
        return is_valid, self.current_bpm, confidence, details
    
    def detect_heartbeat(self, frame, face_bbox, timestamp=None):
        """
        Main detection method - wrapper for process_frame
        
        Args:
            frame: BGR frame
            face_bbox: (x, y, w, h) face bounding box
            timestamp: Frame timestamp (optional)
            
        Returns:
            (has_heartbeat, bpm, confidence, details)
        """
        return self.process_frame(frame, face_bbox, timestamp)
    
    def reset(self):
        """
        Reset detector state (useful when switching users)
        """
        self.green_values.clear()
        self.timestamps.clear()
        self.bpm_history.clear()
        self.current_bpm = 0
        self.heartbeat_detected = False
        self.signal_quality = 0


# Quick test
if __name__ == "__main__":
    detector = RPPGDetector(fps=30, window_size=10)
    cap = cv2.VideoCapture(0)
    
    # Simple face detector for testing
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    print("="*60)
    print("rPPG Heartbeat Detection Test")
    print("="*60)
    print("Position your face in frame and stay still")
    print("Detection takes 5-10 seconds")
    print("Press 'q' to quit")
    print("="*60)
    
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect face
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            # Use first face
            face_bbox = faces[0]
            x, y, w, h = face_bbox
            
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Draw ROI (forehead)
            roi_y = y + int(h * 0.1)
            roi_h = int(h * 0.3)
            roi_x = x + int(w * 0.2)
            roi_w = int(w * 0.6)
            cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), 
                         (0, 255, 0), 2)
            
            # Process frame
            has_heartbeat, bpm, confidence, details = detector.detect_heartbeat(
                frame, face_bbox
            )
            
            # Display results
            if details.get("status") == "collecting_data":
                progress = details.get("progress", 0)
                cv2.putText(frame, f"Collecting data: {progress:.0f}%", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            elif has_heartbeat:
                cv2.putText(frame, f"♥ {bpm:.0f} BPM", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.putText(frame, f"Confidence: {confidence:.0f}%", (10, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"SNR: {details['snr']:.1f}", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            else:
                cv2.putText(frame, "No heartbeat detected", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                if details.get("bpm", 0) > 0:
                    cv2.putText(frame, f"BPM: {details['bpm']:.0f} (invalid)", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        else:
            cv2.putText(frame, "No face detected", (10, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.imshow("rPPG Heartbeat Detection", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        if cv2.getWindowProperty("rPPG Heartbeat Detection", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nTest completed.")
