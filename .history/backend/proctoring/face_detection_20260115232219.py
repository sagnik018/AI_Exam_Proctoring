import cv2

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(60, 60)
    )

    face_count = len(faces)

    # ---------------------------
    # DRAW FACE BOXES
    # ---------------------------
    for (x, y, w, h) in faces:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    # ---------------------------
    # INSTRUCTIONS ON FRAME
    # ---------------------------
    if face_count == 0:
        text = "No face detected - Please face the camera"
        color = (0, 0, 255)  # Red
    elif face_count == 1:
        text = "Face detected - OK"
        color = (0, 255, 0)  # Green
    else:
        text = "Multiple faces detected - Warning!"
        color = (0, 0, 255)  # Red

    cv2.putText(
        frame,
        text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        color,
        2,
        cv2.LINE_AA
    )

    return face_count, faces
