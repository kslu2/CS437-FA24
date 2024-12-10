import time
import random
import threading
import numpy as np

from Motor import *            
from Ultrasonic import *
from servo import *

ultrasonic=Ultrasonic() 
PWM=Motor()  
pwm=Servo()

running = True

def left_right():
        while running:
            for i in range(50,110,1):
                pwm.setServoPwm('0',i)
                time.sleep(0.01)
            for i in range(110,50,-1):
                pwm.setServoPwm('0',i)
                time.sleep(0.01)
                
        pwm.setServoPwm('0',90)
        pwm.setServoPwm('1',90)
        PWM.setMotorModel(0,0,0,0) 
        
def up_down():
    
        while running:
            for i in range(80,150,1):
                pwm.setServoPwm('1',i)
                time.sleep(0.01)
            for i in range(150,80,-1):
                pwm.setServoPwm('1',i)
                time.sleep(0.01)   
                
        pwm.setServoPwm('0',90)
        pwm.setServoPwm('1',90)
        PWM.setMotorModel(0,0,0,0) 
        
        

def scanning():
  
                while running:
                        last_read = ultrasonic.get_distance()
                        data1=ultrasonic.get_distance()
                        if(data1 != 0):
                                print ("Obstacle distance is "+str(data1)+"CM")
                        if(data1 < 20 and last_read < 40 and last_read != 0):
                                move_over()
                        last_read = ultrasonic.get_distance()
                        PWM.setMotorModel(650,650,650,650) 
                        
                pwm.setServoPwm('0',90)
                pwm.setServoPwm('1',90)
                PWM.setMotorModel(0,0,0,0)       
             
def move_over():
        if running == True:
                PWM.setMotorModel(0,0,0,0)
                
                flip = random.randint(0,1)
                            
                if(flip == 0):
                        PWM.setMotorModel(-1000,-1000,-1000,-1000)     #Back
                        print ("The car is going backwards")
                        time.sleep(1)
                        #PWM.setMotorModel(2000,2000,-500,-500)       #Turn right
                        PWM.setMotorModel(4095,4095,-4095,-4095) 
                        print ("The car is turning right")
                        time.sleep(0.5)
                        PWM.setMotorModel(0,0,0,0)
                else:
                        PWM.setMotorModel(-1000,-1000,-1000,-1000)     #Back
                        print ("The car is going backwards")
                        time.sleep(1)
                        #PWM.setMotorModel(-500,-500,2000,2000)       #Turn left
                        PWM.setMotorModel(-4095,-4095,4095,4095)
                        print ("The car is turning left")
                        time.sleep(0.5)  
                        PWM.setMotorModel(0,0,0,0) 
        else:
                pwm.setServoPwm('0',90)
                pwm.setServoPwm('1',90)
                PWM.setMotorModel(0,0,0,0)
        

# Main program logic follows:

if __name__ == '__main__':
        t1 = threading.Thread(target=left_right)
        t2 = threading.Thread(target=up_down)
        t3 = threading.Thread(target=scanning)
        
        t1.daemon = True
        t2.daemon = True
        t3.daemon = True
        
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
        
        
        
        pwm.setServoPwm('0',90)
        pwm.setServoPwm('1',90)
        PWM.setMotorModel(0,0,0,0)