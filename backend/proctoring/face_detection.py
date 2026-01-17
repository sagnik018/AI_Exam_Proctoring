import cv2

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces_strict = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(60, 60)
    )

    if len(faces_strict) == 0:
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(45, 45)
        )
    else:
        faces = faces_strict

    faces = list(faces)

    def _iou(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        x1 = max(ax, bx)
        y1 = max(ay, by)
        x2 = min(ax + aw, bx + bw)
        y2 = min(ay + ah, by + bh)
        inter_w = max(0, x2 - x1)
        inter_h = max(0, y2 - y1)
        inter = inter_w * inter_h
        if inter == 0:
            return 0.0
        union = (aw * ah) + (bw * bh) - inter
        return inter / union if union else 0.0

    if len(faces) > 1:
        faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        kept = []
        for r in faces:
            if all(_iou(r, k) < 0.35 for k in kept):
                kept.append(r)
        faces = kept

    if len(faces) > 1:
        faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        largest_area = faces[0][2] * faces[0][3]
        faces = [r for r in faces if (r[2] * r[3]) >= (0.30 * largest_area)]

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
        text = "No face detected"
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
