import cv2
import numpy as np
import os
import time
import threading
from datetime import datetime
from PIL import ImageGrab

class ScreenRecorder:
    def __init__(self, output_dir="screenshots"):
        self.output_dir = output_dir
        self.recording = False
        self.screenshot_interval = 60  # Take screenshot every 1 minute
        self.last_screenshot_time = 0
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def start_recording(self):
        """Start periodic screenshot capture"""
        self.recording = True
        self.last_screenshot_time = time.time()
        threading.Thread(target=self._record_loop, daemon=True).start()
    
    def stop_recording(self):
        """Stop screenshot capture"""
        self.recording = False
    
    def _record_loop(self):
        """Main recording loop"""
        while self.recording:
            current_time = time.time()
            
            # Take screenshot if interval has passed
            if current_time - self.last_screenshot_time >= self.screenshot_interval:
                self._take_screenshot()
                self.last_screenshot_time = current_time
            
            time.sleep(1)  # Check every second
    
    def _take_screenshot(self):
        """Capture and save screenshot"""
        try:
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Convert to numpy array (OpenCV format)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save screenshot
            cv2.imwrite(filepath, screenshot_cv)
            
            print(f"[SCREENSHOT] Saved: {filename}")
            
        except Exception as e:
            print(f"[SCREENSHOT ERROR] {e}")

# Global screen recorder instance
screen_recorder = ScreenRecorder()

def start_screen_recording():
    """Start screen recording for evidence collection"""
    screen_recorder.start_recording()

def stop_screen_recording():
    """Stop screen recording"""
    screen_recorder.stop_recording()

def get_screenshot_count():
    """Get count of screenshots taken"""
    if os.path.exists(screen_recorder.output_dir):
        return len([f for f in os.listdir(screen_recorder.output_dir) if f.endswith('.jpg')])
    return 0
