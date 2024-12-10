import time
import random

from Motor import *            
from Ultrasonic import *
from servo import *

ultrasonic=Ultrasonic() 
PWM=Motor()  

def scanning():
        for i in range(50,110,1): #range of servo 0 (head moving right)
                
                data1=ultrasonic.get_distance()
                print ("Obstacle distance is "+str(data1)+"CM")
                if(data1 < 30):
                        move_over()
                PWM.setMotorModel(650,650,650,650) 
                pwm.setServoPwm('0',i)
                time.sleep(0.01)
                
        for i in range(110,50,-1): #range of servo 0 (head moving left)
                
                data2=ultrasonic.get_distance()
                print ("Obstacle distance is "+str(data2)+"CM")
                if(data2 < 30):
                        move_over()
                PWM.setMotorModel(650,650,650,650)         
                pwm.setServoPwm('0',i)
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
        

# Main program logic follows:

if __name__ == '__main__':
        
    pwm=Servo()

    print ('Program is starting ... ')
    pwm.setServoPwm('1',70)
    
    try:
        while True:
            scanning()
                    
            
    except KeyboardInterrupt:
        PWM.setMotorModel(0,0,0,0)
        pwm.setServoPwm('0',90)
        print ("\nEnd of program")
  
 
        
        
