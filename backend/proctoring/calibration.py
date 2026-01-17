import cv2
import numpy as np
import time
import json
import os
from datetime import datetime

class CalibrationWizard:
    def __init__(self):
        self.calibration_data = {}
        self.calibration_file = "calibration_settings.json"
        self.steps = [
            'camera_position',
            'lighting_check', 
            'face_detection_test',
            'audio_test',
            'final_settings'
        ]
        self.current_step = 0
        self.test_results = {}
        
        # Load existing calibration if available
        self._load_calibration()
    
    def _load_calibration(self):
        """Load existing calibration settings"""
        try:
            if os.path.exists(self.calibration_file):
                with open(self.calibration_file, 'r') as f:
                    self.calibration_data = json.load(f)
                    print(f"[CALIBRATION] Loaded existing settings")
        except Exception as e:
            print(f"[CALIBRATION] Could not load settings: {e}")
            self.calibration_data = {}
    
    def _save_calibration(self):
        """Save calibration settings"""
        try:
            with open(self.calibration_file, 'w') as f:
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
            'current_step': self.steps[self.current_step],
            'total_steps': len(self.steps),
            'progress': 0
        }
    
    def next_step(self):
        """Move to next calibration step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            return {
                'status': 'in_progress',
                'current_step': self.steps[self.current_step],
                'total_steps': len(self.steps),
                'progress': (self.current_step + 1) / len(self.steps) * 100
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
