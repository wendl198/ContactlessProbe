import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
# import warnings
import os

save_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData'

save_file = open(os.path.join(save_path, input("Please type the file name here: ") + ".dat"), "a")
save_file.write("Time (min)"   + "\t"+ "Vx (V)" + "\t" + "Vy (V)"+ "\t" + "R (V)"+ "\t" + 'Freq (kHz)'+ "\t" + "Time Constant (ms)"+"\n")
#votlage mode: -1 means A-B mode, 1 means A

signal_amp = 100 #in mV
time_cons = [100] #ms
freq_range = [100,2000] #in kHz
scan_time = 10*60 #in seconds


freqs = np.array([100.003,250.003,400.003,500.003,600.003,671.111,800.003,900.003,1000.03,1250.03,1500.03,1800.03,2000.03,2250.03,2500.03,2750.03,3000.03,3500.03,4000])
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
sens_keys = np.array(list(sens_dict.keys()))
sens_keys.sort()
input_range_dict = {1000:0,
                    300:1,
                    100:2,
                    30:3,
                    10:4}
input_range_keys = np.array(list(input_range_dict.keys()))
input_range_keys.sort()



rm = pyvisa.ResourceManager()
ls = rm.open_resource('GPIB0::16::INSTR')#this is the lake shore temp controller
time.sleep(0.1)
srs = rm.open_resource('GPIB0::13::INSTR')#this is the lock-in
time.sleep(0.1)
# srs.query('SLVL ',+str(signal_amp)+' MV')#set lock in voltage amplitude
# time.sleep(0.1)

#set scan parameters
command_list = [
    'SLVL ',+str(signal_amp)+' MV',
    'SCNPAR F',
    'SCNFREQ 0, '+str(freq_range[0])+' KHZ',
    'SCNFREQ 1, '+str(freq_range[1])+' KHZ',
    'SCNSEC ' +str(scan_time),
    'SCNLOG 0',
    'SCNEND 0',
    'SCNINRVL 0',
    'ISRC 0',
    'CDSP 0, 0', #first data point is vx
    'CDSP 1, 1', #second is vy
    'CDSP 2, 2', #third is R
    'CDSP 3, 15', #fourth is freq
    'SCNENBL ON'
]

for com in command_list:
    srs.query(com) #execute command
    time.sleep(0.01)#wait 10ms


values = {}
intitial_time = time.perf_counter()#get intitial time

srs.query('SCNRUN')

for time_con in time_cons:
    srs.query('OFLT 10')
    while srs.query('SCNSTATE')=='2':#scan is running
        values['Vx'],values['Vy'],values['R'],values['Freq'] = srs.query('SNAPD?').split(',') 
        R = float(values['R'])*1000 #this is the Voltage Magnitude in mV
        j = sens_dict[sens_keys[np.logical_not(sens_keys<R)][0]]
        k = input_range_dict[input_range_keys[np.logical_not(input_range_keys<R)][0]]
        try:
            vs = srs.query('IRNG '+str(k))
        except:
            pass
        try:
            vs = srs.query('SCAL '+str(j))
        except:
            pass
        values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
        #this is [Vx, Vy, Voltage Magnitude, Theta]
        save_file.write(str(values['time'])  + "\t" + str(values['Vx']) + "\t" + str(values['Vy'])+ "\t" +  str(values['R']) + "\t" + str(values['Freq'])+ "\t"+str(time_con)+"\n")
        save_file.flush()
        time.sleep(time_con*5)


#######################
# Close Instruments
#######################
time.sleep(0.05)
srs.query('SCNENBL 0')
ls.close()
srs.close()
save_file.close()
