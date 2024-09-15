import time
import threading
import math
import heapq
import tensorflow as tf
import numpy as np

#from picamera2 import Picamera2, Preview
#from Image_Recognition import detect
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
dest_x = 100//20
dest_y = 200//20

#model = tf.saved_model.load("ssd_mobilenet_v2_coco_2018_03_29/saved_model")
#inference = model.signatures['serving_default']
#labels = {13: 'stop sign'}

def left_right():
    global running, cur_angle
    while running:
        for i in range(50, 130, 1):
            pwm.setServoPwm('0', i)
            cur_angle = i
            time.sleep(0.01)
        for i in range(130, 50, -1):
            pwm.setServoPwm('0', i)
            cur_angle = i
            time.sleep(0.01)
                
    pwm.setServoPwm('0', 90)
    pwm.setServoPwm('1', 90)
    PWM.setMotorModel(0, 0, 0, 0)        


def scanning():
    global cur_x, cur_y, obj_map, path, running, dest_x, dest_y, facing
    while running:
        last_read = ultrasonic.get_distance()
        data1 = ultrasonic.get_distance()
        print(data1)
        if data1 != 0:
            x, y = trig_loc(data1, cur_angle - 90)
            #if detect(model=model, labels=labels) and x < 40:
                # TODO: stop for a second
            #       pass
            obj_x, obj_y = obj_distance(cur_x, cur_y, x, y, facing)
            print("Obstacle distance is " + str(obj_x) + "CM x and " + str(obj_y) + "CM y")
            print(str(dest_x) + " " + str(dest_y))
            if obj_x < dest_x and obj_y < dest_y and obj_x >= 0 and obj_y >= 0:
                obj_map[obj_x][obj_y] = 1
            if data1 < 40 and last_read < 65 and last_read != 0:
                new_path = astar_search([cur_x, cur_y], obj_map)
                path.clear()
                path.extend(new_path)
            last_read = ultrasonic.get_distance()
        step = path[0]
        new_direction, lorr = check_rotate(step, cur_x, cur_y, facing)
        if new_direction == -1:
            continue
        path = path[1:]
        move(step, new_direction, lorr)
        if cur_x == dest_x and cur_y == dest_y:
            running = False
    pwm.setServoPwm('0', 90)
    pwm.setServoPwm('1', 90)
    PWM.setMotorModel(0, 0, 0, 0)


def move(step, new_direction, lorr):
    global cur_x, cur_y, facing
    #print("Moving to " + str(next[0]) + " " + str(next[1]))
    #print("From " + str(cur_x) + " " + str(cur_y))
    if new_direction != facing:
        if lorr == 1:
            turn_right()
            #print("Turning Right")
        elif lorr == 0:
            turn_left()
            #print("Turning Left")
    PWM.setMotorModel(700,700,700,700)
    time.sleep(1.1)   
    PWM.setMotorModel(0,0,0,0)
    cur_x = step[0]
    cur_y = step[1]
    print("Current Location Updated to " + str(cur_x) + " " + str(cur_y))
    time.sleep(1.5)
    facing = new_direction


def turn_right():
    n = 51
    PWM.setMotorModel(0,0,0,0)
    time.sleep(1)
    for i in range(0,n,1):
        PWM.setMotorModel(2000,2000,-2000,-2000)
        time.sleep(0.01)
    PWM.setMotorModel(0,0,0,0)

def turn_left():
    n = 51
    for i in range(0,n,1):
        PWM.setMotorModel(-2000,-2000,2000,2000) 
        time.sleep(0.01)
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


def trig_loc(dist, angle):
    angle_rad = math.radians(angle)
    y = dist * math.cos(angle_rad)/20
    x = dist * math.sin(angle_rad)/20
    return int(x), int(y)


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
    directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    g = {tuple(start): 0}
    f = {tuple(start): manhattan(start, goal)}
    prev = dict()
    while queue:
        cur = heapq.heappop(queue)[1]
        if cur == goal:
            path = []
            while tuple(cur) in prev.keys():
                path.append(cur)
                cur = prev[tuple(cur)]
            path.reverse()
            return path
        
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
    t1 = threading.Thread(target=left_right)
    t2 = threading.Thread(target=scanning)
        
    t1.daemon = True
    t2.daemon = True

    obj_map = [[0 for _ in range(dest_y)] for _ in range(dest_x)]
    path = astar_search([cur_x, cur_y], obj_map)
    print("Started Running")
    t1.start()
    t2.start()
        
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        running = False
        #picam2.stop()
    #picam2.stop()    
    t1.join()
    t2.join()
         
    pwm.setServoPwm('0', 90)
    pwm.setServoPwm('1', 90)
    PWM.setMotorModel(0, 0, 0, 0)