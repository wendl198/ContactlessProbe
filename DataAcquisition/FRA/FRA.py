import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import warnings
import os

save_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData'

save_file = open(os.path.join(save_path, input("Please type the file name here: ") + ".dat"), "a")
save_file.write("Time (min)" + "\t" + "T (K)" + "\t" + 'Freq (kHz)' + "\t"+ "Vx (V)" + "\t" + "Vy (V)"+"\n")

freqs = np.array([100.003,250.003,400.003,671.111,800.003,1000.03,1200.03,1500.03,1800.03,2000.03,2500.03,3000.03,4000.03])
trials = 3
vx = []
vy = []

rm = pyvisa.ResourceManager()
ls = rm.open_resource('GPIB0::16::INSTR')#this is the lake shore temp controller
time.sleep(0.1)
srs = rm.open_resource('GPIB0::13::INSTR')#this is the lock-in
time.sleep(0.1)

values = {}
intitial_time = time.perf_counter()#get intitial time

for i in range(len(trials)):
    print('Begin Trial 1')
    vx.append([])
    vy.append([])
    for freq in freqs:
        ls.write('FREQ '+ freq + ' KHZ')
        time.sleep(5)
        values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
        values['Temp'] = float(ls.query('KRDG? a')) #temp in K
        vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Voltage Magnitude, Theta]
        values['Vx'] = float(vs[0])
        values['Vy'] = float(vs[1])
        values['Freq'] = freq
        save_file.write(str(values['time']) + "\t" +  str(values['Temp']) + "\t" + str(values['Freq']) + "\t" + str(values['Vx']) + "\t" + str(values['Vy'])+"\n")
        save_file.flush()

#######################
# Close Instruments
#######################
time.sleep(0.05)
ls.close()
srs.close()
save_file.close()