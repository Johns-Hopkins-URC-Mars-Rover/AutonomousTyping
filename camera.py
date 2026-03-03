import cv2

port = 0  # change this

cap = cv2.VideoCapture(port)
if not cap.isOpened():
    print(f"Could not open camera on port {port}")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Camera Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()