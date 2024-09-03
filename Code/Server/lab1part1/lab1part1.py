import time
import random

from Motor import *            
PWM=Motor()          
def test_Motor(): 
    try:
        PWM.setMotorModel(1000,1000,1000,1000)         #Forward
        print ("The car is moving forward")
        time.sleep(1)
        PWM.setMotorModel(-1000,-1000,-1000,-1000)     #Back
        print ("The car is going backwards")
        time.sleep(1)
        PWM.setMotorModel(-1500,-1500,2000,2000)       #Turn left
        print ("The car is turning left")
        time.sleep(1)
        PWM.setMotorModel(2000,2000,-1500,-1500)       #Turn right 
        print ("The car is turning right")  
        time.sleep(1)
        PWM.setMotorModel(-2000,2000,2000,-2000)       #Move left 
        print ("The car is moving left")  
        time.sleep(1)
        PWM.setMotorModel(2000,-2000,-2000,2000)       #Move right 
        print ("The car is moving right")  
        time.sleep(1)    
            
        PWM.setMotorModel(0,2000,2000,0)         #Move diagonally to the left and forward
        print ("The car is moving diagonally to the left and forward")  
        time.sleep(1)
        PWM.setMotorModel(0,-2000,-2000,0)       #Move diagonally to the right and backward
        print ("The car is moving diagonally to the right and backward")  
        time.sleep(1) 
        PWM.setMotorModel(2000,0,0,2000)         #Move diagonally to the right and forward
        print ("The car is moving diagonally to the right and forward")  
        time.sleep(1)
        PWM.setMotorModel(-2000,0,0,-2000)       #Move diagonally to the left and backward
        print ("The car is moving diagonally to the left and backward")  
        time.sleep(1) 
        
        PWM.setMotorModel(0,0,0,0)               #Stop
        print ("\nEnd of program")
    except KeyboardInterrupt:
        PWM.setMotorModel(0,0,0,0)
        print ("\nEnd of program")


from Ultrasonic import *
ultrasonic=Ultrasonic()                
def test_Ultrasonic():
    try:
        while True:
            data=ultrasonic.get_distance()   #Get the value
            print ("Obstacle distance is "+str(data)+"CM")
            time.sleep(1)
    except KeyboardInterrupt:
        print ("\nEnd of program")

def car_Rotate():
    try:
        while True:
          PWM.Rotate(0)
    except KeyboardInterrupt:
        print ("\nEnd of program")
        
        
        
from servo import *
pwm=Servo()


def scanning():
        for i in range(50,110,1):
                
                data2=ultrasonic.get_distance()
                print ("Obstacle distance is "+str(data2)+"CM")
                if(data2 < 30):
                        move_over()
                        
                pwm.setServoPwm('0',i)
                time.sleep(0.01)
        for i in range(110,50,-1):
                
                data2=ultrasonic.get_distance()
                print ("Obstacle distance is "+str(data2)+"CM")
                if(data2 < 30):
                        move_over()
                        
                pwm.setServoPwm('0',i)
                time.sleep(0.01)
             
def move_over():
        PWM.setMotorModel(0,0,0,0)
        
        flip = random.randint(0,1)
                    
        if(flip == 0):
                PWM.setMotorModel(-750,-750,-750,-750)     #Back
                print ("The car is going backwards")
                time.sleep(1)
                PWM.setMotorModel(2000,2000,-2000,-2000)       #Turn right 
                print ("The car is turning right")
                time.sleep(2)
                PWM.setMotorModel(0,0,0,0)
        else:
                PWM.setMotorModel(-750,-750,-750,-750)     #Back
                print ("The car is going backwards")
                time.sleep(1)
                PWM.setMotorModel(-2000,-2000,2000,2000)       #Turn left
                print ("The car is turning left")
                time.sleep(2)  
                PWM.setMotorModel(0,0,0,0) 
        

# Main program logic follows:

data2 = 1

if __name__ == '__main__':
        
    #pwm=Servo()

    print ('Program is starting ... ')
    
    try:
        while True:
            data2=ultrasonic.get_distance()   #Get the value
            scanning()
            print ("Obstacle distance is "+str(data2)+"CM")
            if(data2 > 30):
                    PWM.setMotorModel(650,650,650,650)         #Forward
            else:
                move_over()     
                    
            
    except KeyboardInterrupt:
        PWM.setMotorModel(0,0,0,0)
        pwm.setServoPwm('0',90)
        print ("\nEnd of program")
  
 
        
        
