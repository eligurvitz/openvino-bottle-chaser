
import cv2
import sys
import time
import pigpio
import settings
import imutils
from imutils.object_detection import non_max_suppression
import numpy as np
from lircclass import LIRC

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]

GPIO = 2
MIN_WIDTH = 700
MAX_WIDTH = 2000
STEP = 100
MIN_CONFIDENCE = 0.7
BOTTLE_IDX = 5

class Scan:
    def __init__(self, piconn):
        self.camera = cv2.VideoCapture(0)
        self.pi = piconn
        self.lirc = LIRC()
        print('loading networks')
        self.facenet = cv2.dnn.readNet('face-detection-adas-0001.xml', 'face-detection-adas-0001.bin')
        self.facenet.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
        self.mbnet = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt', 'MobileNetSSD_deploy.caffemodel')
        self.mbnet.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
        print('finished loading networks')
        self.image = None
        self.width = MIN_WIDTH
        self.mode = 'face'
        return

    def __del__(self):
        del self.camera

    def scan(self):
        step = STEP

        while True:
            self.pi.set_servo_pulsewidth(GPIO, self.width)
            time.sleep(0.1)
            self.take_photo()
            if self.mode == 'face':
                found, x = self.detect_face()
            else:
                found, x = self.detect_bottle()

            if found:
                self.pi.set_servo_pulsewidth(GPIO, settings.CENTER_WIDTH)
                width = self.width
                self.width = settings.CENTER_WIDTH
                return True, self.mode, width, x

            self.width += step
            if self.width < MIN_WIDTH or self.width > MAX_WIDTH:
                step = -step
                self.width += step

            if self.lirc.key_pressed() == True:
                if self.mode == 'face':
                    self.mode= 'bottle'
                    print ('searching for bottle')
                else:
                    print('searching for face')
                    self.mode = 'face'

    def take_photo(self):
        return_value, self.image = self.camera.read()
        for i in range(4):
            self.camera.grab()

    def detect_face(self):
        blob = cv2.dnn.blobFromImage(self.image, size=(672, 384), ddepth=cv2.CV_8U)
        self.facenet.setInput(blob)
        out = self.facenet.forward()

        for detection in out.reshape(-1, 7):
            confidence = float(detection[2])
            if confidence > 0.5:
                xmin = int(detection[3] * self.image.shape[1])
                ymin = int(detection[4] * self.image.shape[0])
                xmax = int(detection[5] * self.image.shape[1])
                ymax = int(detection[6] * self.image.shape[0])
                x = int(xmin + ((xmax - xmin) / 2))
                print ('detected a face at xmin: {}  ymin: {} xmax: {} ymax: {}  x: {}'.format(xmin, ymin, xmax, ymax, x))
                return True, x

        return False, 0

    def detect_bottle(self):
        frame = imutils.resize(self.image, width=400)
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        self.mbnet.setInput(blob)
        detections = self.mbnet.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > MIN_CONFIDENCE:
                idx = int(detections[0, 0, i, 1])
                if idx != BOTTLE_IDX:
                    return False, 0

                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (xmin, ymin, xmax, ymax) = box.astype("int")
                x = int(xmin + ((xmax - xmin) / 2))
                print ('detected a bottle at xmin: {}  ymin: {} xmax: {} ymax: {}  x: {}'.format(xmin, ymin, xmax, ymax, x))
                return True, x

        return False, 0
