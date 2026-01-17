
import mediapipe as mp
import cv2

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh()

def detect_head_movement(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    return results.multi_face_landmarks is not None
