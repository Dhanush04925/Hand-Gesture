import cv2
import time
import math
import numpy as np
import HandTrackingModule as htm
import pyautogui
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

minVol, maxVol = -63, volRange[1]
hmin, hmax = 50, 200

tipIds = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
mode = 'N'
pinch_active = False  
mode_active = False  
last_mode = 'N'  
last_action = ''  

pyautogui.FAILSAFE = False  
pyautogui.PAUSE = 0  

while True:
    success, img = cap.read()
    if not success:
        continue  

    img = cv2.flip(img, 1)  
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=True)

    if len(lmList) == 0:
        if mode != 'N':
            print("❌ Hand Lost - Resetting Mode")
        mode = 'N'
        pinch_active = False
        mode_active = False
        last_mode = 'N'
        continue  

    fingers = [1 if lmList[tipIds[i]][2] < lmList[tipIds[i] - 2][2] else 0 for i in range(1, 5)]
    fingers.insert(0, 1 if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1] else 0)

    # 🚀 Detect mode based on gesture
    if mode == 'N' and not mode_active:
        if fingers == [0, 1, 0, 0, 0]:  # Only index finger up
            mode = 'Scroll'
            mode_active = True
        elif fingers == [1, 1, 0, 0, 0]:  # Index + Thumb up
            mode = 'Volume'
            mode_active = True
        elif fingers == [1, 1, 1, 1, 1]:  # Open palm
            mode = 'Cursor'
            mode_active = True

    if mode != last_mode:
        print(f"🔄 Entered {mode} Mode")
        last_mode = mode

    # Scroll Mode
    action = ""
    if mode == 'Scroll':
        if fingers == [0, 1, 0, 0, 0]:  
            pyautogui.scroll(300)
            action = "📜 Scrolling Up"
        elif fingers == [0, 1, 1, 0, 0]:  
            pyautogui.scroll(-300)
            action = "📜 Scrolling Down"

        if sum(fingers) == 0:  
            print("📜 Exiting Scroll Mode")
            mode = 'N'
            mode_active = False

    # Volume Mode
    if mode == 'Volume':
        x1, y1 = lmList[4][1], lmList[4][2]  
        x2, y2 = lmList[8][1], lmList[8][2]  
        length = math.hypot(x2 - x1, y2 - y1)

        vol = np.interp(length, [hmin, hmax], [minVol, maxVol])
        volume.SetMasterVolumeLevel(vol, None)

        action = f"🔊 Volume Set to {int(np.interp(length, [hmin, hmax], [0, 100]))}%"

        if fingers[4] == 1:  
            print("🔊 Exiting Volume Mode (Pinky Up)")
            mode = 'N'
            mode_active = False

    # Cursor Mode with Middle Finger Tracking
    if mode == 'Cursor':
        x1, y1 = lmList[12][1], lmList[12][2]  
        screen_w, screen_h = pyautogui.size()

        X = int(np.interp(x1, [110, 620], [0, screen_w]))  
        Y = int(np.interp(y1, [20, 350], [0, screen_h]))

        pyautogui.moveTo(X, Y, duration=0.1)  
        action = f"🖱 Moving Cursor to ({X}, {Y})"

        x_thumb, y_thumb = lmList[4][1], lmList[4][2]  
        x_index, y_index = lmList[8][1], lmList[8][2]  

        distance = math.hypot(x_index - x_thumb, y_index - y_thumb)

        if distance < 30 and not pinch_active:  
            pyautogui.click()
            action = "🖱 Click Detected"
            pinch_active = True  
        elif distance > 40:  
            pinch_active = False  

    if mode == 'Cursor' and sum(fingers) == 0:
        print("🖱 Exiting Cursor Mode")
        mode = 'N'
        mode_active = False

    if action and action != last_action:
        print(action)
        last_action = action

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
    cv2.imshow('Hand LiveFeed', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()