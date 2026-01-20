# backend/database/db.py
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

# Use absolute path for database file
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exam_logs.db"))

try:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    logger.info(f"Database initialized at: {DB_PATH}")
except Exception as e:
    logger.error(f"Failed to initialize database at {DB_PATH}: {str(e)}", exc_info=True)
    raise

def log_event(event):
    try:
        cursor.execute("INSERT INTO logs(event) VALUES(?)", (event,))
        conn.commit()
        logger.debug(f"Event logged: {event}")
    except Exception as e:
        logger.error(f"Failed to log event '{event}': {str(e)}", exc_info=True)

# ✅ ADDED FUNCTION (for admin.html)
def get_logs():
    try:
        cursor.execute("SELECT event, timestamp FROM logs ORDER BY timestamp DESC")
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {str(e)}", exc_info=True)
        return []
