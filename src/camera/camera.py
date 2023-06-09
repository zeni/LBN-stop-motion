from threading import Thread
import cv2
from errors import errors


class Camera:
    def __init__(self, src=0, w=1920, h=1080):
        self.width = w
        self.height = h
        self.exposure = -2
        self.auto_exp = False
        self.stopped = False
        self.source = src
        self.error = False

    def start_stream(self, src):
        self.source = src
        try:
            self.stream = cv2.VideoCapture(self.source)
            if not self.stream.isOpened():
                raise errors.VideoCaptureError()
        except errors.VideoCaptureError:
            pass
        else:
            self.stream.setExceptionMode(True)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            self.stream.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
            (self.grabbed, self.frame) = self.stream.read()
            self.new = self.grabbed

    def start(self):
        Thread(target=self._update, args=()).start()
        return self

    def _update(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                self.error = False
                try:
                    self.frame_prev = self.frame.copy()
                    try:
                        (self.grabbed, self.frame) = self.stream.read()
                    except:
                        self.error = True
                        self.stopped = True
                    self.new = self.grabbed
                    if not self.grabbed:
                        self.stopped = True
                except:
                    self.error = True

    def read(self):
        return self.frame, self.error

    def stop(self):
        self.stopped = True

    def set_exposure(self, e):
        self.auto_exp = False
        self.exposure = int(e)
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self.stream.set(cv2.CAP_PROP_EXPOSURE, self.exposure)

    def exposure_auto(self):
        if self.auto_exp:
            self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        else:
            self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            self.stream.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
