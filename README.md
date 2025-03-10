Team members:
  Dhanush yadav c (student of CVR College Of Engineering)
  Harshavardhan K (student of CVR College Of Engineering)
  Zenith golusu   (student of CVR College Of Engineering)
  Karthik reddy   (student of CVR College Of Engineering)
  Viishweshwar    (student of CVR College Of Engineering)

python packages needs to install
  opencv-python, pycaw, pyautogui, autopy, mediapipe, numpy

Gesture-Based Human-Computer Interaction System
  our project is a gesture-based human-computer interaction system that enables users to control various system functions (like volume, scrolling, and cursor movement) 
  using hand gestures detected through a webcam. This eliminates the need for a mouse, keyboard, or physical touch, making it useful for touchless interactions, especially in public kiosks and smart environments.

Key Technologies Used :
  Flask-SocketIO & Streamlit – (For web-based/real-time UI interaction)
  OpenCV – (For capturing and processing video frames)
  MediaPipe – (For real-time hand tracking)
  PyAutoGUI – (For controlling system functions like scrolling and mouse movement)
  PyCAW – (For controlling system volume)

Gesture-Based System Controls
  Once the hand landmarks are extracted, your project maps different finger positions to specific system actions:
  Index finger up	                                      Scroll Up
  Index + Middle finger up	                            Scroll Down
  Thumb + Index close together	                        Volume Control (Pinching distance adjusts volume)
  All fingers up	                                      Cursor Mode (Move mouse using hand)
  Pinch Gesture (Thumb + Index touching)	              Click (Mouse Click & Double Click)
  Exit Gesture (Index, Middle, and Ring up, rest down)	Closes the program

System Volume Control (Using PyCAW)
  Adjusts system volume based on the distance between thumb and index finger.
  Uses Exponential Moving Average (EMA) for smoother volume transitions.
  Exits volume mode when the pinky finger is raised.
Cursor Control & Clicks (Using PyAutoGUI)
  Moves the mouse based on hand movement.
  Uses the middle finger position to move the cursor.
  Detects pinch gestures for clicking.
  Implements a double-click delay to differentiate between single and double clicks.
