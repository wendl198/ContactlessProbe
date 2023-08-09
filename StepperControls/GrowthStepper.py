from Phidget22.Phidget import *
from Phidget22.Devices.Log import *
from Phidget22.LogLevel import *
from Phidget22.Devices.Stepper import *
from Phidget22.Devices.DigitalInput import *
import time

#Declare any event handlers here. These will be called every time the associated event occurs.

def onDigitalInput1_StateChange(self, state):
	print("State [1]: " + str(state))

def onDigitalInput2_StateChange(self, state):
	print("State [2]: " + str(state))

def onDigitalInput3_StateChange(self, state):
	print("State [3]: " + str(state))

def main():
	Log.enable(LogLevel.PHIDGET_LOG_INFO, "phidgetlog.log")
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
	stepper0.setTargetPosition(10000)
	stepper0.setEngaged(True)

	try:
		input("Press Enter to Stop\n")
	except (Exception, KeyboardInterrupt):
		pass

	#Close your Phidgets once the program is done.
	stepper0.close()
	digitalInput1.close()
	digitalInput2.close()
	digitalInput3.close()

main()
