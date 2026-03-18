import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ab = a - b
    cb = c - b

    cosine = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
    angle = np.degrees(np.arccos(np.clip(cosine, -1, 1)))

    return round(angle, 2)


state = "STANDING"
rep_count = 0

cap = cv2.VideoCapture("squat.mp4")

# keep tracking without returning detection if detection confidence is over 0.5
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )

            landmarks = results.pose_landmarks.landmark

            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

            hip = [left_hip.x, left_hip.y]
            knee = [left_knee.x, left_knee.y]
            ankle = [left_ankle.x, left_ankle.y]

            angle = calculate_angle(hip, knee, ankle)

            if left_knee.visibility > 0.5:
                if state == "STANDING" and angle < 120:
                    state = "SQUATTING"
                elif state == "SQUATTING" and angle > 160:
                    state = "STANDING"
                    rep_count += 1

            cv2.putText(
                image,
                f"Angle: {angle}",
                (int(left_knee.x * image.shape[1]), int(left_knee.y * image.shape[0])),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                image,
                f"Reps: {rep_count}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3,
            )

            cv2.putText(
                image,
                f"State: {state}",
                (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2,
            )
        cv2.imshow("Form Guard", image)

        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
