# backend/database/db.py
import sqlite3

conn = sqlite3.connect("exam_logs.db", check_same_thread=False)
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
# backend/database/db.py
import sqlite3

conn = sqlite3.connect("exam_logs.db", check_same_thread=False)
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

# ✅ ADDED FUNCTION (as requested)
def get_logs():
    cursor.execute("SELECT event, timestamp FROM logs ORDER BY timestamp DESC")
    return cursor.fetchall()
