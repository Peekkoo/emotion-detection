import cv2
import threading
import time

class CameraThread:
    def __init__(self, camera_index=1):
        self.capture = cv2.VideoCapture(camera_index)
        if not self.capture.isOpened():
            raise IOError("Cannot open webcam")
        self.ret, self.frame = self.capture.read()
        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while self.running:
            self.ret, self.frame = self.capture.read()
            if not self.ret:
                self.running = False
                break

    def read(self):
        return self.frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.capture.release()


if __name__ == '__main__':
    camera_thread = CameraThread()
    try:
        while True:
            frame = camera_thread.read()
            if frame is not None:
                cv2.imwrite('speaker.png', frame)
            time.sleep(1)
    finally:
        camera_thread.stop()
        cv2.destroyAllWindows()