from datetime import datetime

# Store last alert globally (used by UI)
LAST_ALERT = {
    "message": "",
    "level": "INFO",
    "time": ""
}

def generate_alert(event, level="WARNING"):
    """
    Generate an alert with timestamp and severity.
    Stores latest alert for UI + prints to console.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    LAST_ALERT["message"] = event
    LAST_ALERT["level"] = level
    LAST_ALERT["time"] = timestamp

    print(f"[{level} | {timestamp}] {event}")


def get_last_alert():
    """
    Returns the last generated alert (for web UI).
    """
    return LAST_ALERT
