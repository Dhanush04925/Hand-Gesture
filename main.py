import cv2
import time
import math
import numpy as np
import pyautogui
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Camera setup
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
detector = htm.handDetector(maxHands=1, detectionCon=0.7, trackCon=0.7)

# Audio control setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()  

minVol, maxVol = volRange[0], volRange[1]
hmin, hmax = 5, 80  # Adjusted hand range for better precision

# Sensitivity Control (Tuned)
volSensitivity = 1.4  
smooth_factor = 0.2  # For Exponential Moving Average (Smoothing)

prev_vol = volume.GetMasterVolumeLevel()  # Store previous volume

tipIds = [4, 8, 12, 16, 20]  
mode = 'N'
pinch_active = False
mode_active = False

pyautogui.FAILSAFE = False  
pyautogui.PAUSE = 0  

screen_w, screen_h = pyautogui.size()

click_delay = 0.5  # Time threshold for double click
last_click_time = 0  

while True:
    success, img = cap.read()
    if not success:
        continue  

    img = cv2.flip(img, 1)  
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=True)

    if len(lmList) == 0:
        mode = 'N'
        pinch_active = False
        mode_active = False
        continue  

    fingers = [1 if lmList[tipIds[i]][2] < lmList[tipIds[i] - 2][2] else 0 for i in range(1, 5)]
    fingers.insert(0, 1 if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1] else 0)

    # **Exit Condition using Hand Gesture**
    if fingers == [0, 1, 1, 1, 0]:  # Index, Middle, and Ring fingers up, Thumb and Pinky down
        print("🖐 Exit Gesture Detected! Closing Program...")
        break

    if mode == 'N' and not mode_active:
        if fingers == [0, 1, 0, 0, 0]:  
            mode = 'Scroll Up'
            mode_active = True
        elif fingers == [0, 1, 1, 0, 0]:  
            mode = 'Scroll Down'
            mode_active = True
        elif fingers == [1, 1, 0, 0, 0]:  
            mode = 'Volume'
            mode_active = True
        elif fingers == [1, 1, 1, 1, 1]:  
            mode = 'Cursor'
            mode_active = True

    if mode.startswith('Scroll'):
        finger_y = lmList[8][2]  
        scroll_speed = int(np.interp(finger_y, [50, 400], [150,10]))  

        if mode == 'Scroll Up' and fingers == [0, 1, 0, 0, 0]:
            pyautogui.scroll(scroll_speed)
        elif mode == 'Scroll Down' and fingers == [0, 1, 1, 0, 0]:
            pyautogui.scroll(-scroll_speed)

        if sum(fingers) == 0:  
            mode = 'N'
            mode_active = False

    if mode == 'Volume':
        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb
        x2, y2 = lmList[8][1], lmList[8][2]  # Index finger
        length = math.hypot(x2 - x1, y2 - y1)  # Distance between thumb and index

        # Adjust volume range based on sensitivity
        raw_vol = np.interp(length, [hmin, hmax], [minVol, maxVol]) * volSensitivity

        # Smooth volume transition using Exponential Moving Average (EMA)
        vol = (smooth_factor * raw_vol) + ((1 - smooth_factor) * prev_vol)
        prev_vol = vol  # Update previous volume for next iteration

        # Clamp volume within limits
        vol = max(minVol, min(vol, maxVol))
        volume.SetMasterVolumeLevel(vol, None)

        # Exit Volume Mode when Pinky is Raised
        if fingers[4] == 1:  
            mode = 'N'
            mode_active = False

    if mode == 'Cursor': 
        x1, y1 = lmList[12][1], lmList[12][2]  
        X = int(0.8 * pyautogui.position()[0] + 0.2 * np.interp(x1, [110, 620], [screen_w, 0]) * 1.5)  
        Y = int(0.8 * pyautogui.position()[1] + 0.2 * np.interp(y1, [20, 350], [0, screen_h]) * 1.5)
        pyautogui.moveTo(X, Y, duration=0.1)  

        x_thumb, y_thumb = lmList[4][1], lmList[4][2]  
        x_index, y_index = lmList[8][1], lmList[8][2]  
        distance = math.hypot(x_index - x_thumb, y_index - y_thumb)

        current_time = time.time()

        if distance < 30:  # Pinch detected
            if not pinch_active:
                if current_time - last_click_time < click_delay:
                    pyautogui.doubleClick()  
                else:
                    pyautogui.click()  
                last_click_time = current_time
                pinch_active = True
        elif distance > 40:
            pinch_active = False  

    if mode == 'Cursor' and sum(fingers) == 0:
        mode = 'N'
        mode_active = False

    # Display Sensitivity on Screen
    cv2.putText(img, f"Volume Sensitivity: {volSensitivity:.1f}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Hand LiveFeed', img)

    # **Exit on Keyboard Press 'e'**
    if cv2.waitKey(1) & 0xFF == ord('e'):
        print("🔴 'E' key pressed! Exiting program...")
        break

cap.release()
cv2.destroyAllWindows()