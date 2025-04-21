import cv2

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("❌ Webcam not detected or in use by another application.")
else:
    print("✅ Webcam detected.")
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Webcam Test", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("❌ Couldn't read frame from webcam.")

cap.release()