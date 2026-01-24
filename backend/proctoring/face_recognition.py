import cv2
import numpy as np
import os
import pickle
import time
from datetime import datetime

class FaceRecognitionSystem:
    def __init__(self, known_faces_dir="known_faces"):
        self.known_faces_dir = known_faces_dir
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.known_face_names = []
        self.known_face_encodings = []
        
        # Create known faces directory if it doesn't exist
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
        
        # Load known faces
        self._load_known_faces()
    
    def _load_known_faces(self):
        """Load known face encodings from directory"""
        self.known_face_encodings = []
        self.known_face_names = []
        
        if not os.path.exists(self.known_faces_dir):
            return
        
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith('.pkl'):
                filepath = os.path.join(self.known_faces_dir, filename)
                with open(filepath, 'rb') as f:
                    encoding_data = pickle.load(f)
                    self.known_face_encodings.append(encoding_data['encoding'])
                    self.known_face_names.append(encoding_data['name'])
        
        print(f"[FACE_RECOGNITION] Loaded {len(self.known_face_names)} known faces")
    
    def register_face(self, face_image, name):
        """Register a new face for recognition"""
        try:
            # Check if name already exists
            if any(n.lower() == name.lower() for n in self.known_face_names):
                return {'status': 'already_registered', 'message': f'User {name} is already registered.'}
            
            # Convert to grayscale
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            # Detect face
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
            
            if len(faces) > 0:
                # Get the largest face
                face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = face
                face_roi = gray[y:y+h, x:x+w]
                
                # Save the face encoding
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.pkl"
                filepath = os.path.join(self.known_faces_dir, filename)
                
                with open(filepath, 'wb') as f:
                    pickle.dump({'name': name, 'encoding': face_roi}, f)
                
                # Reload known faces
                self._load_known_faces()
                
                # Train the recognizer with all faces
                if len(self.known_face_encodings) > 0:
                    labels = list(range(len(self.known_face_encodings)))
                    self.recognizer.train(self.known_face_encodings, np.array(labels))
                
                print(f"[FACE_RECOGNITION] Registered new face: {name}")
                return {'status': 'success', 'message': f'Successfully registered {name}'}
            else:
                return {'status': 'error', 'message': 'No face detected. Please ensure your face is clearly visible.'}
                
        except Exception as e:
            error_msg = f'Registration error: {str(e)}'
            print(f"[FACE_RECOGNITION ERROR] {error_msg}")
            return {'status': 'error', 'message': error_msg}
    
    def quick_verification(self, frame, max_attempts=3):
        """Quick face verification before exam starts"""
        if len(self.known_face_encodings) == 0:
            return {
                'status': 'no_registered_faces',
                'message': 'No registered faces found. Please register a user first.',
                'verified': False
            }
        
        for attempt in range(max_attempts):
            try:
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Check lighting conditions first
                brightness = np.mean(gray)
                contrast = np.std(gray)
                
                # Debug logging for lighting values
                print(f"[LIGHTING_DEBUG] Brightness: {brightness:.1f}, Contrast: {contrast:.1f}")
                
                # More lenient lighting thresholds for normal room conditions
                if brightness < 30:
                    print(f"[LIGHTING_DEBUG] Poor lighting detected: {brightness:.1f} < 30")
                    return {
                        'status': 'poor_lighting',
                        'message': 'Face not visible due to very poor lighting. Please ensure some lighting is available.',
                        'verified': False,
                        'lighting_advice': 'Turn on room lights or use natural lighting'
                    }
                elif brightness > 240:
                    print(f"[LIGHTING_DEBUG] Overexposed detected: {brightness:.1f} > 240")
                    return {
                        'status': 'overexposed',
                        'message': 'Face is overexposed due to very bright lighting. Please adjust lighting.',
                        'verified': False,
                        'lighting_advice': 'Reduce bright lighting or adjust camera position'
                    }
                elif contrast < 15:
                    print(f"[LIGHTING_DEBUG] Low contrast detected: {contrast:.1f} < 15")
                    return {
                        'status': 'low_contrast',
                        'message': 'Poor contrast affecting face detection. Please improve lighting slightly.',
                        'verified': False,
                        'lighting_advice': 'Ensure even lighting without heavy shadows'
                    }
                
                print(f"[LIGHTING_DEBUG] Lighting acceptable: Brightness={brightness:.1f}, Contrast={contrast:.1f}")
                
                # Detect faces with more lenient parameters
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.05,  # More sensitive to different face sizes
                    minNeighbors=3,     # Less strict neighbor requirement
                    minSize=(40, 40),   # Smaller minimum face size
                    maxSize=(400, 400)  # Reasonable maximum face size
                )
                
                if len(faces) == 0:
                    if attempt == max_attempts - 1:
                        return {
                            'status': 'no_face_detected',
                            'message': 'No face detected. Please position yourself in front of camera with proper lighting.',
                            'verified': False,
                            'lighting_advice': 'Ensure your face is well-lit and clearly visible'
                        }
                    continue
                
                if len(faces) > 1:
                    return {
                        'status': 'multiple_faces',
                        'message': 'Multiple faces detected. Only one person should be in frame.',
                        'verified': False
                    }
                
                # Get single face
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                
                # Check if face is properly sized (more lenient)
                face_area = w * h
                frame_area = frame.shape[0] * frame.shape[1]
                face_ratio = face_area / frame_area
                
                if face_ratio < 0.02:  # Face too small (reduced from 0.05)
                    return {
                        'status': 'face_too_small',
                        'message': 'Face too small or too far from camera. Please move closer.',
                        'verified': False,
                        'lighting_advice': 'Move closer to camera for better face visibility'
                    }
                
                # Try to recognize the face
                if len(self.known_face_encodings) > 0:
                    # Ensure recognizer is trained
                    try:
                        label, confidence = self.recognizer.predict(face_roi)
                    except cv2.error:
                        return {
                            'status': 'model_not_trained',
                            'message': 'Face recognition model not trained. Please register a face first.',
                            'verified': False
                        }
                    
                    if confidence < 100:  # Good confidence threshold
                        name = self.known_face_names[label] if label < len(self.known_face_names) else "Unknown"
                        
                        if name != "Unknown":
                            return {
                                'status': 'verified',
                                'message': f'Face verified: {name} (Confidence: {100-confidence:.1f}%)',
                                'verified': True,
                                'name': name,
                                'confidence': 100 - confidence
                            }
                        else:
                            return {
                                'status': 'unauthorized',
                                'message': 'Unauthorized face detected. Access denied.',
                                'verified': False
                            }
                    else:
                        if attempt == max_attempts - 1:
                            return {
                                'status': 'low_confidence',
                                'message': 'Face recognition failed. Please ensure proper lighting and positioning.',
                                'verified': False,
                                'lighting_advice': 'Move to optimal lighting conditions and try again'
                            }
            
            except Exception as e:
                print(f"[FACE_RECOGNITION ERROR] {e}")
                if attempt == max_attempts - 1:
                    return {
                        'status': 'error',
                        'message': f'Face verification error: {str(e)}',
                        'verified': False
                    }
        
        return {
            'status': 'failed',
            'message': 'Face verification failed after multiple attempts.',
            'verified': False
        }

    def recognize_face(self, frame):
        """Recognize faces in frame and verify if authorized"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
            
            recognized_faces = []
            
            for (x, y, w, h) in faces:
                # Try to recognize each face
                face_roi = gray[y:y+h, x:x+w]
                
                if len(self.known_face_encodings) > 0:
                    # Predict the face
                    label, confidence = self.recognizer.predict(face_roi)
                    
                    if confidence < 100:  # Confidence threshold
                        name = self.known_face_names[label] if label < len(self.known_face_names) else "Unknown"
                        recognized_faces.append({
                            'name': name,
                            'confidence': confidence,
                            'location': (x, y, w, h),
                            'authorized': name != "Unknown"
                        })
                        
                        # Draw rectangle and name on frame
                        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        cv2.putText(frame, f"{name} ({confidence:.1f}%)", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    else:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            return recognized_faces
            
        except Exception as e:
            print(f"[FACE_RECOGNITION ERROR] {e}")
            return []
    
    def verify_authorized_user(self, frame):
        """Check if any detected face matches authorized users"""
        recognized_faces = self.recognize_face(frame)
        
        authorized_present = False
        unauthorized_present = False
        
        for face in recognized_faces:
            if face['authorized']:
                authorized_present = True
            else:
                unauthorized_present = True
        
        return {
            'authorized_present': authorized_present,
            'unauthorized_present': unauthorized_present,
            'total_faces': len(recognized_faces),
            'details': recognized_faces
        }

# Global face recognition system
face_recognition = FaceRecognitionSystem()

def initialize_face_recognition():
    """Initialize face recognition system"""
    return face_recognition

def register_new_user(face_image, name):
    """Register a new authorized user"""
    return face_recognition.register_face(face_image, name)

def quick_face_verification(frame, max_attempts=3):
    """Quick face verification before exam starts"""
    return face_recognition.quick_verification(frame, max_attempts)

def verify_user_identity(frame):
    """Verify if user in frame is authorized"""
    return face_recognition.verify_authorized_user(frame)
