import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import math
import os

save_path = ('C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData')
parameter_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\parameters.dat'


#Save data file
file_input = input("Please type the file name here: ")
filename = file_input + ".dat"
completeName = os.path.join(save_path, filename)

file = open(completeName, "a")
file.write("Time (sec)" + "\t" + "T (K)" + "\t" + "T_sample(K)" + "\t" + "R" + "\t" + "Th" + "\t" + "V")
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

fig = plt.figure(constrained_layout = True)
ax = fig.add_subplot(1, 2, 1)
bx = fig.add_subplot(1, 2, 2)


TA_temp = ls.query('KRDG? a')
TA = float(TA_temp)
time.sleep(0.05)
TB_temp = ls.query('KRDG? b')
TB = float(TB_temp)
time.sleep(0.05)
ls.write('RAMP 1,1,%.2f' % rrate)
time.sleep(0.05)
ls.write('SETP 1,%.2f' % finalT)
time.sleep(0.05)

while Stop_flag == 0:
    time.sleep(0.05)
    values = {}
    xa,ya,xb,yb,vx, vy, vr, vt = [[],[],[],[],[],[],[], []]
    del Stop_flag
    
    time1 = time.perf_counter()

    rrate = Parameter_Reader.rrate()
    finalT = Parameter_Reader.finalT()
    Stop_flag = Parameter_Reader.Stop_flag()

    TA_temp = ls.query('KRDG? a')
    TA = float(TA_temp)
    time.sleep(0.1)
    TB_temp = ls.query('KRDG? b')
    TB = float(TB_temp)
    time.sleep(0.05)
    ls.write('RAMP 1,1,%.2f' % rrate)
    time.sleep(0.05)
    ls.write('SETP 1,%.2f' % finalT)
    time.sleep(0.05)

   
    for i in range(4):
        p = srs.query('SNAPD?')
        p1 = p.split(',')
        vx_temp = float(p1[0])
        vy_temp = float(p1[1])
        vr_temp = float(p1[2])
        vt_temp = float(p1[3])
        vx.append(vx_temp)
        vy.append(vy_temp)
        vr.append(vr_temp)
        vt.append(vt_temp)
        del vx_temp, vy_temp, vr_temp, vt_temp
        time.sleep(0.1)

    vx_final = sum(vx)/4
    vy_final = sum(vy)/4
    vr_final = sum(vr)/4
    vt_final = sum(vt)/4
    v_final = math.sqrt((vx_final)**2+(vy_final)**2)

    values['time'] = time1
    values['T'] = TA
    values['T_sample'] = TB
    values['R'] = vr_final
    values['Th'] = vt_final
    values['V_total'] = v_final 

    #fig.suptitle('Resistivity measurement', fontname = "Times New Roman", fontweight = 'bold', fontsize = 20)
    fig.suptitle('Resistance measurement')
    xa.append(values['T'])
    ya.append(values['R'])

    xb.append(values['time'])
    yb.append(values['R'])

    ax.plot(xa,ya,'bo--')
    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('R')
   
    bx.plot(xb,yb,'bo--')
    bx.set_xlabel('Time')
    bx.set_ylabel('R')
   
    plt.pause(0.1)

    time.sleep(0.1)

    file = open(completeName, "a")
    file.write(str(values['time']) + "\t" +  str(values['T']) + "\t" + str(values['T_sample']) + "\t" + str(values['R'])   + "\t" + str(values['Th']) + "\t" + str(values['V_total']))
    file.write("\n")
    file.flush()
    time.sleep(0.1)

    del time1,TA_temp,TA, TB_temp,TB, vx_final, vr_final, vy_final, vt_final, values['time'],values['T'],values['T_sample'],values['R'],values['Th'], values['V_total']
    del xa,ya,xb,yb,vx, vy, vr, vt
    file.close()
   
print("measurement_done")
ls.close()
srs.close()
#sr.close()
##file.close()
