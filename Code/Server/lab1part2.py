import time
import heapq
import os
import tensorflow as tf
import numpy as np
import cv2
import argparse

from picamera2 import Picamera2, Preview
from Motor import *            
from Ultrasonic import *
from servo import *

ultrasonic=Ultrasonic() 
PWM=Motor()  
pwm=Servo()

running = True
obj_map = None
cur_x = 0
cur_y = 0
facing = 0
path = None
cur_angle = 90
dest_x = 150//25
dest_y = 150//25
path_taken = []

model = tf.saved_model.load("ssd_mobilenet_v2_coco_2018_03_29/saved_model")
inference = model.signatures['serving_default']
labels = {13: 'stop sign'}
picam2 = Picamera2()
os.environ["LIBCAMERA_LOG_LEVELS"] = "3"
picam2.set_logging(Picamera2.ERROR)
picam2.start_preview(Preview.NULL)

def detect():
    picam2.start_and_capture_file("image.jpg")
    image = cv2.imread("image.jpg")
    if image is None:
        return False
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    
    objects = inference(input_tensor)
    detection_classes = objects['detection_classes'][0].numpy().astype(np.int32)
    detection_scores = objects['detection_scores'][0].numpy()
    print(f"Detected: {detection_classes}")
    for i in range(len(detection_classes)):
        if detection_classes[i] == 13 and detection_scores[i] > 0.5:
            return True
    return False

def scanning():
    last_read = 100
    count = 0
    while running:
        data1 = ultrasonic.get_distance()
        # Make sure the read is valid
        if data1 != 0:
            obj_x, obj_y = obj_distance(cur_x, cur_y, 0, data1//25, facing)
            # if the object is within our range and it is not a stop sign, mark on the map
            if obj_x < dest_x and obj_y < dest_y and obj_x >= 0 and obj_y >= 0 and not detect():
                obj_map[obj_x][obj_y] = 1
                # Recalculate shortest path
                new_path = astar_search([cur_x, cur_y], obj_map)
                path.clear()
                path.extend(new_path)
            last_read = data1
        
        # Error handling for if we arrive at the destination
        if (len(path) == 0):
            running = False
            print(path_taken)
            print(obj_map)
        count += 1

        # Only run moving code every so often to give scanning more time
        if count >= 3:
            if detect() and data1 < 20:
                print("Found Stop Sign")
                time.sleep(5)
            count = 0
            step = path[0]
            # Check if we need to rotate left or right (lorr) and which direction
            new_direction, lorr = check_rotate(step, cur_x, cur_y, facing)
            if new_direction == -1:
                continue
            path_taken.append(step)
            path = path[1:]
            # Move in direction
            move(step, new_direction, lorr)
            if cur_x == dest_x and cur_y == dest_y:
                running = False
    pwm.setServoPwm('0', 90)
    pwm.setServoPwm('1', 90)
    PWM.setMotorModel(0, 0, 0, 0)


def move(step, new_direction, lorr):
    # Turn if needed
    if new_direction != facing:
        if lorr == 1:
            turn_right()
        elif lorr == 0:
            turn_left()
    # Move 25 cm
    PWM.setMotorModel(700,700,700,700)
    time.sleep(1.5)   
    PWM.setMotorModel(0,0,0,0)
    cur_x = step[0]
    cur_y = step[1]
    print("Current Location Updated to " + str(cur_x) + " " + str(cur_y))
    facing = new_direction


def turn_right():
    # In-place right turn
    PWM.setMotorModel(2000, 2000, -2000, -2000)
    time.sleep(0.9)
    PWM.setMotorModel(0,0,0,0)

def turn_left():
    # In-place left turn
    PWM.setMotorModel(-2000, -2000, 2000, 2000)
    time.sleep(0.9)
    PWM.setMotorModel(0,0,0,0)


# returns new direction, 0 for left turn, 1 for right turn
def check_rotate(next, x, y, face):
    diff_x = next[0] - x
    diff_y = next[1] - y
    if diff_y == 1:
        if face == 1:
            return 0, 0
        elif face == 3: 
            return 0, 1
        elif face == 0:
            return 0, -1
    elif diff_y == -1:
        if face == 1:
            return 2, 1
        elif face == 3: 
            return 2, 0
        elif face == 2:
            return 2, -1
    elif diff_x == 1:
        if face == 0:
            return 1, 1
        elif face == 2: 
            return 1, 0
        elif face == 1:
            return 1, -1
    elif diff_x == -1:
        if face == 0:
            return 3, 0
        elif face == 2: 
            return 3, 1
        elif face == 3:
            return 3, -1
    return -1, -1


# 0 = North, 1 = East, 2 = South, 3 = West
# Calculates where the object is w.r.t where we are facing
def obj_distance(cur_x, cur_y, x, y, facing):
    if facing == 0:
        obj_x = cur_x + x
        obj_y = cur_y + y
    elif facing == 1:
        obj_x = cur_x + y
        obj_y = cur_y - x
    elif facing == 2:
        obj_x = cur_x - x
        obj_y = cur_y - y
    elif facing == 3:
        obj_x = cur_x - y
        obj_y = cur_y + x
    return int(obj_x), int(obj_y)    


# cur -> [x, y] representing current coordinates
# dst -> [m, n] representing target coordinates
def manhattan(cur, dst):
    return abs(cur[0] - dst[0]) + abs(cur[1] + dst[1])


# start -> [x, y] representing current coordinates
# obj_map -> [m, n] representing map of objects
def astar_search(start, obj_map):
    queue = []
    visited = set()
    m = len(obj_map)
    n = len(obj_map[0])
    goal = [m - 1, n - 1]
    heapq.heappush(queue, (0, start))
    visited.add(tuple(start))
    g = {tuple(start): 0}
    f = {tuple(start): manhattan(start, goal)}
    directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    prev = dict()
    while queue:
        cur = heapq.heappop(queue)[1]
        if cur == goal:
            # Generate path
            path = []
            while tuple(cur) in prev.keys():
                path.append(cur)
                cur = prev[tuple(cur)]
            path.reverse()
            return path
        
        # Search in all directions until we arrive at goal
        for dir in directions:
            move = [cur[0] + dir[0], cur[1] + dir[1]]
            if (0 <= move[0] < m) and (0 <= move[1] < n) and obj_map[move[0]][move[1]] == 0:
                if tuple(move) not in visited:
                    visited.add(tuple(move))
                    prev[tuple(move)] = tuple(cur)
                    g[tuple(move)] = g[tuple(cur)] + 1
                    f[tuple(move)] = g[tuple(move)] + manhattan(move, goal)
                    heapq.heappush(queue, (f[tuple(move)], move))
    return None
        

# Main program logic follows:

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--destination", type=str, default="4,5")
    args = argparser.parse_args()
    if args.destination:
        dest_x, dest_y = map(int, args.destination.split(","))
    
    print(f"Started Running to {dest_x}, {dest_y}")

    obj_map = [[0 for _ in range(dest_y)] for _ in range(dest_x)]
    path = astar_search([cur_x, cur_y], obj_map)
    scanning()
        
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        running = False  
         
    pwm.setServoPwm('0', 90)
    pwm.setServoPwm('1', 90)
    PWM.setMotorModel(0, 0, 0, 0)