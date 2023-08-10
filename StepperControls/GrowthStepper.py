from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *
from Phidget22.Devices.DigitalInput import *
import time

def get_parameters(f):
    try:
        f.seek(0) #resets pointer to top of the file
        lines = f.readlines()
        return (lines[0].split()[1],#MaxSpeed
                lines[1].split()[1])#SomethingElse
    except:
        print('Error Reading Parameters: Edit parameters.txt or redownload it from https://github.com/wendl198/ContactlessProbe.')
        time.sleep(1)
        return get_parameters(f) #this will recursively tunnel deeper until the problem is fixed. It will not record data
    #May be smart to install a better fail safe, but this is probably good enough for most users.


StepsPerRev = 360/1.8*(204687/2057)*16 #200steps/rev*gear ratio*16microsteps
timeout = 10000

parameter_path = 'C:\\Users\\Contactless\\Desktop\\Stepper\\StepperParameters.txt'
parameter_file = open(parameter_path, 'r')
        
#Declare any event handlers here. These will be called every time the associated event occurs.

def onDigitalInput1_StateChange(self, state):
    #print("State [1]: " + str(state))
    pass

def onDigitalInput2_StateChange(self, state):
    #print("State [2]: " + str(state))
    if not(state):
        stepper0.setEngaged(False)
        stepper0.addPositionOffset(-stepper0.getPosition())
    elif not(digitalInput3.getState()):
        stepper0.setTargetPosition(3000000)
        stepper0.setEngaged(True)
            
        

def onDigitalInput3_StateChange(self, state):
    #print("State [3]: " + str(state))
    if not(state):
        stepper0.setEngaged(False)
        stepper0.addPositionOffset(-stepper0.getPosition())
    elif not(digitalInput2.getState()):
        stepper0.setTargetPosition(-3000000)
        stepper0.setEngaged(True)


    #Create your Phidget channels
stepper0 = Stepper()
digitalInput1 = DigitalInput()
digitalInput2 = DigitalInput()
digitalInput3 = DigitalInput()

    #Set addressing parameters to specify which channel to open (if any)
digitalInput1.setChannel(1)
digitalInput2.setChannel(2)
digitalInput3.setChannel(3)
    #Assign any event handlers you need before calling open so that no events are missed.
digitalInput1.setOnStateChangeHandler(onDigitalInput1_StateChange)
digitalInput2.setOnStateChangeHandler(onDigitalInput2_StateChange)
digitalInput3.setOnStateChangeHandler(onDigitalInput3_StateChange)

    #Open your Phidgets and wait for attachment
stepper0.openWaitForAttachment(5000)
digitalInput1.openWaitForAttachment(5000)
digitalInput2.openWaitForAttachment(5000)
digitalInput3.openWaitForAttachment(5000)

    #Do stuff with your Phidgets here or in your event handlers.
    # stepper0.setTargetPosition(int(StepsPerRev))
    # stepper0.setEngaged(True)
    # while stepper0.getTargetPosition() != stepper0.getPosition():
    #     speed,_ = get_parameters(parameter_file)
    #     stepper0.setVelocityLimit(int(speed))
    #     #get_parameters
    # time.sleep(3)
    # stepper0.addPositionOffset(int(StepsPerRev))
    # stepper0.setTargetPosition(0) #this zeros the position
    # while stepper0.getTargetPosition() != stepper0.getPosition():
    #     speed,_ = get_parameters(parameter_file)
    #     stepper0.setVelocityLimit(int(speed))

    
while not(digitalInput2.getState() and digitalInput3.getState()):
    speed,_ = get_parameters(parameter_file)
    stepper0.setVelocityLimit(int(speed))
#Close your Phidgets once the program is done.
stepper0.close()
digitalInput1.close()
digitalInput2.close()
digitalInput3.close()
