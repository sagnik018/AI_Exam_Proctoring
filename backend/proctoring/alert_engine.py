from datetime import datetime
import threading
import time

# Store last alert globally (used by UI)
LAST_ALERT = {
    "message": "",
    "level": "INFO",
    "time": ""
}

# Alert queue for multiple warnings
ALERT_QUEUE = []
ALERT_LOCK = threading.Lock()
CURRENT_ALERT_INDEX = 0
ALERT_DISPLAY_DURATION = 3  # seconds per alert

def generate_alert(event, level="WARNING"):
    """
    Generate an alert with timestamp and severity.
    Stores latest alert for UI + prints to console.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alert = {
        "message": event,
        "level": level,
        "time": timestamp
    }
    
    # Add to queue
    with ALERT_LOCK:
        ALERT_QUEUE.append(alert)
        print(f"[{level} | {timestamp}] {event} - Queued (Total: {len(ALERT_QUEUE)})")
    
    # If this is the first alert, start displaying it
    if len(ALERT_QUEUE) == 1:
        display_next_alert()

def display_next_alert():
    """
    Display the next alert in the queue
    """
    global CURRENT_ALERT_INDEX
    
    with ALERT_LOCK:
        if CURRENT_ALERT_INDEX < len(ALERT_QUEUE):
            # Set current alert
            current_alert = ALERT_QUEUE[CURRENT_ALERT_INDEX]
            LAST_ALERT["message"] = current_alert["message"]
            LAST_ALERT["level"] = current_alert["level"]
            LAST_ALERT["time"] = current_alert["time"]
            
            print(f"[DISPLAYING] {current_alert['message']}")
            
            # Move to next alert after duration
            threading.Timer(ALERT_DISPLAY_DURATION, advance_alert_queue).start()

def advance_alert_queue():
    """
    Move to the next alert in the queue
    """
    global CURRENT_ALERT_INDEX
    
    with ALERT_LOCK:
        CURRENT_ALERT_INDEX += 1
        
        if CURRENT_ALERT_INDEX < len(ALERT_QUEUE):
            # Display next alert
            display_next_alert()
        else:
            # Reset queue when done
            ALERT_QUEUE.clear()
            CURRENT_ALERT_INDEX = 0
            LAST_ALERT["message"] = ""
            LAST_ALERT["level"] = "INFO"
            LAST_ALERT["time"] = ""

def clear_alert_queue():
    """
    Clear the alert queue and reset
    """
    global CURRENT_ALERT_INDEX
    
    with ALERT_LOCK:
        ALERT_QUEUE.clear()
        CURRENT_ALERT_INDEX = 0
        LAST_ALERT["message"] = ""
        LAST_ALERT["level"] = "INFO"
        LAST_ALERT["time"] = ""
        print("[ALERT QUEUE] Cleared")

def get_queue_status():
    """
    Get current queue status for debugging
    """
    with ALERT_LOCK:
        return {
            "queue_length": len(ALERT_QUEUE),
            "current_index": CURRENT_ALERT_INDEX,
            "current_alert": LAST_ALERT
        }

def get_last_alert():
    """
    Returns the current alert being displayed (for web UI).
    """
    return LAST_ALERT
