import tensorflow as tf
import numpy as np
import cv2
import os
from picamera2 import Picamera2, Preview

model = tf.saved_model.load("ssd_mobilenet_v2_coco_2018_03_29/saved_model")
inference = model.signatures['serving_default']
labels = {13: 'stop sign'}
picam2 = Picamera2()
os.environ["LIBCAMERA_LOG_LEVELS"] = "3"
Picamera2.set_logging(Picamera2.ERROR)
picam2.start_preview(Preview.NULL)

def detect(model, labels):
    picam2.start_and_capture_file("image.jpg")
    image = cv2.imread("image.jpg")
    if image is None:
        return False
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    
    objects = model(input_tensor)
    detection_classes = objects['detection_classes'][0].numpy().astype(np.int32)
    detection_scores = objects['detection_scores'][0].numpy()

    for i in range(len(detection_classes)):
        if detection_classes[i] == 13 and detection_scores[i] > 0.5:
            return True
    return False
