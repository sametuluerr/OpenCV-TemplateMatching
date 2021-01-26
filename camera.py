import cv2
import numpy as np

font = cv2.FONT_HERSHEY_SIMPLEX
template = None
w = 0
h = 0


class VideoCamera:
    def __init__(self, img):
        self.img = img
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def template_config(self):
        global w
        global h
        global template
        template = cv2.imread(self.img, cv2.IMREAD_GRAYSCALE)
        w, h = template.shape[::-1]

    def get_frame(self):
        success, frame = self.video.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)

        threshold = 0.6

        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            cv2.rectangle(frame, pt, (pt[0] + w, pt[1] + h), (124, 252, 0), 1)
            cv2.putText(frame, "%" + str(threshold*100).split('.')[0],
                        (pt[0] + w, pt[1] + h), font, 1, (124, 252, 0), 1)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
