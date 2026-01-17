import time

last_active = time.time()

def detect_tab_switch(current_time):
    global last_active
    if current_time - last_active > 5:
        last_active = current_time
        return True
    return False