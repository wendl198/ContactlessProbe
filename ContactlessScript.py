import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import os

def get_parameters():
    with open(parameter_path) as f:
        lines = f.readlines()
    del f
    lines[6] = lines[6].split()
    del lines[6][0] #this removes the word, but still returns a list
    return (lines[0].split()[1],#RampRate
            lines[1].split()[1],#StartTemp
            lines[2].split()[1],#FinalTemp
            lines[3].split()[1],#RampingStatus
            [lines[4].split()[1],lines[4].split()[2],lines[4].split()[3]],#PID paratmeters
            lines[5].split()[1],#Autoscale boolean
            lines[6]) #time scale

def change_status(new_status):
    with open(parameter_path) as f:
        lines = f.readlines()
    del f
    lines[3] = lines[3][:-2] + str(new_status) +'\n'
    file1 = open(parameter_path,"w")#write mode
    file1.writelines(lines)
    file1.close()
    del file1, lines
    #status is an int [0,2]
    # No Ramp = 0
    # StartRamp = 1
    # Stop = 2


# save_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData'
# parameter_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\parameters.txt'


save_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData'
parameter_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/parameters.txt'

avg_num = 4 #this is the number times the lock-in will collect a voltage measurement before the average is reported

#######################
# Intitiate Save File
#######################
file_input = input("Please type the file name here: ")
filename = file_input + ".dat"
completeName = os.path.join(save_path, filename)

file = open(completeName, "a")
file.write("Time (min)" + "\t" + "T (K)" + "\t" + "Vx (V)" + "\t" + "Vy (V)"+"\n")
file = completeName

#######################
# Open Instuments
#######################

rm = pyvisa.ResourceManager()
ls = rm.open_resource('GPIB0::16::INSTR')#this is the lake shore temp controller
time.sleep(0.1)
srs = rm.open_resource('GPIB0::13::INSTR')#this is the lock-in
time.sleep(0.1)

#set intial lakeshore parameters
parameters = get_parameters()
ls.write('RAMP 1,0,'+ parameters[0]) #the ramping is intially off
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1])

#######################
# Initialize Plots
#######################

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

p1, = ax.plot(0,float(ls.query('KRDG? a')),'bo--')
p2, = bx.plot(0,float(ls.query('HTR? 1')),'ro--')
vs = srs.query('SNAPD?').split(',')
p3, = cx.plot(0,1000*float(vs[0]),'bo--') #plot in mV
p4,= dx.plot(0,1000*float(vs[1]),'bo--')
del vs

values = {}
intitial_time = time.perf_counter()#get intitial time


#######################
# Main Loop
#######################

while parameters[3] < 2:
    ########################
    # Update Parameters
    ########################
    del parameters #all local variables are deleted to prevent data pileup in secondary memory that slow processes down
    parameters = get_parameters()

    values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
    values['Temp'] = float(ls.query('KRDG? a')) #temp in K
    time.sleep(0.05)
    
    # values['T_sample'] = float(ls.query('KRDG? b'))
    # time.sleep(0.05)
    values['heater'] = float(ls.query('HTR? 1')) #this is the percentage of the heater
    time.sleep(0.05)

    vx=0
    vy=0
    for i in range(avg_num):
        vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Resistance, Theta]
        vx += float(vs[0])/avg_num
        vy += float(vs[1])/avg_num
        del vs
        time.sleep(0.1)
    values['Vx'] = vx
    values['Vy'] = vy

    ########################
    # Update Ramping Status
    ########################

    if parameters[3] == 0: #no ramp
        ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
        time.sleep(0.05)
        ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping

    elif parameters[3] == 1: #ramp mode
        ls.write('RAMP 1,1,'+ parameters[0])
        time.sleep(0.05)
        ls.write('SETP 1,'+ parameters[1])#this sets the setpoint to the final temp
        time.sleep(0.05)
        ls.write('PID 1,',+parameters[4][0]+','+parameters[4][1]+','+parameters[4][2])#this sets the setpoint to the final temp
    time.sleep(0.05)
    
    #######################
    # Plotting
    #######################

    # ax.plot(values['time'],values['Temp'],'ko--')
    # bx.plot(values['time'],values['heater'],'ro--')
    # cx.plot(values['time'],1000*values['Vx'],'bo--') #plot in mV
    # dx.plot(values['time'],1000*values['Vy'],'go--')

    p1.set_xdata(np.concatenate((p1.get_xdata(),values['time'])))
    p1.set_ydata(np.concatenate((p1.get_ydata(),values['Temp'])))
    p2.set_xdata(np.concatenate((p2.get_xdata(),values['time'])))
    p2.set_ydata(np.concatenate((p2.get_ydata(),values['heater'])))
    p3.set_xdata(np.concatenate((p3.get_xdata(),values['time'])))
    p3.set_ydata(np.concatenate((p3.get_ydata(),1000*values['Vx'])))
    p4.set_xdata(np.concatenate((p4.get_xdata(),values['time'])))
    p4.set_ydata(np.concatenate((p4.get_ydata(),1000*values['Vy'])))

    if parameters[5]:
        ax.set_xlim(left = 0, right = values['time'])
        bx.set_xlim(left = 0, right = values['time'])
        cx.set_xlim(left = 0, right = values['time'])
        dx.set_xlim(left = 0, right = values['time'])
    else:
        if len(parameters[6]) == 2:
            ax.set_xlim(left = parameters[6][0],right = parameters[6][1])
            bx.set_xlim(left = parameters[6][0],right = parameters[6][1])
            cx.set_xlim(left = parameters[6][0],right = parameters[6][1])
            dx.set_xlim(left = parameters[6][0],right = parameters[6][1])
        elif len(parameters[6]) == 1:
            ax.set_xlim(left = parameters[6][0],right = values['time'])
            bx.set_xlim(left = parameters[6][0],right = values['time'])
            cx.set_xlim(left = parameters[6][0],right = values['time'])
            dx.set_xlim(left = parameters[6][0],right = values['time'])
        else:
            ax.set_xlim(left = 0, right = values['time'])
            bx.set_xlim(left = 0, right = values['time'])
            cx.set_xlim(left = 0, right = values['time'])
            dx.set_xlim(left = 0, right = values['time'])

    ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)
    bx.set_title('Setpoint ='+str(ls.query('SETP? 1'))[1:6],fontsize = 12)
   
    plt.pause(0.2) #this displays the graph

    #######################
    # Save Data
    #######################

    file = open(completeName, "a")
    file.write(str(values['time']) + "\t" +  str(values['Temp']) + "\t" + str(values['Vx']) + "\t" + str(values['Vy'])+"\n")
    file.flush()
    file.close()

    #check if final temp is reached
    if parameters[2] <= values['Temp']:
        change_status(0) #stop ramping, but still collect data

    del values['time'],values['Temp'],values['Vx'],values['Vy'],values['heater']#,values['T_sample'],values['R'],values['Th'], values['V_total']
    del vx, vy#, vr, vt


#######################
# Close Instruments
#######################
ls.write('RAMP 1,0,'+ parameters[0])#turn off ramping
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1]) #set temp back to start
change_status(0)
time.sleep(0.05)
ls.close()
srs.close()