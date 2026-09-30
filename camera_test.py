import cv2
import time

# Try camera index 0
camera = cv2.VideoCapture(0)

# Wait for webcam startup
time.sleep(3)

if not camera.isOpened():

    print("❌ Camera not opened")

else:

    print("✅ Camera detected")

    success, frame = camera.read()

    if success:

        cv2.imwrite("test_capture.jpg", frame)

        print("✅ Image Captured Successfully")

    else:

        print("❌ Failed to capture image")

camera.release()