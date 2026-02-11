import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


time.sleep(2) 

ret, frame = cap.read()
if ret:
    cv2.imwrite('photo.png', frame)

cap.release()