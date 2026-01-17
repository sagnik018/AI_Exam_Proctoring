import cv2
import numpy as np
import time
import json
import os
from datetime import datetime

class CalibrationWizard:
    def __init__(self):
        self.current_step = 0
        self.calibration_data = {}
        self.test_results = {}
        self.is_running = False
        
        # Define calibration steps including exam preparation
        self.calibration_steps = [
            {
                'id': 'welcome',
                'title': 'Welcome to Exam Setup',
                'description': 'This wizard will help you set up your environment for secure exam proctoring.',
                'instructions': [
                    'Ensure you are in a quiet, well-lit room',
                    'Position your camera at eye level',
                    'Have your government ID ready for verification',
                    'Close all unnecessary applications',
                    'Disable notifications on your device'
                ],
                'test_type': None
            },
            {
                'id': 'camera_position',
                'title': 'Camera Position Check',
                'description': 'Position your camera to capture your face clearly.',
                'instructions': [
                    'Center your face in the frame',
                    'Ensure good lighting on your face',
                    'Position camera at eye level',
                    'Keep 1-2 feet distance from camera',
                    'Avoid backlighting'
                ],
                'test_type': 'camera'
            },
            {
                'id': 'face_verification',
                'title': 'Face Identity Verification',
                'description': 'Verify your identity before starting the exam.',
                'instructions': [
                    'Look directly at the camera',
                    'Remove glasses if possible for better recognition',
                    'Keep neutral expression',
                    'Wait for face detection and verification',
                    'Only registered users can proceed'
                ],
                'test_type': 'face_verification'
            },
            {
                'id': 'lighting_check',
                'title': 'Lighting Assessment',
                'description': 'Check if lighting conditions are optimal for face detection.',
                'instructions': [
                    'Ensure even lighting on your face',
                    'Avoid strong shadows',
                    'Natural light is preferred',
                    'Avoid backlight from windows',
                    'Adjust room lighting if needed'
                ],
                'test_type': 'lighting'
            },
            {
                'id': 'face_detection',
                'title': 'Face Detection Test',
                'description': 'Test if the system can detect your face reliably.',
                'instructions': [
                    'Keep your face visible in the camera',
                    'Move slightly to test detection',
                    'Ensure no obstructions',
                    'Test different angles briefly',
                    'Return to centered position'
                ],
                'test_type': 'face_detection'
            },
            {
                'id': 'audio_check',
                'title': 'Audio Environment Check',
                'description': 'Check for background noise that might trigger alerts.',
                'instructions': [
                    'Ensure quiet environment',
                    'Turn off music/TV',
                    'Close windows to reduce outside noise',
                    'Inform others in the house',
                    'Test microphone clarity'
                ],
                'test_type': 'audio'
            },
            {
                'id': 'exam_rules',
                'title': 'Exam Rules Confirmation',
                'description': 'Review and confirm understanding of exam rules.',
                'instructions': [
                    'No other persons should be in the room',
                    'No talking during the exam',
                    'No looking away from screen frequently',
                    'No switching tabs or applications',
                    'No mobile phone usage during exam',
                    'Maintain eye contact with screen',
                    'No unauthorized materials nearby',
                    'Follow all examiner instructions'
                ],
                'test_type': 'rules_confirmation'
            },
            {
                'id': 'final_check',
                'title': 'Final System Check',
                'description': 'Complete system verification before starting exam.',
                'instructions': [
                    'All systems verified successfully',
                    'Face identity confirmed',
                    'Environment is suitable',
                    'You are ready to start the exam',
                    'Click "Start Exam" when ready'
                ],
                'test_type': None
            }
        ]
        
        # Load existing calibration if available
        self._load_calibration()
    
    def _load_calibration(self):
        """Load existing calibration settings"""
        try:
            if os.path.exists("calibration_settings.json"):
                with open("calibration_settings.json", 'r') as f:
                    self.calibration_data = json.load(f)
                    print(f"[CALIBRATION] Loaded existing settings")
        except Exception as e:
            print(f"[CALIBRATION] Could not load settings: {e}")
            self.calibration_data = {}
    
    def _save_calibration(self):
        """Save calibration settings"""
        try:
            with open("calibration_settings.json", 'w') as f:
                json.dump(self.calibration_data, f, indent=2)
                print(f"[CALIBRATION] Settings saved")
        except Exception as e:
            print(f"[CALIBRATION] Could not save settings: {e}")
    
    def start_calibration(self):
        """Start the calibration wizard"""
        print("[CALIBRATION] Starting calibration wizard...")
        self.current_step = 0
        self.test_results = {}
        
        return {
            'status': 'started',
            'current_step': self.calibration_steps[self.current_step]['title'],
            'total_steps': len(self.calibration_steps),
            'progress': 0
        }
    
    def next_step(self):
        """Move to next calibration step"""
        if self.current_step < len(self.calibration_steps) - 1:
            self.current_step += 1
            return {
                'status': 'in_progress',
                'current_step': self.calibration_steps[self.current_step]['title'],
                'total_steps': len(self.calibration_steps),
                'progress': (self.current_step + 1) / len(self.calibration_steps) * 100
            }
        else:
            return self.complete_calibration()
    
    def complete_calibration(self):
        """Complete calibration and save settings"""
        # Save all test results to calibration data
        self.calibration_data.update(self.test_results)
        self.calibration_data['calibrated_at'] = datetime.now().isoformat()
        self.calibration_data['calibration_version'] = '1.0'
        
        self._save_calibration()
        
        print("[CALIBRATION] Calibration completed successfully!")
        
        return {
            'status': 'completed',
            'message': 'Calibration completed successfully',
            'settings_saved': True
        }
    
    def run_camera_position_test(self, frame):
        """Test camera positioning and framing"""
        if frame is None:
            return {'status': 'error', 'message': 'No camera feed available'}
        
        height, width = frame.shape[:2]
        
        # Check if face is properly framed
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
        
        results = {
            'resolution': {'width': width, 'height': height},
            'faces_detected': len(faces),
            'framing_ok': len(faces) > 0,
            'recommendations': []
        }
        
        # Add recommendations
        if width < 640 or height < 480:
            results['recommendations'].append("Consider using higher resolution for better detection")
        
        if len(faces) == 0:
            results['recommendations'].append("Position yourself in good lighting and face the camera")
        elif len(faces) > 1:
            results['recommendations'].append("Ensure only one person is in frame")
        else:
            face = faces[0]
            face_area = face[2] * face[3]
            frame_area = width * height
            face_ratio = face_area / frame_area
            
            if face_ratio < 0.1:  # Face takes less than 10% of frame
                results['recommendations'].append("Move closer to camera for better detection")
            elif face_ratio > 0.5:  # Face takes more than 50% of frame
                results['recommendations'].append("Move further from camera for better framing")
        
        self.test_results['camera_position'] = results
        return results
    
    def run_lighting_test(self, frame):
        """Test lighting conditions"""
        if frame is None:
            return {'status': 'error', 'message': 'No camera feed available'}
        
        # Convert to grayscale for lighting analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate brightness and contrast
        brightness = np.mean(gray)
        std_dev = np.std(gray)
        
        results = {
            'brightness': float(brightness),
            'contrast': float(std_dev),
            'lighting_quality': 'good'
        }
        
        # Determine lighting quality
        if brightness < 50:
            results['lighting_quality'] = 'dark'
            results['recommendations'] = ["Increase lighting in the room"]
        elif brightness > 200:
            results['lighting_quality'] = 'bright'
            results['recommendations'] = ["Reduce bright lighting or adjust camera exposure"]
        elif std_dev < 30:
            results['lighting_quality'] = 'low_contrast'
            results['recommendations'] = ["Improve lighting contrast for better detection"]
        else:
            results['recommendations'] = ["Lighting conditions are optimal"]
        
        self.test_results['lighting'] = results
        return results
    
    def run_face_detection_test(self, frame):
        """Test face detection accuracy"""
        if frame is None:
            return {'status': 'error', 'message': 'No camera feed available'}
        
        # Test with different parameters
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Test multiple detection settings
        test_settings = [
            {'scaleFactor': 1.1, 'minNeighbors': 5, 'name': 'conservative'},
            {'scaleFactor': 1.05, 'minNeighbors': 3, 'name': 'balanced'},
            {'scaleFactor': 1.02, 'minNeighbors': 2, 'name': 'aggressive'}
        ]
        
        results = {
            'test_results': [],
            'recommended_setting': 'conservative',
            'detection_accuracy': 'good'
        }
        
        for setting in test_settings:
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=setting['scaleFactor'], 
                minNeighbors=setting['minNeighbors'],
                minSize=(50, 50)
            )
            
            test_result = {
                'setting_name': setting['name'],
                'faces_found': len(faces),
                'false_positives': max(0, len(faces) - 1),  # Assume max 1 face
                'sensitivity': setting['name']
            }
            results['test_results'].append(test_result)
        
        # Recommend best setting (fewest false positives)
        best_setting = min(results['test_results'], key=lambda x: x['false_positives'])
        results['recommended_setting'] = best_setting['setting_name']
        
        if best_setting['false_positives'] > 0:
            results['detection_accuracy'] = 'needs_improvement'
            results['recommendations'] = [f"Recommended setting: {best_setting['setting_name']}"]
        else:
            results['recommendations'] = ["Face detection is working well"]
        
        self.test_results['face_detection'] = results
        return results
    
    def run_face_verification_test(self, frame):
        """Test face verification for exam authorization"""
        if frame is None:
            return {'status': 'error', 'message': 'No camera feed available'}
        
        try:
            # Import face recognition system
            from .face_recognition import quick_face_verification
            
            # Run quick face verification
            verification_result = quick_face_verification(frame, max_attempts=2)
            
            results = {
                'verification_status': verification_result['status'],
                'verified': verification_result['verified'],
                'message': verification_result['message'],
                'recommendations': []
            }
            
            if verification_result['verified']:
                results['recommendations'].append("✅ Face verification successful - You can start the exam")
            else:
                results['recommendations'].append("❌ Face verification failed - Please register your face first")
                if verification_result['status'] == 'no_registered_faces':
                    results['recommendations'].append("Click 'Register Face' button to register your identity")
                elif verification_result['status'] == 'no_face_detected':
                    results['recommendations'].append("Position your face clearly in front of camera")
                elif verification_result['status'] == 'multiple_faces':
                    results['recommendations'].append("Ensure only one person is in the camera frame")
                elif verification_result['status'] == 'unauthorized':
                    results['recommendations'].append("This face is not registered in the system")
            
            self.test_results['face_verification'] = results
            return results
            
        except Exception as e:
            results = {
                'status': 'error',
                'message': f'Face verification test failed: {str(e)}',
                'recommendations': ["Ensure face recognition system is properly initialized"]
            }
            self.test_results['face_verification'] = results
            return results
    
    def run_rules_confirmation_test(self):
        """Test exam rules confirmation"""
        results = {
            'rules_confirmed': False,
            'exam_rules': [
                'No other persons should be in room',
                'No talking during the exam',
                'No looking away from screen frequently',
                'No switching tabs or applications',
                'No mobile phone usage during exam',
                'Maintain eye contact with screen',
                'No unauthorized materials nearby',
                'Follow all examiner instructions'
            ],
            'recommendations': [
                'Please read and understand all exam rules',
                'Violations will be detected and reported',
                'Ensure you can follow these rules before starting'
            ]
        }
        
        self.test_results['rules_confirmation'] = results
        return results

    def run_audio_test(self):
        """Test audio input and background noise levels"""
        try:
            import pyaudio
            import audioop as ao
            
            # Audio test parameters
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            CHUNK = 1024
            RECORD_SECONDS = 3
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_chunk=CHUNK)
            
            print("[CALIBRATION] Testing audio levels for 3 seconds...")
            frames = []
            
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            # Calculate audio levels
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            
            # Calculate RMS (root mean square) for volume
            rms = np.sqrt(np.mean(audio_data**2))
            volume = 20 * np.log10(rms + 1e-6)  # Convert to dB
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            results = {
                'volume_db': float(volume),
                'audio_quality': 'good',
                'recommendations': []
            }
            
            # Evaluate audio quality
            if volume < -40:
                results['audio_quality'] = 'very_quiet'
                results['recommendations'].append("Microphone may not be working properly")
            elif volume > -10:
                results['audio_quality'] = 'noisy'
                results['recommendations'].append("Reduce background noise for better detection")
            else:
                results['recommendations'].append("Audio levels are optimal")
            
            self.test_results['audio'] = results
            return results
            
        except ImportError:
            results = {
                'status': 'warning',
                'message': 'PyAudio not available for audio testing',
                'recommendations': ["Install PyAudio for audio calibration: pip install pyaudio"]
            }
            self.test_results['audio'] = results
            return results
        except Exception as e:
            results = {
                'status': 'error',
                'message': f'Audio test failed: {str(e)}',
                'recommendations': ["Check microphone permissions and connection"]
            }
            self.test_results['audio'] = results
            return results
    
    def get_calibration_summary(self):
        """Get summary of all calibration results"""
        return {
            'calibration_data': self.calibration_data,
            'test_results': self.test_results,
            'current_step': self.steps[self.current_step] if self.current_step < len(self.steps) else 'completed',
            'progress': ((self.current_step + 1) / len(self.steps)) * 100
        }
    
    def get_optimal_settings(self):
        """Get optimal settings based on calibration results"""
        if not self.test_results:
            return {}
        
        optimal_settings = {
            'face_detection': {
                'scaleFactor': 1.1,
                'minNeighbors': 5,
                'minSize': (50, 50)
            },
            'audio_threshold': -25,  # dB
            'lighting_requirements': {
                'min_brightness': 50,
                'max_brightness': 200,
                'min_contrast': 30
            }
        }
        
        # Adjust based on test results
        if 'face_detection' in self.test_results:
            recommended = self.test_results['face_detection'].get('recommended_setting', 'conservative')
            if recommended == 'aggressive':
                optimal_settings['face_detection']['scaleFactor'] = 1.02
                optimal_settings['face_detection']['minNeighbors'] = 2
            elif recommended == 'balanced':
                optimal_settings['face_detection']['scaleFactor'] = 1.05
                optimal_settings['face_detection']['minNeighbors'] = 3
        
        return optimal_settings

# Global calibration wizard
calibration_wizard = CalibrationWizard()

def start_calibration_wizard():
    """Start the calibration wizard"""
    return calibration_wizard.start_calibration()

def run_calibration_test(step, frame=None):
    """Run specific calibration test"""
    if step == 'camera_position':
        return calibration_wizard.run_camera_position_test(frame)
    elif step == 'lighting':
        return calibration_wizard.run_lighting_test(frame)
    elif step == 'face_detection':
        return calibration_wizard.run_face_detection_test(frame)
    elif step == 'audio':
        return calibration_wizard.run_audio_test()
    else:
        return {'status': 'error', 'message': f'Unknown calibration step: {step}'}

def get_calibration_status():
    """Get current calibration status"""
    return calibration_wizard.get_calibration_summary()

def apply_optimal_settings():
    """Apply optimal settings from calibration"""
    return calibration_wizard.get_optimal_settings()
