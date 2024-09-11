import time
import threading
import math
import heapq
import tensorflow as tf
import numpy as np

from picamera2 import Picamera2
from Image_Recognition import detect
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

model = tf.saved_model.load("ssd_mobilenet_v2_coco_2018_03_29/saved_model")
inference = model.signatures['serving_default']
labels = {13: 'stop sign'}
picam2 = Picamera2()


def left_right():
    while running:
        for i in range(50, 110, 1):
            pwm.setServoPwm('0', i)
            cur_angle = i
            time.sleep(0.01)
        for i in range(110, 50, -1):
            pwm.setServoPwm('0', i)
            cur_angle = i
            time.sleep(0.01)
                
    pwm.setServoPwm('0', 90)
    pwm.setServoPwm('1', 90)
    PWM.setMotorModel(0, 0, 0, 0)        


def scanning():
    while running:
        last_read = ultrasonic.get_distance()
        data1 = ultrasonic.get_distance()
        if data1 != 0:
            x, y = trig_loc(data1, cur_angle - 90)
            if detect(model=model, labels=labels) and x < 40:
                # TODO: stop for a second

            print("Obstacle distance is " + str(x) + "CM x and " + str(y) + "CM y")
            obj_x, obj_y = obj_distance(cur_x, cur_y, x, y, facing)
            if obj_x < dest_x and obj_y < dest_y:
                obj_map[obj_x][obj_y] = 1
            
            if data1 < 20 and last_read < 40 and last_read != 0:
                path = astar_search([cur_x, cur_y], obj_map)
            last_read = ultrasonic.get_distance()
            PWM.setMotorModel(650, 650, 650, 650)

    pwm.setServoPwm('0', 90)
    pwm.setServoPwm('1', 90)
    PWM.setMotorModel(0, 0, 0, 0)


def move():
    while path and len(path) > 0:
        next = path[0]
        path = path[1:]
        new_direction = check_rotate(next)
        if new_direction != facing:
            # TODO: rotate if needed, move by 1 unit
        cur_x = next[0]
        cur_y = next[1]
        facing = new_direction


def check_rotate(next):
    diff_x = next[0] - cur_x
    diff_y = next[1] - cur_y
    if cur_y == 1:
        return 0
    elif cur_y == -1:
        return 2
    elif cur_x == 1:
        return 1
    elif cur_x == -1:
        return 3


# 0 = North, 1 = East, 2 = South, 3 = West
def obj_distance(cur_x, cur_y, x, y, facing):
    if facing == 0:
        obj_x = cur_x + x
        obj_y = cur_y + y
    elif facing == 1:
        obj_x = cur_x - y
        obj_y = cur_y + x
    elif facing == 2:
        obj_x = cur_x - x
        obj_y = cur_y - y
    elif facing == 3:
        obj_x = cur_x + y
        obj_y = cur_y - x
    return obj_x, obj_y      


def trig_loc(dist, angle):
    angle_rad = math.radians(angle)
    y = dist * math.sin(angle_rad)
    x = dist * math.cos(angle_rad)
    return x, y


# cur -> [x, y] representing current coordinates
# dst -> [m, n] representing target coordinates
def manhattan(cur, dst):
    return abs(cur[0] - dst[0]) + abs(cur[1] + dst[1])


# start -> [x, y] representing current coordinates
# obj_map -> [m, n] representing map of objects
def astar_search(start, obj_map):
    queue = []
    visited = {}
    m = len(obj_map)
    n = len(obj_map[0])
    goal = [m, n]
    heapq.heappush(queue, (0, start))
    visited.add(start)
    directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    g = {start: 0}
    f = {start: manhattan(start, goal)}
    prev = {}
    while queue:
        cur = heapq.heappop(queue)[1]
        if cur == goal:
            path = []
            while cur in prev:
                path.append(cur)
                cur = prev[cur]
            path.append(start)
            path.reverse()
            return path
        for dir in directions:
            move = [cur[0] + dir[0], cur[1] + dir[1]]
            if obj_map[move[0]][move[1]] == 0 and move in visited:
                prev[move] = cur
                g[move] = g[cur] + 1
                f[move] = g[move] + manhattan(move, goal)
                if move not in [i[1] for i in queue]:
                    heapq.heappush(queue, (f[move], move))
    return None
        

# Main program logic follows:

if __name__ == '__main__':
    t1 = threading.Thread(target=left_right)
    t2 = threading.Thread(target=scanning)
    t3 = threading.Thread(target=move)
        
    t1.daemon = True
    t2.daemon = True
    t3.daemon = True

    dest_x = 99
    dest_y = 99
    obj_map = [[0 for _ in range(dest_x)] for _ in range(dest_y)]
    path = astar_search([cur_x, cur_y], obj_map)

    t1.start()
    t2.start()
    t3.start()
        
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        running = False
                    
    t1.join()
    t2.join()
    t3.join()
         
    pwm.setServoPwm('0', 90)
    pwm.setServoPwm('1', 90)
    PWM.setMotorModel(0, 0, 0, 0)
