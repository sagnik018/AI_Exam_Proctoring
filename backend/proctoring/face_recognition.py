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
            # Convert to grayscale
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            # Detect face
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
            
            if len(faces) > 0:
                # Train recognizer with the face
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                
                # Train the recognizer
                self.recognizer.train([face_roi], np.array([1]))
                
                # Save the trained model
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.pkl"
                filepath = os.path.join(self.known_faces_dir, filename)
                
                with open(filepath, 'wb') as f:
                    pickle.dump({'name': name, 'encoding': face_roi}, f)
                
                # Reload known faces
                self._load_known_faces()
                
                print(f"[FACE_RECOGNITION] Registered new face: {name}")
                return True
                
        except Exception as e:
            print(f"[FACE_RECOGNITION ERROR] {e}")
            return False
    
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
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
                
                if len(faces) == 0:
                    if attempt == max_attempts - 1:
                        return {
                            'status': 'no_face_detected',
                            'message': 'No face detected. Please position yourself in front of camera.',
                            'verified': False
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
                
                # Try to recognize the face
                if len(self.known_face_encodings) > 0:
                    label, confidence = self.recognizer.predict(face_roi)
                    
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
                                'message': 'Face recognition failed. Please try again with better lighting.',
                                'verified': False
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
