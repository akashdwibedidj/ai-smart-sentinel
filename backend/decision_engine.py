"""
Decision Engine
Combines all checks and makes final access control decision
"""

import json
import os
from datetime import datetime
import cv2

class DecisionEngine:
    def __init__(self, log_dir="data/logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "access_log.json")
        
        # Initialize log file if doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def make_decision(self, injection_result, liveness_result, verification_result):
        """
        Make final access control decision based on all checks
        
        Args:
            injection_result: (is_injection, confidence, details)
            liveness_result: (is_real, confidence, details)
            verification_result: (matched, similarity, person_id, details)
        
        Returns:
            decision_dict with access granted/denied and reasons
        """
        is_injection, inj_confidence, inj_details = injection_result
        is_real, live_confidence, live_details = liveness_result
        matched, face_similarity, person_id, verify_details = verification_result
        
        # Decision logic
        decision = {
            'timestamp': datetime.now().isoformat(),
            'access_granted': False,
            'decision': 'DENIED',
            'reason': [],
            'confidence': 0,
            'person_id': person_id,
            'checks': {
                'injection_check': {},
                'liveness_check': {},
                'face_verification': {}
            }
        }
        
        # CRITICAL: Injection attack check (highest priority)
        if is_injection:
            decision['decision'] = 'INJECTION_ATTACK_DETECTED'
            decision['reason'].append(f"Injection attack detected ({inj_confidence}% confidence)")
            decision['confidence'] = inj_confidence
            decision['checks']['injection_check'] = {
                'passed': False,
                'confidence': inj_confidence,
                'details': inj_details
            }
            return decision
        else:
            decision['checks']['injection_check'] = {
                'passed': True,
                'confidence': 100 - inj_confidence,
                'details': inj_details
            }
        
        # Liveness check
        if not is_real:
            decision['decision'] = 'SPOOF_DETECTED'
            decision['reason'].append(f"Presentation attack detected (confidence: {live_confidence:.1f}%)")
            decision['confidence'] = live_confidence
            decision['checks']['liveness_check'] = {
                'passed': False,
                'confidence': live_confidence,
                'details': live_details
            }
            return decision
        else:
            decision['checks']['liveness_check'] = {
                'passed': True,
                'confidence': live_confidence,
                'details': live_details
            }
        
        # Face verification
        if not matched:
            decision['decision'] = 'FACE_MISMATCH'
            decision['reason'].append(f"Face does not match registered ID (similarity: {face_similarity:.1f}%)")
            decision['confidence'] = face_similarity
            decision['checks']['face_verification'] = {
                'passed': False,
                'similarity': face_similarity,
                'person_id': person_id,
                'details': verify_details
            }
            return decision
        else:
            decision['checks']['face_verification'] = {
                'passed': True,
                'similarity': face_similarity,
                'person_id': person_id,
                'details': verify_details
            }
        
        # ALL CHECKS PASSED - GRANT ACCESS
        decision['access_granted'] = True
        decision['decision'] = 'ACCESS_GRANTED'
        decision['reason'].append(f"All security checks passed")
        decision['person_id'] = person_id
        
        # Calculate overall confidence (average of all checks)
        decision['confidence'] = (
            (100 - inj_confidence) * 0.3 +  # 30% weight to injection check
            live_confidence * 0.3 +           # 30% weight to liveness
            face_similarity * 0.4              # 40% weight to face match
        )
        
        return decision
    
    def log_decision(self, decision, frame=None):
        """
        Log the decision to file and optionally save screenshot
        """
        try:
            # Read existing logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Save screenshot if provided
            if frame is not None:
                screenshot_dir = os.path.join(self.log_dir, "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(
                    screenshot_dir,
                    f"{timestamp_str}_{decision['decision']}.jpg"
                )
                cv2.imwrite(screenshot_path, frame)
                decision['screenshot'] = screenshot_path
            
            # Append new log
            logs.append(decision)
            
            # Keep only last 1000 logs to prevent file from growing too large
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Logging error: {e}")
            return False
    
    def get_recent_logs(self, count=10):
        """
        Get most recent access logs
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            return logs[-count:]
        except:
            return []
    
    def get_statistics(self):
        """
        Get access statistics
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            total = len(logs)
            granted = sum(1 for log in logs if log['access_granted'])
            denied = total - granted
            
            # Count by reason
            injection_attacks = sum(1 for log in logs if log['decision'] == 'INJECTION_ATTACK_DETECTED')
            spoofs = sum(1 for log in logs if log['decision'] == 'SPOOF_DETECTED')
            mismatches = sum(1 for log in logs if log['decision'] == 'FACE_MISMATCH')
            
            return {
                'total_attempts': total,
                'access_granted': granted,
                'access_denied': denied,
                'injection_attacks': injection_attacks,
                'spoofs_detected': spoofs,
                'face_mismatches': mismatches,
                'success_rate': (granted / total * 100) if total > 0 else 0
            }
        except:
            return {
                'total_attempts': 0,
                'access_granted': 0,
                'access_denied': 0,
                'injection_attacks': 0,
                'spoofs_detected': 0,
                'face_mismatches': 0,
                'success_rate': 0
            }

# Quick test
if __name__ == "__main__":
    engine = DecisionEngine()
    
    # Simulate different scenarios
    
    # Scenario 1: Injection attack
    print("Scenario 1: Injection Attack")
    decision1 = engine.make_decision(
        injection_result=(True, 80, {'virtual_camera': True}),
        liveness_result=(True, 90, {}),
        verification_result=(True, 85, 'john_doe', {})
    )
    print(json.dumps(decision1, indent=2))
    engine.log_decision(decision1)
    
    # Scenario 2: Spoof detected
    print("\nScenario 2: Spoof Attack")
    decision2 = engine.make_decision(
        injection_result=(False, 10, {}),
        liveness_result=(False, 85, {'is_real': False}),
        verification_result=(True, 90, 'john_doe', {})
    )
    print(json.dumps(decision2, indent=2))
    engine.log_decision(decision2)
    
    # Scenario 3: Face mismatch
    print("\nScenario 3: Face Mismatch")
    decision3 = engine.make_decision(
        injection_result=(False, 5, {}),
        liveness_result=(True, 92, {}),
        verification_result=(False, 45, 'unknown', {})
    )
    print(json.dumps(decision3, indent=2))
    engine.log_decision(decision3)
    
    # Scenario 4: All checks passed
    print("\nScenario 4: Access Granted")
    decision4 = engine.make_decision(
        injection_result=(False, 5, {}),
        liveness_result=(True, 95, {}),
        verification_result=(True, 88, 'john_doe', {})
    )
    print(json.dumps(decision4, indent=2))
    engine.log_decision(decision4)
    
    # Show statistics
    print("\nStatistics:")
    print(json.dumps(engine.get_statistics(), indent=2))