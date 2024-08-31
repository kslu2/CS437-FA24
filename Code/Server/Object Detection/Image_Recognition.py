import tensorflow as tf
import numpy as np
import cv2
from picamera2 import Picamera2

model = tf.saved_model.load("ssd_mobilenet_v2_coco_2018_03_29/saved_model")
labels = {13: 'stop sign'}


def detect(model, labels):
    picam2 = Picamera2()
    picam2.start_and_capture_file("image.jpg")
    image = cv2.imread("image.jpg")
    if image is None:
        return False
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    
    objects = model(input_tensor)
    object_classes = objects['object_classes'][0].numpy().astype(np.int32)
    object_scores = objects['object_scores'][0].numpy()

    for i in range(len(object_classes)):
        if labels[object_classes[i]] == 'stop sign' and object_scores[i] > 0.5:
            return True
    return False


try: 
    while True:
        if detect(model, labels):
            print("\nfound stop sign")
except KeyboardInterrupt:
    print("\nEnd of program")