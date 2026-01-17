import mediapipe as mp
import cv2

# MediaPipe Face Mesh
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def detect_head_movement(frame):
    """
    Detects abnormal head tilt and draws instructions on the frame.
    Returns True if suspicious head movement is detected.
    """

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return False

    landmarks = results.multi_face_landmarks[0].landmark

    # Key landmarks
    nose = landmarks[1]        # Nose tip
    left_eye = landmarks[33]   # Left eye
    right_eye = landmarks[263] # Right eye
    chin = landmarks[152]      # Chin

    # Horizontal tilt (looking left / right)
    horizontal_tilt = abs(left_eye.y - right_eye.y)

    # Vertical tilt (looking up / down)
    vertical_tilt = abs(nose.y - chin.y)

    suspicious = False
    message = "Head position normal"
    color = (0, 255, 0)

    # Thresholds (tuned for stability)
    if horizontal_tilt > 0.10:
        suspicious = True
        message = "Head tilted left/right"
        color = (0, 0, 255)

    elif vertical_tilt < 0.13:
        suspicious = True
        message = "Looking up or down"
        color = (0, 0, 255)


    # Draw instruction text on frame
    cv2.putText(
        frame,
        message,
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2,
        cv2.LINE_AA
    )

    return suspicious
