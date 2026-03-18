import mediapipe as mp
from analyzer.base_analyzer import BaseAnalyzer
from analyzer.pose_detector import calculate_angle


mp_pose = mp.solutions.pose


class DeadliftAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("deadlift")

    @property
    def down_threshold(self):
        return 110

    @property
    def up_threshold(self):
        return 160

    def is_visible(self, landmarks):
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        return hip.visibility > 0.5

    def get_primary_angle(self, landmarks):
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        return calculate_angle(
            [shoulder.x, shoulder.y], [hip.x, hip.y], [knee.x, knee.y]
        )

    def detect_errors(self, landmarks):
        errors = []
        if self.state != "ACTIVE":
            return errors

        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

        if abs(shoulder.x - hip.x) > 0.15:
            errors.append("back_rounding")

        knee_angle = calculate_angle(
            [hip.x, hip.y], [knee.x, knee.y], [ankle.x, ankle.y]
        )
        if knee_angle > 160:
            errors.append("knees_locked_early")

        return errors
