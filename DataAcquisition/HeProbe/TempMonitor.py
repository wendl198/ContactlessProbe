import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import pyvisa
import time
from scipy import optimize
import warnings
import traceback

warnings.filterwarnings("ignore")

def get_parameters(f):
    try:
        f.seek(0) #resets pointer to top of the file
        lines = f.readlines()
        lines[9] = lines[9].split()
        lines[9].pop(0) #this removes the word, but still returns a list if empty
        return (lines[0].split()[1],#RampRate
                lines[1].split()[1],#StartTemp
                lines[2].split()[1],#FinalTemp
                float(lines[3].split()[1]),#SweepTime
                float(lines[4].split()[1]),#FreqWidth
                float(lines[5].split()[1]),#SignalAmp
                int(lines[6].split()[1]),#RampingStatus
                [lines[7].split()[1],lines[7].split()[2],lines[7].split()[3]],#PID paratmeters
                int(lines[8].split()[1]),#Autoscale boolean
                lines[9],#time scale
                int(lines[10].split()[1]),#ramp boolean
                int(lines[11].split()[1]), #3 part scan boolean
                float(lines[12].split()[1])) #central scan width
    except Exception as error:
        #print(error)
        print('Error Reading Parameters: Edit parameters.txt or redownload it from https://github.com/wendl198/ContactlessProbe.')
        print('Warning: Data is not currently being recorded.')
        time.sleep(1)
        return get_parameters(f) #this will recursively tunnel deeper until the problem is fixed. It will not record data
    #May be smart to install a better fail safe, but this is probably good enough for most users.

def change_status(new_status,f):
    f.seek(0)
    lines = f.readlines()
    lines[6] = 'Status: ' + str(new_status) +' 0=idle,1=intialscan,2=repeatedscan,>2=end\n'
    file1 = open(parameter_path,"w")#write mode
    file1.writelines(lines)
    file1.close()
    #status is an integer [0,2]
    # No Ramp = 0
    # StartRamp = 1
    # Stop = 2


class TempController:
    def __init__(self,GPIBport,parameters,max_power = 16, waittime = 0.05):
        self.instra = rm.open_resource('GPIB0::'+str(GPIBport)+'::INSTR')
        self.waittime = waittime
        self.modelnum = self.instra.query('*IDN?').split(',')[1][-3:]

        self.write('RAMP 1,0,'+ parameters[0]) #the ramping is intially off
        self.write('SETP 1,'+ parameters[1]) #this is the starting temp for the ramp
        self.write('Range 1,0') #this turns the heater off
        self.write('TLIMIT A,500')#set temp limit to 500K

        if self.modelnum == '325':
            self.write('CSET 1,A,1,0,2')# configure loop
            self.write('INTYPE A,[],[]')#specify diode
            self.write('HTRSET 1,2')# set to 50 ohm heater
        elif self.modelnum == '335':
            self.write('INTYPE A,1,0,0,0,1')#specify diode
            self.write('OUTMODE 1,1,1,0')#same as CSET
            self.write('HTRSET 1,1,0,'+str(min(round(np.sqrt(max_power/56),3),1))+',2')#set 50 ohm resister and max current
            self.write('MOUT 1,0')#set manual output to 0%
        else:
            print('LakeShore Model not recognized')
        self.write('INCRV A,02') #set to DT670 diode
    
    def write(self,command):
        self.instra.write(command)
        time.sleep(self.waittime)

    def query(self,command):
        return self.instra.query(command)
    
    def startramp(self, parameters):
        self.write('PID 1,'+ parameters[7][0]+','+ parameters[7][1]+',' + parameters[7][2])#this sets the setpoint to the final temp
        if self.modelnum == '325':
            self.write('Range 1,1') #this turns the heater to low
        elif self.modelnum == '335':
            self.write('Range,1,2')#set to medium. 
        else:
            print('How in the world did you even get this far??')

        if not(int(self.query('RAMP? 1')[0])): #if ramp is off, start ramp
            self.write('RAMP 1,1,'+ parameters[0])
            self.write('SETP 1,'+ parameters[2])#this sets the setpoint to the final temp

    def stopramp(self,parameters):
        ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
        ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping
        ls.write('Range 1,0') #this turns the heater off

    def close(self):
        self.instra.close()
        
# adjustable parameters
pause_time = .75 #time in sec


parameter_path = 'C:\\Users\\NewContactless\\Desktop\\Contactless Probe\\HeProbe\\HeProbeParameters.txt'
default_path = 'C:\\Users\\NewContactless\\Desktop\\Contactless Probe\\HeProbe\\HeProbeDefaultParameters.txt'
save_path = 'C:\\Users\\NewContactless\\Desktop\\Contactless Probe\\RawData\\HeProbe\\'




#set intial lakeshore parameters
parameter_file = open(parameter_path, 'r')
parameters = get_parameters(parameter_file)

rm = pyvisa.ResourceManager()
try:
    ls = TempController(16,parameters)
except:
    ls = TempController(9,parameters)
time.sleep(0.1)

ls.write('RAMP 1,0,'+ parameters[0]) #the ramping is intially off
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1]) #this is the starting temp for the ramp
time.sleep(0.05)
ls.write('Range 1,0') #this turns the heater off
time.sleep(0.05)
ls.write('CSET 1,A,1,0,2')# configure loop
time.sleep(0.05)
ls.write('TLIMIT 500')


fig = plt.figure(figsize = (12,9))
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel('Time (min)')
ax.set_ylabel('Temperature (K)')

T0 = float(ls.query('KRDG? a'))
intitial_time = time.perf_counter()#get intitial time
p1, = ax.plot(0,T0,'ko-')

values = {}
sweep_num = 0


#######################
# Main Loop
#######################

while parameters[6] < 3:#main loop
        
            values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
            values['Temp'] = float(ls.query('KRDG? a')) #temp in K

            #######################
            # Plotting
            #######################

            # update data

            ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)

            times = np.append(p1.get_xdata(),values['time'])
            y1 = np.append(p1.get_ydata(),values['Temp'])
            
            p1.set_xdata(times)
            p1.set_ydata(y1)

            #update limits 
            if parameters[8]:
                ax.set_xlim(left = 0, right = values['time'])
                ax.set_ylim(bottom = y1.min(), top = y1.max())
            else:
                if len(parameters[9]) == 2:
                    t0 = float(parameters[9][0])
                    if t0> times[-1]:
                        t0 = times[-1]-.1
                    t1 = float(parameters[9][1])
                    inds = np.logical_and(times >= t0, times <= t1)
                    ax.set_xlim(left = t0,right = t1)
                elif len(parameters[9]) == 1:
                    t0 = float(parameters[9][0])
                    if t0> times[-1]:
                        t0 = times[-1]-.1
                    inds = np.logical_not(times<t0)
                    ax.set_xlim(left = t0,right = values['time'])
                else:
                    inds = np.logical_not(times<0)
                    ax.set_xlim(left = 0, right = values['time'])
                ax.set_ylim(bottom = y1[inds].min(), top = y1[inds].max())

            plt.pause(0.1)

            parameters = get_parameters(parameter_file)

#######################
# Close Instruments
#######################
ls.write('RAMP 1,0,'+ parameters[0])#turn off ramping
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1]) #set temp back to start
time.sleep(0.05)
ls.write('Range 1,0') #this turns the heater off
time.sleep(0.05)
ls.close()

#######################
# Reset Parameters
#######################
parameter_file.close()
with open(default_path) as f:
    lines = f.readlines()
file1 = open(parameter_path,"w")#write mode
file1.writelines(lines)
file1.close()
