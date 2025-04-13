import pygetwindow as gw
import win32gui
import win32con
from PIL import ImageGrab
import time
import os
import subprocess
import ctypes  # For getting screen dimensions

# Get screen dimensions
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

command = "C:/Users/lifei/OneDrive/Documents/EmotionDetection/emotion-detection/face_classification/src/main_emotion_classifier.py C:/Users/lifei/OneDrive/Documents/EmotionDetection/emotion-detection/face_classification/images/audience.png"
output_folder = "C:/Users/lifei/OneDrive/Documents/EmotionDetection/emotion-detection/face_classification/images"
count = 0
run = True
while (True):
    if (count > 0 and run == True):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
    count += 1
    time.sleep(1)
    print("Searching for Zoom window...")
    
    # Find Zoom windows with more flexible title matching
    zoom_windows = [w for w in gw.getAllWindows() 
                   if w.title and ('zoom workplace' in w.title.lower() or 'zoom meeting' in w.title.lower())]
    
    print(f"Found {len(zoom_windows)} potential Zoom windows: {[w.title for w in zoom_windows]}")
    try:
        if not zoom_windows and count == 1:
            print("No Zoom windows found.")
            win32gui.ShowWindow(zoom_window_handle, win32con.SW_RESTORE)     
            time.sleep(0.5)
            win32gui.SetForegroundWindow(zoom_window_handle)
            time.sleep(0.5)
            win32gui.ShowWindow(zoom_window_handle, win32con.SW_MAXIMIZE)
            time.sleep(.5)  # Allow time for the window to maximize
    
        
    
    # Select the first matching window
        zoom_window = zoom_windows[0]
        zoom_window_handle = zoom_window._hWnd
        print(f"Working with window: '{zoom_window.title}'")
        
        # Force window to normal state first (from any state)
        
        # Move the window to the bottom-right corner
        
        
        
        win32gui.ShowWindow(zoom_window_handle, win32con.SW_RESTORE)     
        time.sleep(.5)
        # Bring to foreground
        win32gui.SetForegroundWindow(zoom_window_handle)
        time.sleep(0.5)
        
        # Get window position and dimensions
        left, top, right, bottom = win32gui.GetWindowRect(zoom_window_handle)
        print(f"Window dimensions: ({left}, {top}) to ({right}, {bottom})")
        
        # Take screenshot
        bbox = (left, top, right, bottom)
        img = ImageGrab.grab(bbox)
        screenshot_path = os.path.join(output_folder, f"audience.png")
        img.save(screenshot_path)
        print(f"Screenshot saved as {screenshot_path}")
        run = True
    except Exception as e:
        print(f"Error interacting with Zoom window: {e}")
        run = False


