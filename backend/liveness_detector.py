"""
Advanced Liveness Detector - Phase 1
Implements passive liveness detection to catch phone screens and photos
Uses: Moiré pattern detection, motion analysis, texture analysis
"""

import cv2
import numpy as np
from scipy import fftpack

class LivenessDetector:
    def __init__(self):
        # Thresholds - ADJUSTED FOR LOW-QUALITY WEBCAMS
        self.texture_threshold = 20  # Lowered from 50
        self.motion_threshold = 0.5  # Lowered from 2.0 (more lenient)
        self.moire_threshold = 0.6   # Raised from 0.3 (less sensitive)
        self.edge_sharpness_threshold = 250  # Raised from 150 (less sensitive)
        
        # Frame history for motion analysis
        self.frame_history = []
        self.max_history = 5
        
    def detect_moire_pattern(self, frame):
        """
        Detect moiré patterns that appear when photographing screens
        Screens have regular pixel grids that create interference patterns
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply FFT to detect periodic patterns
        f_transform = fftpack.fft2(gray)
        f_shift = fftpack.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        # Look for strong periodic components (screen refresh patterns)
        # Real faces have more random frequency distribution
        h, w = magnitude_spectrum.shape
        center_h, center_w = h // 2, w // 2
        
        # Sample regions away from DC component
        region_size = 20
        regions = [
            magnitude_spectrum[center_h-50:center_h-30, center_w-50:center_w-30],
            magnitude_spectrum[center_h+30:center_h+50, center_w+30:center_w+50]
        ]
        
        # Calculate periodicity score
        periodicity = np.mean([np.std(region) for region in regions])
        
        # Normalize (higher = more periodic = more likely screen)
        moire_score = min(1.0, periodicity / 10000)
        
        is_screen = moire_score > self.moire_threshold
        
        return is_screen, moire_score
    
    def analyze_motion(self, frame):
        """
        Analyze motion patterns across frames
        Real faces have micro-movements, photos/screens are static or move uniformly
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Add to history
        self.frame_history.append(gray)
        if len(self.frame_history) > self.max_history:
            self.frame_history.pop(0)
        
        # Need at least 2 frames
        if len(self.frame_history) < 2:
            return False, 0, {"reason": "insufficient_frames"}
        
        # Calculate optical flow between consecutive frames
        prev_frame = self.frame_history[-2]
        curr_frame = self.frame_history[-1]
        
        # Calculate dense optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_frame, curr_frame,
            None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # Calculate flow magnitude
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        
        # Analyze motion characteristics
        avg_motion = np.mean(magnitude)
        motion_variance = np.std(magnitude)
        
        # Real faces have non-uniform motion (micro-movements in different areas)
        # Photos/screens have uniform motion (entire image moves together) or no motion
        
        # Check for suspicious patterns
        is_suspicious = False
        reason = "normal_motion"
        
        # ADJUSTED FOR LOW-QUALITY WEBCAMS
        if avg_motion < 0.1:  # Lowered from 0.5 - only flag if REALLY static
            # Too static - likely a photo
            is_suspicious = True
            reason = "too_static"
        elif motion_variance < self.motion_threshold and avg_motion < 0.3:
            # Too uniform AND low motion - likely screen/photo being moved
            is_suspicious = True
            reason = "uniform_motion"
        
        details = {
            "avg_motion": avg_motion,
            "motion_variance": motion_variance,
            "reason": reason
        }
        
        return is_suspicious, motion_variance, details
    
    def analyze_edge_sharpness(self, frame):
        """
        Analyze edge sharpness
        Photos/screens have artificially sharp edges
        Real faces have natural blur at edges
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 100, 200)
        
        # Calculate edge density and sharpness
        edge_density = np.sum(edges > 0) / edges.size
        
        # Apply Laplacian for sharpness
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # Photos/screens have higher edge density and sharpness
        is_too_sharp = sharpness > self.edge_sharpness_threshold
        
        return is_too_sharp, sharpness, {
            "edge_density": edge_density,
            "sharpness": sharpness
        }
    
    def detect_texture_quality(self, frame):
        """
        Enhanced texture analysis
        Real skin has natural texture, screens/photos are too smooth or too pixelated
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance (texture measure)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate gradient magnitude
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(sobelx**2 + sobely**2).mean()
        
        # Calculate local binary patterns (texture descriptor)
        # Real skin has specific texture patterns
        radius = 1
        n_points = 8 * radius
        
        # Simplified LBP-like calculation
        texture_score = (laplacian_var / 10) + (gradient_mag / 5)
        
        # Check if texture is in realistic range
        # WIDENED RANGE FOR LOW-QUALITY WEBCAMS
        # Too low = smooth screen, too high = pixelated photo
        is_realistic = 15 < texture_score < 300  # Was 30-200
        
        return is_realistic, texture_score, {
            'laplacian': laplacian_var,
            'gradient': gradient_mag,
            'texture_score': texture_score
        }
    
    def hybrid_liveness_check(self, frame):
        """
        Comprehensive liveness check combining all methods
        Returns: (is_real, confidence, details)
        """
        details = {}
        spoof_indicators = []
        confidence_factors = []
        
        # 1. Moiré pattern detection (screens)
        has_moire, moire_score = self.detect_moire_pattern(frame)
        details['moire'] = {
            'detected': has_moire,
            'score': moire_score
        }
        if has_moire:
            spoof_indicators.append("screen_pattern_detected")
            confidence_factors.append(moire_score * 100)
        
        # 2. Motion analysis (static photos/uniform movement)
        is_suspicious_motion, motion_var, motion_details = self.analyze_motion(frame)
        details['motion'] = motion_details
        if is_suspicious_motion:
            spoof_indicators.append(f"suspicious_motion_{motion_details['reason']}")
            confidence_factors.append(70)
        
        # 3. Edge sharpness (artificial sharpness)
        is_too_sharp, sharpness, edge_details = self.analyze_edge_sharpness(frame)
        details['edges'] = edge_details
        if is_too_sharp:
            spoof_indicators.append("artificial_sharpness")
            confidence_factors.append(60)
        
        # 4. Texture quality (realistic skin texture)
        is_realistic_texture, texture_score, texture_details = self.detect_texture_quality(frame)
        details['texture'] = texture_details
        if not is_realistic_texture:
            spoof_indicators.append("unrealistic_texture")
            confidence_factors.append(50)
        
        # Make final decision
        # ADJUSTED: Require 3 indicators for high confidence spoof detection
        if len(spoof_indicators) >= 3:
            # Multiple indicators = likely spoof
            is_real = False
            confidence = np.mean(confidence_factors) if confidence_factors else 75
            details['decision'] = 'SPOOF_DETECTED'
            details['reasons'] = spoof_indicators
        elif len(spoof_indicators) == 2:
            # Two indicators = suspicious but give benefit of doubt for low-quality cams
            is_real = True  # Changed from False
            confidence = 50 + (texture_score / 10)
            details['decision'] = 'SUSPICIOUS_BUT_ALLOWED'
            details['reasons'] = spoof_indicators
        elif len(spoof_indicators) == 1:
            # Single indicator = likely just low quality camera
            is_real = True
            confidence = 70 + (texture_score / 10)
            details['decision'] = 'REAL_FACE'
            details['reasons'] = ['minor_anomaly_ignored']
        else:
            # No indicators = likely real
            is_real = True
            confidence = 85 + (texture_score / 10)  # Base confidence + texture bonus
            confidence = min(100, confidence)
            details['decision'] = 'REAL_FACE'
            details['reasons'] = ['all_checks_passed']
        
        details['method'] = 'advanced_passive_liveness'
        
        return is_real, confidence, details
    
    def detect_liveness(self, frame):
        """Wrapper for compatibility"""
        return self.hybrid_liveness_check(frame)


# Quick test
if __name__ == "__main__":
    detector = LivenessDetector()
    cap = cv2.VideoCapture(0)
    
    print("="*60)
    print("AI Smart Sentinel - Advanced Liveness Detection")
    print("="*60)
    print("Phase 1: Moiré + Motion + Texture Analysis")
    print("Try: Real face, phone screen, printed photo")
    print("Press 'q' to quit")
    print("="*60)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run liveness check
        is_real, confidence, details = detector.hybrid_liveness_check(frame)
        
        # Display results
        if is_real:
            status = "✓ REAL FACE"
            color = (0, 255, 0)
        else:
            status = f"✗ {details['decision']}"
            color = (0, 0, 255)
        
        cv2.putText(frame, status, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, f"Confidence: {confidence:.1f}%", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Show reasons
        y_offset = 120
        if 'reasons' in details:
            cv2.putText(frame, "Reasons:", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_offset += 25
            for reason in details['reasons'][:3]:  # Show max 3 reasons
                cv2.putText(frame, f"- {reason}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y_offset += 20
        
        cv2.imshow("Advanced Liveness Detection", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        if cv2.getWindowProperty("Advanced Liveness Detection", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nCamera closed successfully.")