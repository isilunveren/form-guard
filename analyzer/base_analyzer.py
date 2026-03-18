from abc import ABC, abstractmethod
import time
from analyzer.database import create_session, save_rep, end_session


class BaseAnalyzer(ABC):
    def __init__(self, exercise_type):
        self.exercise_type = exercise_type
        self.state = "STANDING"
        self.rep_count = 0
        self.session_id = create_session(exercise_type)
        self.session_start = time.time()
        self.rep_start = time.time()

    def analyze(self, landmarks):
        if landmarks is None:
            return None

        if not self.is_visible(landmarks):
            return None

        angle = self.get_primary_angle(landmarks)
        errors = self.detect_errors(landmarks)

        if self.state == "STANDING" and angle < self.down_threshold:
            self.state = "ACTIVE"
            self.rep_start = time.time()
        elif self.state == "ACTIVE" and angle > self.up_threshold:
            self.state = "STANDING"
            self.rep_count += 1
            duration_ms = int((time.time() - self.rep_start) * 1000)
            quality_score = round(max(0.0, 1.0 - len(errors) * 0.3), 2)
            save_rep(
                self.session_id, self.rep_count, quality_score, errors, duration_ms
            )

        return {
            "angle": angle,
            "state": self.state,
            "rep_count": self.rep_count,
            "errors": errors,
            "exercise_type": self.exercise_type,
        }

    def finish(self):
        duration = int(time.time() - self.session_start)
        end_session(self.session_id, duration)

    @abstractmethod
    def is_visible(self, landmarks):
        pass

    @abstractmethod
    def get_primary_angle(self, landmarks):
        pass

    @abstractmethod
    def detect_errors(self, landmarks):
        pass

    @property
    @abstractmethod
    def down_threshold(self):
        pass

    @property
    @abstractmethod
    def up_threshold(self):
        pass
