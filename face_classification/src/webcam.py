import cv2

if __name__ == "__main__":
    vcam = cv2.VideoCapture(0)
    sucess, frame = vcam.read
    cv2.imwrite('speaker.png', frame)
    vcam.release