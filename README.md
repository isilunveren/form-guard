# Form Guard

Real-time workout form analysis powered by pose estimation. Tracks reps, detects form errors, and visualizes session history through a web dashboard.

## Features

- Real-time pose detection via MediaPipe BlazePose (33 keypoints)
- Joint angle calculation using vector math
- Rep counting with Finite State Machine
- Form error detection per exercise
- Session and rep history stored in PostgreSQL
- Web dashboard with live video feed and rep quality charts

## Supported Exercises

| Exercise       | Tracked Angle                    | Errors Detected                   |
| -------------- | -------------------------------- | --------------------------------- |
| Squat          | Knee (hip → knee → ankle)        | Knee cave, back rounding          |
| Deadlift       | Hip (shoulder → hip → knee)      | Back rounding, knees locked early |
| Lunge          | Knee (hip → knee → ankle)        | Knee over toe, torso lean         |
| Bicep Curl     | Elbow (shoulder → elbow → wrist) | Elbow flare, shoulder raise       |
| Shoulder Press | Elbow (shoulder → elbow → wrist) | Back arch, neck strain            |
| Push-up        | Elbow (shoulder → elbow → wrist) | Hips sagging, hips raised         |
| Plank          | Body alignment                   | Hips sagging, hips raised         |

## Architecture

```
Webcam
  ↓
MediaPipe BlazePose → 33 keypoints
  ↓
Feature Engineering → joint angles, visibility filtering
  ↓
Analyzer (FSM) → rep count, state, errors
  ↓
WebSocket → React Dashboard (live feed + stats)
  ↓
PostgreSQL → session & rep history
```

## Tech Stack

- **CV & Analysis:** MediaPipe, OpenCV, NumPy
- **Backend:** Python, FastAPI, WebSocket, PostgreSQL
- **Frontend:** React
