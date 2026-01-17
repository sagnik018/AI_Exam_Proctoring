import time

last_active = time.time()
COOLDOWN = 10  # seconds

def detect_tab_switch(current_time):
    global last_active

    if current_time - last_active > COOLDOWN:
        last_active = current_time
        return True

    return False
