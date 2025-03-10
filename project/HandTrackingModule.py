import cv2
import mediapipe as mp
import time

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.7, trackCon=0.7):
        """
        Initializes the hand detection module using MediaPipe.
        :param mode: Static mode (False for video input, True for static images)
        :param maxHands: Maximum number of hands to detect
        :param detectionCon: Minimum confidence for detection
        :param trackCon: Minimum confidence for tracking
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # Load MediaPipe Hands module
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        """
        Detects hands in the image and draws landmarks.
        :param img: Input image
        :param draw: Boolean to draw hand landmarks
        :return: Processed image
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert image to RGB
        self.results = self.hands.process(imgRGB)  # Process image for hand detection

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True, color=(255, 0, 255)):
        """
        Finds position of hand landmarks.
        :param img: Input image
        :param handNo: Hand index (0 for first detected hand)
        :param draw: Boolean to draw landmark points
        :param color: Color of landmark points
        :return: List of landmark positions [(id, x, y), ...]
        """
        lmList = []
        imgWidth = img.shape[1]  # Get image width

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)  # Convert to pixel coordinates

                # Mirror x-coordinates for flipped video
                mirrored_x = imgWidth - cx
                lmList.append([id, mirrored_x, cy])

                if draw:
                    cv2.circle(img, (mirrored_x, cy), 5, color, cv2.FILLED)  # Draw landmark point

        return lmList

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # Open webcam
    detector = handDetector()
    while True:
        success, img = cap.read()
        if not success:
            print("⚠️ Camera not available!")
            continue

        img = detector.findHands(img)  # Detect hands
        lmList = detector.findPosition(img, draw=True)  # Get landmark positions

        if lmList:
            pass  # Uncomment below to print index finger tip position
            # print(lmList[8])  # Index finger tip position

        cv2.imshow("Hand Tracking", img)  # Show output
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()