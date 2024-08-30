import time
import random
import math
import numpy as np

from Motor import *            
from Ultrasonic import *
from servo import *

ultrasonic=Ultrasonic() 
PWM=Motor()  


def scanning():
        last_read = ultrasonic.get_distance()

        for i in range(50,130,5): #range of servo 0 (head moving right)
                
                data1=ultrasonic.get_distance()
                x, y = trig_loc(data1, i - 90)
                if(data1 != 0):
                        print ("Obstacle distance is "+ str(x) +"CM x and " + str(y) + "CM y")
                if(data1 < 20 and last_read < 40 and last_read != 0):
                        move_over()
                PWM.setMotorModel(650,650,650,650) 
                pwm.setServoPwm('0',i)
                last_read = ultrasonic.get_distance()
                time.sleep(0.01)
                
        for i in range(130,50,-5): #range of servo 0 (head moving left)
                
                data2=ultrasonic.get_distance()
                x, y = trig_loc(data2, i - 90)
                if(data2 != 0):
                        print ("Obstacle distance is "+ str(x) +"CM x and " + str(y) + "CM y")
                if(data2 < 20 and last_read < 40 and last_read != 0):
                        move_over()
                PWM.setMotorModel(650,650,650,650)         
                pwm.setServoPwm('0',i)
                last_read = ultrasonic.get_distance()
                time.sleep(0.01)
             
def move_over():
        PWM.setMotorModel(0,0,0,0)
        
        flip = random.randint(0,1)
                    
        if(flip == 0):
                PWM.setMotorModel(-650,-650,-650,-650)     #Back
                print ("The car is going backwards")
                time.sleep(1)
                PWM.setMotorModel(2000,2000,-2000,-2000)       #Turn right 
                print ("The car is turning right")
                time.sleep(1)
                PWM.setMotorModel(0,0,0,0)
        else:
                PWM.setMotorModel(-650,-650,-650,-650)     #Back
                print ("The car is going backwards")
                time.sleep(1)
                PWM.setMotorModel(-2000,-2000,2000,2000)       #Turn left
                print ("The car is turning left")
                time.sleep(1)  
                PWM.setMotorModel(0,0,0,0)

def trig_loc(dist, angle):
        angle_rad = math.radians(angle)
        y = dist * math.sin(angle_rad)
        x = dist * math.cos(angle_rad)
        return x, y
        

# Main program logic follows:

if __name__ == '__main__':
        
    pwm=Servo()

    print ('Program is starting ... ')
    pwm.setServoPwm('1',90)
    
    try:
        while True:
            scanning()
                    
            
    except KeyboardInterrupt:
        PWM.setMotorModel(0,0,0,0)
        pwm.setServoPwm('0',90)
        print ("\nEnd of program")
