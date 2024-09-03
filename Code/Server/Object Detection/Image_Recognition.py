import tensorflow as tf
import numpy as np
import cv2
from picamera2 import Picamera2

model = tf.saved_model.load("ssd_mobilenet_v2_coco_2018_03_29/saved_model")
inference = model.signatures['serving_default']
labels = {13: 'stop sign'}
picam2 = Picamera2()

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
    print(detection_classes)
    return False

try: 
    while True:
        if detect(inference, labels):
            print("\nfound stop sign")
        else:
            print("False")
except KeyboardInterrupt:
    print("\nEnd of program")
