import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import math
import os

#parameter reading function 
def get_parameters():
    with open(parameter_path) as f:
        lines = f.readlines()
    del f
    return (float(lines[0].split()[1]),float(lines[1].split()[1]),float(lines[2].split()[1]),int(lines[3].split()[1]))
    #The format of the output is (RampRate, StartTemp, FinalTemp, Status)

def change_status(new_status):
    with open(parameter_path) as f:
        lines = f.readlines()
    del f
    lines[3] = lines[3][:-1] + str(new_status)
    file1 = open(parameter_path,"w")#write mode
    file1.writelines(lines)
    file1.close()
    del file1, lines
    #status is an int [0,2]
    # No Ramp = 0
    # StartRamp = 1
    # Stop = 2

save_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData'
parameter_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\parameters.txt'

#save_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData'
#parameter_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/parameters.txt'

avg_num = 4 #this is the number times the lock in will get each voltage before the average is reported

#Intitiate save data file
file_input = input("Please type the file name here: ")
filename = file_input + ".dat"
completeName = os.path.join(save_path, filename)

file = open(completeName, "a")
file.write("Time (min)" + "\t" + "T (K)" + "\t" + "Vx (V)" + "\t" + "Vy (V)"+"\n")
file = completeName


#open instuments
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
#fig.suptitle('Resistance measurement')
#fig.suptitle('Resistivity measurement', fontname = "Times New Roman", fontweight = 'bold', fontsize = 20)
ax.set_xlabel('Time (min)')
ax.set_ylabel('Temperature (K)')
bx.set_xlabel('Time (min)')
bx.set_ylabel('Heater Percent (%)')
cx.set_xlabel('Time (min)')
cx.set_ylabel('Vx (mV)')
dx.set_xlabel('Time (min)')
dx.set_ylabel('Vy (mV)')

#set intial lakeshore parameters
parameters = get_parameters()
ls.write('RAMP 1,0,%.2f' % parameters[0]) #the ramping is intially off
time.sleep(0.05)
ls.write('SETP 1,%.2f' % parameters[1])
time.sleep(0.05)


values = {}
intitial_time = time.perf_counter()#get intitial time

#main loop
while parameters[3] < 2:
    #update parameters each interation
    del parameters #all local variables are deleted to prevent data pileup in secondary memory that slow processes down
    parameters = get_parameters()

    values['time'] = (time.perf_counter()-intitial_time)/60
    values['Temp'] = float(ls.query('KRDG? a'))
    time.sleep(0.05)
    

    
    # values['T_sample'] = float(ls.query('KRDG? b'))
    # time.sleep(0.05)
    values['heater'] = float(ls.query('HTR? 1'))
    time.sleep(0.05)

    if parameters[3] == 0: #no ramp
        ls.write('RAMP 1,0,%.2f' % parameters[0])# Turns off ramping
        time.sleep(0.05)
        ls.write('SETP 1,%.5f' % parameters[1])# intializes temperature for ramping

    elif parameters[3] == 1: #ramp mode
        ls.write('RAMP 1,1,%.2f' % parameters[0])
        time.sleep(0.05)
        ls.write('SETP 1,%.5f' % parameters[2])#this sets the setpoint to the final temp
        time.sleep(0.05)

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

    if parameters[2] <= values['Temp'] and parameters[3]<2:
        change_status(0) #stop ramping condition
        del parameters
        parameters = get_parameters()
    values['Vx'] = vx
    values['Vy'] = vy
    ax.plot(values['time'],values['Temp'],'bo--')
    bx.plot(values['time'],values['heater'],'ro--')
    cx.plot(values['time'],1000*values['Vx'],'bo--')
    dx.plot(values['time'],1000*values['Vy'],'bo--')
    ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)
    bx.set_title('Setpoint ='+str(ls.query('SETP? 1'))[1:6],fontsize = 12)
   
    plt.pause(0.1) #this displays the graph
    time.sleep(0.1)

    #save data
    file = open(completeName, "a")
    file.write(str(values['time']) + "\t\t" +  str(values['Temp']) + "\t" + str(values['Vx']) + "\t\t" + str(values['Vy'])+"\n")
    file.flush()
    file.close()
    time.sleep(0.1)

    del values['time'],values['Temp'],values['Vx'],values['Vy'],values['heater']#,values['T_sample'],values['R'],values['Th'], values['V_total']
    del vx, vy#, vr, vt


ls.write('RAMP 1,0,%.2f' % parameters[0])#turn off ramping
time.sleep(0.05)
ls.write('SETP 1,%.5f' % parameters[1]) #set temp back to start
change_status(0)
time.sleep(0.05)
ls.close()
srs.close()
