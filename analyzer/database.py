import psycopg2
import json
from datetime import datetime


def get_connection():
    return psycopg2.connect(
        dbname="formguard", user="isilunveren", host="localhost", port="5432"
    )


def create_session(exercise_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (exercise_type, started_at) VALUES (%s, %s) RETURNING id",
        (exercise_type, datetime.now()),
    )
    session_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return session_id


def save_rep(session_id, rep_number, quality_score, errors, duration_ms):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO reps (session_id, rep_number, quality_score, errors, duration_ms)
           VALUES (%s, %s, %s, %s, %s)""",
        (session_id, rep_number, quality_score, json.dumps(errors), duration_ms),
    )
    conn.commit()
    cur.close()
    conn.close()


def end_session(session_id, duration_seconds):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE sessions SET duration_seconds = %s WHERE id = %s",
        (duration_seconds, session_id),
    )
    conn.commit()
    cur.close()
    conn.close()
