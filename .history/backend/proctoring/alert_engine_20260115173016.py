from datetime import datetime

def generate_alert(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ALERT | {timestamp}] {event}")
