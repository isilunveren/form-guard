import time
import mediapipe as mp
from analyzer.pose_detector import calculate_angle
from analyzer.database import create_session, save_rep, end_session


mp_pose = mp.solutions.pose


class SquatAnalyzer:
    def __init__(self):
        self.state = "STANDING"
        self.rep_count = 0
        self.session_id = create_session("squat")
        self.session_start = time.time()
        self.rep_start = time.time()

    def analyze(self, landmarks):
        if landmarks is None:
            return None

        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

        if left_knee.visibility < 0.5:
            return None

        hip = [left_hip.x, left_hip.y]
        knee = [left_knee.x, left_knee.y]
        ankle = [left_ankle.x, left_ankle.y]

        angle = calculate_angle(hip, knee, ankle)

        errors = []
        if self.state == "SQUATTING":
            if abs(left_knee.x - left_ankle.x) > 0.08:
                errors.append("knee_cave")
            if abs(left_shoulder.x - left_hip.x) > 0.15:
                errors.append("back_rounding")

        if self.state == "STANDING" and angle < 120:
            self.state = "SQUATTING"
            self.rep_start = time.time()
        elif self.state == "SQUATTING" and angle > 160:
            self.state = "STANDING"
            self.rep_count += 1
            duration_ms = int((time.time() - self.rep_start) * 1000)
            quality_score = (
                1.0 if len(errors) == 0 else round(1.0 - len(errors) * 0.3, 2)
            )
            save_rep(
                self.session_id, self.rep_count, quality_score, errors, duration_ms
            )

        return {
            "angle": angle,
            "state": self.state,
            "rep_count": self.rep_count,
            "errors": errors,
        }

    def finish(self):
        duration = int(time.time() - self.session_start)
        end_session(self.session_id, duration)
