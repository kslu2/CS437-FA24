import time
import random
import math
import numpy as np

from Motor import *            
from Ultrasonic import *
from servo import *

ultrasonic=Ultrasonic() 
PWM=Motor()  


def scanning(dest_x, dest_y):
        obj_map = [[0 for _ in range(dest_x)] for _ in range(dest_y)]
        # need a function to find the current location
        cur_x = 0
        cur_y = 0
        last_read = ultrasonic.get_distance()

        for i in range(50,130,5): #range of servo 0 (head moving right)
                
                data1=ultrasonic.get_distance()
                x, y = trig_loc(data1, i - 90)
                if data1 != 0:
                        print ("Obstacle distance is "+ str(x) +"CM x and " + str(y) + "CM y")
                        # need to account for what direction i am facing
                        obj_x, obj_y = obj_distance(cur_x, cur_y, x, y)
                        if (obj_x < dest_x and obj_y < dest_y):
                                obj_map[obj_x][obj_y] = 1
                if data1 < 20 and last_read < 40 and last_read != 0:
                        # recalculate A* keep moving
                pwm.setServoPwm('0',i)
                last_read = ultrasonic.get_distance()
                time.sleep(0.01)
                
        for i in range(130,50,-5): #range of servo 0 (head moving left)
                
                data2=ultrasonic.get_distance()
                x, y = trig_loc(data2, i - 90)
                if data2 != 0:
                        print ("Obstacle distance is "+ str(x) +"CM x and " + str(y) + "CM y")
                        # need to account for what direction i am facing
                        obj_x, obj_y = obj_distance(cur_x, cur_y, x, y)
                        if (obj_x < dest_x and obj_y < dest_y):
                                obj_map[obj_x][obj_y] = 1
                if data2 < 20 and last_read < 40 and last_read != 0:
                        # recalculate A* keep moving    
                pwm.setServoPwm('0',i)
                last_read = ultrasonic.get_distance()
                time.sleep(0.01)


def trig_loc(dist, angle):
        angle_rad = math.radians(angle)
        y = dist * math.sin(angle_rad)
        x = dist * math.cos(angle_rad)
        return x, y


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


def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] + b[1])


if __name__ == '__main__':
        
        pwm=Servo()
        dest_x = 99
        dest_y = 99
        pwm.setServoPwm('1',90)
    
        try:
                while True:
                        scanning(dest_x, dest_y)
                    
            
        except KeyboardInterrupt:
                PWM.setMotorModel(0,0,0,0)
                pwm.setServoPwm('0',90)
                print ("\nEnd of program")
