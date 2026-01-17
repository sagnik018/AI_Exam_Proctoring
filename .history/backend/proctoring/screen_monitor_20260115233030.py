import time

last_switch_time = 0
COOLDOWN = 2  # seconds

def detect_tab_switch():
    global last_switch_time

    current_time = time.time()
    if current_time - last_switch_time > COOLDOWN:
        last_switch_time = current_time
        return True

    return False

