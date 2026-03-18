import mediapipe as mp
from analyzer.base_analyzer import BaseAnalyzer
from analyzer.pose_detector import calculate_angle

mp_pose = mp.solutions.pose


class BicepCurlAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("bicep_curl")

    @property
    def down_threshold(self):
        return 160

    @property
    def up_threshold(self):
        return 40

    def is_visible(self, landmarks):
        elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        return elbow.visibility > 0.5

    def get_primary_angle(self, landmarks):
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        return calculate_angle(
            [shoulder.x, shoulder.y], [elbow.x, elbow.y], [wrist.x, wrist.y]
        )

    def detect_errors(self, landmarks):
        errors = []
        if self.state != "ACTIVE":
            return errors

        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]

        if abs(elbow.x - hip.x) > 0.15:
            errors.append("elbow_flare")
        if abs(shoulder.y - hip.y) < 0.15:
            errors.append("shoulder_raise")

        return errors
