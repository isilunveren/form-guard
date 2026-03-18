from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
