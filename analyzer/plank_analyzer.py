import time
import mediapipe as mp
from analyzer.base_analyzer import BaseAnalyzer
from analyzer.pose_detector import calculate_angle
from analyzer.database import create_session, save_rep, end_session

mp_pose = mp.solutions.pose


class PlankAnalyzer:
    def __init__(self):
        self.exercise_type = "plank"
        self.session_id = create_session("plank")
        self.session_start = time.time()
        self.hold_seconds = 0
        self.rep_count = 0

    @property
    def state(self):
        return "HOLDING"

    def is_visible(self, landmarks):
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        return shoulder.visibility > 0.5

    def analyze(self, landmarks):
        if landmarks is None:
            return None
        if not self.is_visible(landmarks):
            return None

        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

        body_angle = calculate_angle(
            [shoulder.x, shoulder.y], [hip.x, hip.y], [ankle.x, ankle.y]
        )

        self.hold_seconds = int(time.time() - self.session_start)

        errors = []
        if hip.y < shoulder.y - 0.08:
            errors.append("hips_raised")
        if hip.y > shoulder.y + 0.08:
            errors.append("hips_sagging")

        return {
            "angle": round(body_angle, 2),
            "state": "HOLDING",
            "rep_count": self.hold_seconds,
            "errors": errors,
            "exercise_type": "plank",
        }

    def finish(self):
        duration = int(time.time() - self.session_start)
        save_rep(self.session_id, 1, 1.0, [], duration * 1000)
        end_session(self.session_id, duration)
