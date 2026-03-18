from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import json
import cv2
import base64
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from analyzer.squat_analyzer import SquatAnalyzer
from analyzer.deadlift_analyzer import DeadliftAnalyzer
from analyzer.lunge_analyzer import LungeAnalyzer
from analyzer.bicep_curl_analyzer import BicepCurlAnalyzer
from analyzer.shoulder_press_analyzer import ShoulderPressAnalyzer
from analyzer.pushup_analyzer import PushupAnalyzer
from analyzer.plank_analyzer import PlankAnalyzer
import mediapipe as mp

ANALYZERS = {
    "squat": SquatAnalyzer,
    "deadlift": DeadliftAnalyzer,
    "lunge": LungeAnalyzer,
    "bicep_curl": BicepCurlAnalyzer,
    "shoulder_press": ShoulderPressAnalyzer,
    "pushup": PushupAnalyzer,
    "plank": PlankAnalyzer,
}

mp_pose = mp.solutions.pose

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return psycopg2.connect(
        dbname="formguard", user="isilunveren", host="localhost", port="5432"
    )


@app.get("/sessions")
def get_sessions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.id, s.exercise_type, s.started_at, s.duration_seconds,
               COUNT(r.id) as total_reps,
               ROUND(AVG(r.quality_score)::numeric, 2) as avg_quality
        FROM sessions s
        LEFT JOIN reps r ON r.session_id = s.id
        GROUP BY s.id
        ORDER BY s.started_at DESC
    """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": row[0],
            "exercise_type": row[1],
            "started_at": str(row[2]),
            "duration_seconds": row[3],
            "total_reps": row[4],
            "avg_quality": float(row[5]) if row[5] else None,
        }
        for row in rows
    ]


@app.get("/sessions/{session_id}/reps")
def get_reps(session_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT rep_number, quality_score, errors, duration_ms
        FROM reps
        WHERE session_id = %s
        ORDER BY rep_number
    """,
        (session_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "rep_number": row[0],
            "quality_score": row[1],
            "errors": row[2],
            "duration_ms": row[3],
        }
        for row in rows
    ]


@app.get("/stats")
def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM reps")
    total_reps = cur.fetchone()[0]

    cur.execute("SELECT errors FROM reps WHERE errors != '[]'")
    rows = cur.fetchall()
    error_counts = {}
    for row in rows:
        for error in row[0]:
            error_counts[error] = error_counts.get(error, 0) + 1

    cur.close()
    conn.close()
    return {
        "total_sessions": total_sessions,
        "total_reps": total_reps,
        "error_counts": error_counts,
    }


@app.websocket("/ws/{exercise}")
async def workout_stream(websocket: WebSocket, exercise: str):
    await websocket.accept()

    if exercise not in ANALYZERS:
        await websocket.close()
        return

    analyzer = ANALYZERS[exercise]()
    cap = cv2.VideoCapture(0)

    try:
        with mp_pose.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        ) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                analysis = None
                if results.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                    )
                    landmarks = results.pose_landmarks.landmark
                    analysis = analyzer.analyze(landmarks)

                _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 60])
                frame_b64 = base64.b64encode(buffer).decode("utf-8")

                await websocket.send_json(
                    {
                        "frame": frame_b64,
                        "analysis": analysis,
                    }
                )

                await asyncio.sleep(0.033)

    except WebSocketDisconnect:
        pass
    finally:
        cap.release()
        analyzer.finish()
