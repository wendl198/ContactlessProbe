import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import warnings
import os

save_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData'

save_file = open(os.path.join(save_path, input("Please type the file name here: ") + ".dat"), "a")
save_file.write("Time (min)" + "\t" + "T (K)" + "\t" + 'Freq (kHz)' + "\t"+ "Vx (V)" + "\t" + "Vy (V)"+"\n")

set_temp = 92
freqs = np.array([100.003,250.003,400.003,671.111,800.003,1000.03,1200.03,1500.03,1800.03,2000.03,2500.03,3000.03,4000])
trials = 3
sens_dict = {1000:0,
            500:1,
            200:2,
            100:3,
            50:4,
            20:5,
            10:6,
            5:7,
            2:8,
            1:9,
            .5:10,
            .2:11}
input_range_dict = {1000:0,
                    300:1,
                    100:2,
                    30:3,
                    10:4}
rm = pyvisa.ResourceManager()
ls = rm.open_resource('GPIB0::16::INSTR')#this is the lake shore temp controller
time.sleep(0.1)
srs = rm.open_resource('GPIB0::13::INSTR')#this is the lock-in
time.sleep(0.1)
ls.write('RAMP 1,1,'+ str(set_temp))
time.sleep(0.1)
ls.write('SETP 1,'+ str(set_temp))

values = {}
intitial_time = time.perf_counter()#get intitial time

for i in range(trials):
    print('Begin Trial ' + str(i+1))
    for freq in freqs:
        try:
            srs.query('FREQ '+ str(freq) + ' KHZ')
        except:
            pass
        vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Voltage Magnitude, Theta]
        j = sens_dict[sens_dict.keys()[np.logical_not(sens_dict.keys()<vs[2])][0]]
        k = sens_dict[sens_dict.keys()[np.logical_not(input_range_dict.keys()<vs[2])][0]]
        vs = srs.query('IRNG '+str(k))
        vs = srs.query('SCAL '+str(j))
        time.sleep(3)
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
