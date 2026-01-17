# backend/database/db.py
import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exam_logs.db"))
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

def log_event(event):
    cursor.execute("INSERT INTO logs(event) VALUES(?)", (event,))
    conn.commit()

# ✅ ADDED FUNCTION (for admin.html)
def get_logs():
    cursor.execute("SELECT event, timestamp FROM logs ORDER BY timestamp DESC")
    return cursor.fetchall()
