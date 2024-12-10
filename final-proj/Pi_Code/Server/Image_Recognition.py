import tensorflow as tf
import numpy as np
import cv2
import os
from picamera2 import Picamera2, Preview

# Load model
model = tf.saved_model.load("ssd_mobilenet_v2_coco_2018_03_29/saved_model")
inference = model.signatures['serving_default']

# Define labels
labels = {1: 'person'}

# Initialize Picamera2
picam2 = Picamera2()
picam2.start_preview(Preview.NULL)
picam2.start()

# Function to detect objects
def detect():
    picam2.capture_file("image.jpg")
    image = cv2.imread("image.jpg")

    #image = picam2.capture_array()
    if image is None:
        return False

    # Convert RGBA to RGB by removing the alpha channel (4th channel)
    if image.shape[-1] == 4:
        image = image[..., :3]
    
    # Convert to tensor and add batch dimension
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]

    # Perform inference
    objects = inference(input_tensor)
    
    # Get detection results
    detection_classes = objects['detection_classes'][0].numpy().astype(np.int32)
    detection_scores = objects['detection_scores'][0].numpy()
    
    # Loop through detections and check for high-confidence 'person' detections
    for i in range(len(detection_classes)):
        if detection_classes[i] == 1 and detection_scores[i] > 0.5:
            return True

    return False
