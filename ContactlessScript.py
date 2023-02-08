import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import math
import os

#parameter reading function 
def get_parameters():
    parameter_data = np.genfromtxt(parameter_path)
    return (parameter_data[0,2],parameter_data[1,2],parameter_data[2,2])
    #The format of the output is (RampRate, FinalTemp, Status)
    #status is an int [0,2]
    # No Ramp = 0
    # Ramp = 1
    # Stop = 2

save_path = ('C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData')
parameter_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\parameters.dat'

avg_num = 4 #this is the number times the lock in will get each voltage before the average is reported

#Save data file
file_input = input("Please type the file name here: ")
filename = file_input + ".dat"
completeName = os.path.join(save_path, filename)

file = open(completeName, "a")
file.write("Time (sec)" + "\t" + "T (K)" + "\t" + "Vx (V)" + "\t" + "Vy (V)")
file.write("\n")
file = completeName

#open instaments
rm = pyvisa.ResourceManager()
ls = rm.open_resource('GPIB0::16::INSTR')#this is the lake shore temp controller
time.sleep(0.1)
srs = rm.open_resource('GPIB0::13::INSTR')#this is the lock-in
time.sleep(0.1)

#initialize plots
fig = plt.figure(constrained_layout = True)
ax = fig.add_subplot(2, 2, 1)
bx = fig.add_subplot(2, 2, 2)
cx = fig.add_subplot(2, 2, 3)
dx = fig.add_subplot(2, 2, 4)
fig.suptitle('Resistance measurement')
#fig.suptitle('Resistivity measurement', fontname = "Times New Roman", fontweight = 'bold', fontsize = 20)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (K)')
bx.set_xlabel('Time (s)')
bx.set_ylabel('Heater Percent (%)')
cx.set_xlabel('Time (s)')
cx.set_ylabel('Vx (mV)')
dx.set_xlabel('Time (s)')
dx.set_ylabel('Vx (mV)')

#set intial lakeshore parameters
parameters = get_parameters()
ls.write('RAMP 1,1,%.2f' % parameters[0])
time.sleep(0.05)
ls.write('SETP 1,%.2f' % parameters[1])
time.sleep(0.05)


values = {}
intitial_time = time.perf_counter()#get intitial time

#main loop
while parameters[2] != 2:
    #update parameters each interation
    del parameters #all local variables are deleted to prevent data pileup in secondary memory that slow processes down
    parameters = get_parameters()

    values['time'] = time.perf_counter()-intitial_time
    values['Temp'] = float(ls.query('KRDG? a'))
    time.sleep(0.05)
    

    
    # values['T_sample'] = float(ls.query('KRDG? b'))
    # time.sleep(0.05)
    values['heater'] = float(ls.query('HTR? 1'))
    time.sleep(0.05)

    ls.write('RAMP 1,1,%.2f' % parameters[0])
    time.sleep(0.05)

    if parameters[2] == 1: #ramp mode
        ls.write('SETP 1,%.2f' % parameters[1])#this sets the setpoint to the final desired temp
    elif parameters[2] == 0: #ramp mode
        ls.write('SETP 1,%.2f' % 1)#this sets the setpoint to 1 Kelvin, which turns off the heating
    time.sleep(0.05)
    vx=0
    vy=0
    for i in range(avg_num):
        p = srs.query('SNAPD?')
        p1 = p.split(',') #this is [Vx, Vy, Resistance, Theta]
        vx += float(p1[0])/avg_num
        vy += float(p1[1])/avg_num
        del p, p1
        time.sleep(0.1)

    if parameters[1] <= values['Temp']:
        parameters[2] = 2 #stop condition
    values['Vx'] = vx
    values['Vy'] = vy
    ax.plot(values['time'],values['Temp'],'bo--')
    bx.plot(values['time'],values['heater'],'ro--')
    cx.plot(values['time'],1000*values['Vx'],'bo--')
    dx.plot(values['time'],1000*values['Vy'],'bo--')
   
    plt.pause(0.1) #this displays the graph
    time.sleep(0.1)

    #save data
    file = open(completeName, "a")
    file.write(str(values['time']) + "\t" +  str(values['Temp']) + "\t" + str(values['Vx']) + "\t" + str(values['Vy'])+"\n")
    file.flush()
    time.sleep(0.1)

    del values['time'],values['Temp'],values['Vx'],values['Vy'],values['heater']#,values['T_sample'],values['R'],values['Th'], values['V_total']
    del vx, vy#, vr, vt
    file.close()
# print("measurement_done")

ls.write('SETP 1,%.2f' % 1)#turn off the heater
time.sleep(0.05)
ls.close()
srs.close()
#sr.close()
##file.close()
