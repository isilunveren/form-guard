import mediapipe as mp
from analyzer.pose_detector import calculate_angle


mp_pose = mp.solutions.pose


class SquatAnalyzer:
    def __init__(self):
        self.state = "STANDING"
        self.rep_count = 0

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

        if self.state == "STANDING" and angle < 120:
            self.state = "SQUATTING"
        elif self.state == "SQUATTING" and angle > 160:
            self.state = "STANDING"
            self.rep_count += 1

        errors = []
        if self.state == "SQUATTING":
            if abs(left_knee.x - left_ankle.x) > 0.08:
                errors.append("Knee cave")
            if abs(left_shoulder.x - left_hip.x) > 0.15:
                errors.append("Back rounding")

        return {
            "angle": angle,
            "state": self.state,
            "rep_count": self.rep_count,
            "errors": errors,
        }
