import cv2
import mediapipe as mp
from analyzer.pose_detector import get_landmarks, draw_pose
from analyzer.squat_analyzer import SquatAnalyzer


mp_pose = mp.solutions.pose

cap = cv2.VideoCapture("squat.mp4")
analyzer = SquatAnalyzer()

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            draw_pose(image, results)
            landmarks = get_landmarks(results)
            result = analyzer.analyze(landmarks)

            if result:
                cv2.putText(
                    image,
                    f"Angle: {result['angle']}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )
                cv2.putText(
                    image,
                    f"Reps: {result['rep_count']}",
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 255, 0),
                    3,
                )
                cv2.putText(
                    image,
                    f"State: {result['state']}",
                    (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 0),
                    2,
                )

                y_offset = 200
                for error in result["errors"]:
                    cv2.putText(
                        image,
                        error,
                        (30, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2,
                    )
                    y_offset += 40

        cv2.imshow("Form Guard", image)
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
analyzer.finish()
