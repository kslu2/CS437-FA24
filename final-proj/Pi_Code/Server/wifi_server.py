import socket
import subprocess
import time
import tensorflow as tf
import numpy as np
import cv2
from picamera2 import Picamera2, Preview
from PIL import Image, ImageFile
import imageio
import requests
from Motor import *
from Ultrasonic import *
from servo import *

import numpy as np

# Initialize components
ultrasonic = Ultrasonic()
PWM = Motor()
picam2 = Picamera2()

HOST = "192.168.0.104"  # Replace with your Pi's IP
PORT = 65432            # Port for communication
direction = "Stopped"
ultrasonicData = 0
cpu_temperature = 32

# Load model
model = tf.saved_model.load("ssd_mobilenet_v2_coco_2018_03_29/saved_model")
inference = model.signatures['serving_default']

# Define labels
labels = {1: 'person'}

# Initialize Picamera2
picam2 = Picamera2()
picam2.start_preview(Preview.NULL)
picam2.start()

# Function to capture frames and create a GIF
def capture_and_create_gif():
    gif_path = "/home/pi/intruder.gif"
    frames = []

    # Configure camera settings
    camera_config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(camera_config)
    picam2.start()

    # Capture frames for 1 seconds
    start_time = time.time()
    while time.time() - start_time < 1:
        frame = Image.fromarray(picam2.capture_array())  # Capture frame
        if frame.mode != "RGB":  # Ensure consistent mode
            frame = frame.convert("RGB")
        frames.append(np.array(frame))  # Convert to NumPy array

    picam2.stop()

    # Debugging: Verify frames list
    print(f"Number of frames captured: {len(frames)}")
    for idx, frame in enumerate(frames):
        print(f"Frame {idx}: Shape={frame.shape}, Dtype={frame.dtype}")

    # Save frames as a GIF
    if frames:  # Ensure frames were captured
        imageio.mimsave(gif_path, frames, format="GIF", duration=0.2)
    else:
        raise RuntimeError("No frames captured for GIF creation.")

    return gif_path


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


# Function to send GIF to the Electron app
def send_gif_to_server(gif_path):
    url = "http://192.168.0.102:3000/upload"  # Replace with your Electron app's server IP and port
    files = {'file': open(gif_path, 'rb')}
    data = {'alert': 'intruder_detected'}
    
    try:
        response = requests.post(url, files=files, data=data)
        print("Sent GIF to server, response:", response.status_code)
    except Exception as e:
        print("Failed to send GIF:", e)

# Socket communication for car control and intruder detection
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    try:
        while True:
            client, clientInfo = s.accept()
            data = client.recv(1024)  # Receive data
            if data != b"":
                if data == b'forward\r\n':
                    PWM.setMotorModel(700, 700, 700, 700)
                    print("forward")
                    direction = "Forward"
                elif data == b'reverse\r\n':
                    if direction == "Forward":
                        PWM.setMotorModel(0, 0, 0, 0)
                        direction = "Stopped"
                        print("Stopped")
                    else:
                        PWM.setMotorModel(-700, -700, -700, -700)
                        direction = "Reverse"
                        print("Reverse")
                elif data == b'left\r\n':
                    direction = "Turning Left"
                    PWM.setMotorModel(-2000, -2000, 2000, 2000)
                    print("Left")
                elif data == b'right\r\n':
                    PWM.setMotorModel(2000, 2000, -2000, -2000)
                    print("Right")
                    direction = "Turning Right"
                elif data == b'cameraCheck\r\n' or detect():
                    print("Intruder detected!")
                    gif_path = capture_and_create_gif()
                    send_gif_to_server(gif_path)
                elif data == b'update\r\n':
                    raw_cpu_temperature = subprocess.getoutput("cat /sys/class/thermal/thermal_zone0/temp")
                    cpu_temperature = str(round(float(raw_cpu_temperature) / 1000, 2))
                    ultrasonicData = str(ultrasonic.get_distance())
                    
                    dataToSend = f"{direction}-{ultrasonicData}-{cpu_temperature}"
                    client.sendall(dataToSend.encode())
                elif data == b'detect\r\n':
                    print("Intruder detected!")
                    gif_path = capture_and_create_gif()
                    send_gif_to_server(gif_path)
    except Exception as e:
        print(e)
    finally:
        pass

