import mediapipe as mp
from analyzer.base_analyzer import BaseAnalyzer
from analyzer.pose_detector import calculate_angle


mp_pose = mp.solutions.pose


class LungeAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("lunge")

    @property
    def down_threshold(self):
        return 110

    @property
    def up_threshold(self):
        return 155

    def is_visible(self, landmarks):
        knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        return knee.visibility > 0.5

    def get_primary_angle(self, landmarks):
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        return calculate_angle([hip.x, hip.y], [knee.x, knee.y], [ankle.x, ankle.y])

    def detect_errors(self, landmarks):
        errors = []
        if self.state != "ACTIVE":
            return errors

        knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]

        if knee.x - ankle.x > 0.10:
            errors.append("knee_over_toe")
        if abs(shoulder.x - hip.x) > 0.12:
            errors.append("torso_lean")

        return errors
