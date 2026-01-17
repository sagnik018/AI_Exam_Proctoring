import mediapipe as mp
import cv2
import math

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(refine_landmarks=True)

def detect_head_movement(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return False

    landmarks = results.multi_face_landmarks[0].landmark

    # Nose tip & forehead
    nose = landmarks[1]
    forehead = landmarks[10]

    dx = abs(nose.x - forehead.x)
    dy = abs(nose.y - forehead.y)

    # Threshold → abnormal head tilt
    if dx > 0.03 or dy > 0.03:
        return True

    return False
