import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
# import warnings
import os

save_path = 'C:\\Users\\Contactless\\Desktop\\Contactless Probe\\RawData'

save_file = open(os.path.join(save_path, input("Please type the file name here: ") + ".dat"), "a")
save_file.write("Time (min)"   + "\t"+ "Vx (V)" + "\t" + "Vy (V)"+ "\t" + "R (V)"+ "\t" + 'Freq (kHz)'+ "\t" + "Time Constant (ms)"+"\n")
#votlage mode: -1 means A-B mode, 1 means A

signal_amp = 100 #in mV
time_cons = [100] #ms
freq_range = [5,4000] #in kHz
scan_time = 60*60 #in seconds

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
    'SCNRST', #reset scan
    'SLVL '+str(signal_amp)+' MV',
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
    #print(com)
    srs.write(com) #execute command
    time.sleep(0.01)#wait 10ms


values = {}
intitial_time = time.perf_counter()#get intitial time

srs.write('SCNRUN')
print('Sweeping at ' + str((freq_range[1]-freq_range[0])/scan_time*60) +' kHz/min')
for time_con in time_cons:
    srs.write('OFLT 10') #100ms time cosntant
    while srs.query('SCNSTATE?').strip()=='2':#scan is running
        values['Vx'],values['Vy'],values['R'],values['Freq'] = srs.query('SNAPD?').split(',') 
        R = float(values['R'])*1000 #this is the Voltage Magnitude in mV
        j = sens_dict[sens_keys[np.logical_not(sens_keys<R)][0]]
        k = input_range_dict[input_range_keys[np.logical_not(input_range_keys<R)][0]]
        srs.write('IRNG '+str(k))
        srs.write('SCAL '+str(j))
        values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
        save_file.write(str(values['time'])  + "\t" + values['Vx'].strip() + "\t" + values['Vy'].strip()+ "\t" +  values['R'].strip() + "\t" + values['Freq'].strip()+ "\t"+str(time_con)+"\n")
        save_file.flush()
        time.sleep(time_con*5/1000)


#######################
# Close Instruments
#######################
time.sleep(0.05)
srs.write('SCNENBL 0')
ls.close()
srs.close()
save_file.close()
