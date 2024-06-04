import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import warnings
import os
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore")

#############################
# Initialize Functions
#############################

def get_parameters(f):
    try:
        f.seek(0) #resets pointer to top of the file
        lines = f.readlines()
        lines[6] = lines[6].split()
        lines[6].pop(0) #this removes the word, but still returns a list if empty
        return (lines[0].split()[1],#RampRate
                lines[1].split()[1],#StartTemp
                lines[2].split()[1],#FinalTemp
                int(lines[3].split()[1]),#RampingStatus
                [lines[4].split()[1],lines[4].split()[2],lines[4].split()[3]],#PID paratmeters
                int(lines[5].split()[1]),#Autoscale boolean
                lines[6],#time scale
                lines[7].split()[1:3])# voltage offset values [Vx,Vy] in mV
    except:
        print('Error Reading Parameters: Edit parameters.txt or redownload it from https://github.com/wendl198/ContactlessProbe.')
        print('Warning: Data is not currently being recorded.')
        time.sleep(1)
        return get_parameters(f) #this will recursively tunnel deeper until the problem is fixed. It will not record data
    #May be smart to install a better fail safe, but this is probably good enough for most users.

def change_status(new_status,f):
    f.seek(0)
    lines = f.readlines()
    lines[3] = lines[3][:-2] + str(new_status) +'\n'
    file1 = open(parameter_path,"w")#write mode
    file1.writelines(lines)
    file1.close()
    #status is an integer [0,2]
    # No Ramp = 0
    # StartRamp = 1
    # Stop = 2

#paths
save_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData'
parameter_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\parameters.txt'
default_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\default_parameters.txt'

# adjustable parameters
pause_time = .85 #time in sec

#######################
# Open Files
#######################
save_file = open(os.path.join(save_path, input("Please type the file name here: ") + ".dat"), "a")
parameter_file = open(parameter_path, 'r')
#the idea is to keep the files open and avoid constant opening and closing. Use file.flush() to save data

#######################
# Open Instuments
#######################

rm = pyvisa.ResourceManager()
ls = rm.open_resource('GPIB0::16::INSTR')#this is the lake shore temp controller
time.sleep(0.1)
srs = rm.open_resource('GPIB0::13::INSTR')#this is the lock-in
time.sleep(0.1)

#set intial lakeshore parameters
parameters = get_parameters(parameter_file)
ls.write('RAMP 1,0,'+ parameters[0]) #the ramping is intially off
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1]) #this is the starting temp for the ramp
time.sleep(0.05)
ls.write('Range 1,0') #this turns the heater off

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
bx.set_xlabel('Temperature (K)')
bx.set_ylabel('Phase of Voltage (rad)')
cx.set_xlabel('Time (min)')
cx.set_ylabel('Vx (mV)')
dx.set_xlabel('Time (min)')
dx.set_ylabel('Vy (mV)')

T0 = float(ls.query('KRDG? a'))
p1, = ax.plot(0,T0,'ko-')
vs = srs.query('SNAPD?').split(',')
p2, = bx.plot(T0,np.angle(float(vs[0])-float(parameters[7][0])+(float(vs[1])-float(parameters[7][1]))*1j),'ro-')
p3, = cx.plot(0,1000*float(vs[0]),'bo-') #plot in mV
p4,= dx.plot(0,1000*float(vs[1]),'go-')

values = {}
intitial_time = time.perf_counter()#get intitial time

save_file.write("Time (min)" + "\t" + "T (K)" + "\t" + "Vx (V)" + "\t" + "Vy (V)"+'\t'+'Initial Time'+'\t'+str(intitial_time)+"\n")

#######################
# Main Loop
#######################

while parameters[3] < 2:
    ########################
    # Update Parameters
    ########################
    parameters = get_parameters(parameter_file)

    values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
    values['Temp'] = float(ls.query('KRDG? a')) #temp in K
    vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Resistance, Theta]
    values['Vx'] = float(vs[0])
    values['Vy'] = float(vs[1])

    ########################
    # Update Ramping Status
    ########################

    ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)
    bx.set_title('Setpoint ='+str(ls.query('SETP? 1'))[1:6],fontsize = 12)

    if parameters[3] == 0 or values['Temp'] == 0: #no ramp
        ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
        time.sleep(0.05)
        ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping
        time.sleep(0.1)
        ls.write('Range 1,0') #this turns the heater off
    elif parameters[3] == 1: #ramp mode
        #ax.legend().set_visible(False)
        ls.write('RAMP 1,1,'+ parameters[0])
        time.sleep(0.05)
        ls.write('SETP 1,'+ parameters[2])#this sets the setpoint to the final temp
        time.sleep(0.05)
        ls.write('PID 1,'+ parameters[4][0]+','+ parameters[4][1]+',' + parameters[4][2])#this sets the setpoint to the final temp
        time.sleep(0.05)
        ls.write('Range 1,1') #this turns the heater to low
        
    
    #######################
    # Plotting
    #######################

    # update data
    times = np.append(p1.get_xdata(),values['time'])
    y1 = np.append(p1.get_ydata(),values['Temp'])
    y3 = np.append(p3.get_ydata(),1000*values['Vx']) # plot the voltages in mV
    y4 = np.append(p4.get_ydata(),1000*values['Vy'])
    y2 = np.angle(y3-float(parameters[7][0])+(y4-float(parameters[7][1]))*1j)

    p1.set_xdata(times)
    p3.set_xdata(times)
    p4.set_xdata(times)
    p1.set_ydata(y1)
    p3.set_ydata(y3)
    p4.set_ydata(y4)

    #update limits 
    # Note p2 is special because temperature on x axis

    if parameters[5]:
        p2.set_xdata(y1)
        p2.set_ydata(y2)
        ax.set_xlim(left = 0, right = values['time'])
        bx.set_xlim(left = y1.min(), right = y1.max())
        cx.set_xlim(left = 0, right = values['time'])
        dx.set_xlim(left = 0, right = values['time'])
        ax.set_ylim(bottom = y1.min(), top = y1.max())
        bx.set_ylim(bottom = y2.min(), top = y2.max())
        cx.set_ylim(bottom = y3.min(), top = y3.max())
        dx.set_ylim(bottom = y4.min(), top = y4.max())
    else:
        if len(parameters[6]) == 2:
            t0 = float(parameters[6][0])
            if t0> times[-1]:
                t0 = times[-1]-.1
            t1 = float(parameters[6][1])
            inds = np.logical_and(times >= t0, times <= t1)
            p2.set_xdata(y1[inds])
            p2.set_ydata(y2[inds])
            ax.set_xlim(left = t0,right = t1)
            bx.set_xlim(left = y1[inds].min(),right = y1[inds].max())
            cx.set_xlim(left = t0,right = t1)
            dx.set_xlim(left = t0,right = t1)
        elif len(parameters[6]) == 1:
            t0 = float(parameters[6][0])
            if t0> times[-1]:
                t0 = times[-1]-.1
            inds = np.logical_not(times<t0)
            p2.set_xdata(y1[inds])
            p2.set_ydata(y2[inds])
            ax.set_xlim(left = t0,right = values['time'])
            bx.set_xlim(left = y1[inds].min(),right = y1[inds].max())
            cx.set_xlim(left = t0,right = values['time'])
            dx.set_xlim(left = t0,right = values['time'])
        else:
            inds = np.logical_not(times<0)
            p2.set_xdata(y1)
            p2.set_ydata(y2)
            ax.set_xlim(left = 0, right = values['time'])
            bx.set_xlim(left = y1.min(), right = y1.max())
            cx.set_xlim(left = 0, right = values['time'])
            dx.set_xlim(left = 0, right = values['time'])
        ax.set_ylim(bottom = y1[inds].min(), top = y1[inds].max())
        bx.set_ylim(bottom = y2[inds].min(), top = y2[inds].max())
        cx.set_ylim(bottom = y3[inds].min(), top = y3[inds].max())
        dx.set_ylim(bottom = y4[inds].min(), top = y4[inds].max())

    

    #######################
    # Save Data
    #######################

    save_file.write(str(values['time']) + "\t" +  str(values['Temp']) + "\t" + str(values['Vx']) + "\t" + str(values['Vy'])+"\n")
    save_file.flush()#this will save the data without closing the file


    plt.pause(pause_time) #this displays the graph

    #check if final temp is reached
    if float(parameters[2]) <= values['Temp']:
        change_status(0,parameter_file) #stop ramping, but still collect data


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
srs.close()

#######################
# Reset Parameters
#######################
save_file.close()
parameter_file.close()
with open(default_path) as f:
    lines = f.readlines()
file1 = open(parameter_path,"w")#write mode
file1.writelines(lines)
file1.close()
