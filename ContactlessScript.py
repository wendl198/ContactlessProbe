import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import math
import os

save_path = ('C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData')
parameter_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\parameters.dat'


avg_num = 4 #this is the number times the lock in will get each voltage before the average is reported

#Save data file
file_input = input("Please type the file name here: ")
filename = file_input + ".dat"
completeName = os.path.join(save_path, filename)

file = open(completeName, "a")
file.write("Time (sec)" + "\t" + "T (K)" + "\t" + "Vx (V)" + "\t" + "Vy (V)" + "\t" + "Th" + "\t" + "V")
file.write("\n")
file = completeName

#open instaments
rm = pyvisa.ResourceManager()

ls = rm.open_resource('GPIB0::16::INSTR')#this is the lake shore temp controller
time.sleep(0.1)
srs = rm.open_resource('GPIB0::13::INSTR')#this is the lock-in
time.sleep(0.1)

#parameter reading class   
class Parameter_Reader:
    def rrate():
        RT1 = np.genfromtxt(parameter_path)
        rrate = RT1[0,2]
        del RT1
        return rrate

    def finalT():
        RT1 = np.genfromtxt(parameter_path)
        finalT = RT1[1,2]
        del RT1
        return finalT
    
    def Stop_flag():
        RT1 = np.genfromtxt(parameter_path)
        Stop_flag = RT1[2,2]
        del RT1
        return Stop_flag

#get intitial parameters
rrate = Parameter_Reader.rrate()
finalT = Parameter_Reader.finalT()
Stop_flag = Parameter_Reader.Stop_flag()

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
cx.set_ylabel('Vx (?V)')
dx.set_xlabel('Time (s)')
dx.set_ylabel('Vx (?V)')

#set intial lakeshore parameters
ls.write('RAMP 1,1,%.2f' % rrate)
time.sleep(0.05)
ls.write('SETP 1,%.2f' % finalT)
time.sleep(0.05)


values = {}

#main loop
while Stop_flag == 0:
    time.sleep(0.05)
    
    del Stop_flag #all local variables are deleted to prevent data pileup in secondary memory that slows processes down
    
    values['time'] = time.perf_counter()

    rrate = Parameter_Reader.rrate()
    finalT = Parameter_Reader.finalT()
    Stop_flag = Parameter_Reader.Stop_flag()

    values['Temp'] = float(ls.query('KRDG? a'))
    if finalT <= values['Temp']:
        Stop_flag = 1
        print('all done')

    time.sleep(0.05)
    # values['T_sample'] = float(ls.query('KRDG? b'))
    # time.sleep(0.05)
    values['heater'] = float(ls.query('HTR? 1'))
    time.sleep(0.05)
    ls.write('RAMP 1,1,%.2f' % rrate)
    time.sleep(0.05)
    ls.write('SETP 1,%.2f' % finalT)
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
    values['Vx'] = vx
    values['Vy'] = vy
    ax.plot(values['time'],values['Temp'],'bo--')
    bx.plot(values['time'],values['heater'],'ro--')
    cx.plot(values['time'],values['Vx'],'bo--')
    dx.plot(values['time'],values['Vy'],'bo--')
   
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
finalT = Parameter_Reader.finalT()
ls.write('SETP 1,%.2f' % 273)
time.sleep(0.05)
ls.close()
srs.close()
#sr.close()
##file.close()
