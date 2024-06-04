import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import pyvisa
import time


signal_amp = 2000 #in mV
time_cons = [100] #ms
freq_range = [500,2500] #in kHz
scan_time = 60*2 #in seconds

save_path = 'C:\\Users\\Contactless\\Desktop\\Contactless Probe\\RawData'
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%m/%d/%Y %H:%M:%S")
save_file = open(os.path.join(save_path, input("Please type the file name here: ") + ".dat"), "a")
save_file.write("Time (min)"   + "\t"+ "Vx (V)" + "\t" + "Vy (V)"+ "\t" + "R (V)"+ "\t" + 'Freq (kHz)'+ "\t" + "Time Constant (ms): Current Time is "+formatted_datetime+' Signal Voltage is' +str(signal_amp)+'mV\n')
#voltage mode: -1 means A-B mode, 1 means A

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
    'SLVL '+str(signal_amp)+' MV', #intialize voltage
    'FREQ '+ str(freq_range[0]) + ' KHZ' #intialize frequency
    'SCNPAR F', #set freq scan
    'SCNFREQ 0, '+str(freq_range[0])+' KHZ', #scan freq range
    'SCNFREQ 1, '+str(freq_range[1])+' KHZ',
    'SCNSEC ' +str(scan_time), #total scan time in seconds
    'SCNLOG 0',#set linear scan with 0 log scan with 1
    'SCNEND 0',
    'SCNINRVL 0',
    'ISRC 0',
    'CDSP 0, 0', #first data point is vx
    'CDSP 1, 1', #second is vy
    'CDSP 2, 2', #third is R
    'CDSP 3, 15', #fourth is freq
    'SCNENBL ON' #ready scan
]

for com in command_list:
    #print(com)
    srs.write(com) #execute command
    time.sleep(0.05)#wait 10ms

fig = plt.figure(constrained_layout = True)
ax = fig.add_subplot(3, 1, 1)
bx = fig.add_subplot(3, 1, 2)
cx = fig.add_subplot(3, 1, 3)
ax.set_xlabel('Frequency (kHz)')
bx.set_xlabel('Frequency (kHz)')
cx.set_xlabel('Frequency (kHz)')
ax.set_ylabel('Vx (mV)')
bx.set_ylabel('Vy (mV)')
cx.set_ylabel('Voltage Magnitude (mV)')

vx0,vy0,R0,f0 = srs.query('SNAPD?').split(',')
p1, = ax.plot(f1 := float(f0)/1000,1000*float(vx0),'ko-')
p2, = bx.plot(f1,1000*float(vy0),'ro-')
p3, = cx.plot(f1,1000*float(R0),'bo-') #plot in mV

values = {}
intitial_time = time.perf_counter()#get intitial time

srs.write('SCNRUN') #start scan
print('Sweeping at ' + str((freq_range[1]-freq_range[0])/scan_time*60) +' kHz/min')
time.sleep(.05)
for time_con in time_cons:
    srs.write('OFLT 10') #100ms time cosntant
    while srs.query('SCNSTATE?').strip()=='2':#scan is running
        plt.pause(time_con*5/1000)#this cnverts time_con from ms to s
        values['Vx'],values['Vy'],values['R'],values['Freq'] = srs.query('SNAPD?').split(',') 
        R = float(values['R'])*1000 #this is the Voltage Magnitude in mV
        j = sens_dict[sens_keys[np.logical_not(sens_keys<R)][0]]
        k = input_range_dict[input_range_keys[np.logical_not(input_range_keys<R)][0]]
        srs.write('IRNG '+str(k))
        srs.write('SCAL '+str(j))
        values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
        save_file.write(str(values['time'])  + "\t" + values['Vx'].strip() + "\t" + values['Vy'].strip()+ "\t" +  values['R'].strip() + "\t" + values['Freq'].strip()+ "\t"+str(time_con)+"\n")
        save_file.flush()
        
        ax.set_title('Current Frequency '+str(round(f:= (float(values['Freq'])/1000),1))+' kHz')

        
        freqs = np.append(p1.get_xdata(),f)
        y1 = np.append(p1.get_ydata(),1000*float(values['Vx'])) # plot the voltages in mV
        y2 = np.append(p2.get_ydata(),1000*float(values['Vy']))
        y3 = np.append(p3.get_ydata(),R)

        p1.set_xdata(freqs)
        p2.set_xdata(freqs)
        p3.set_xdata(freqs)
        p1.set_ydata(y1)
        p2.set_ydata(y2)
        p3.set_ydata(y3)

        ax.set_xlim(left = freq_range[0], right = f)
        bx.set_xlim(left = freq_range[0], right = f)
        cx.set_xlim(left = freq_range[0], right = f)
        ax.set_ylim(bottom = y1.min(), top = y1.max())
        bx.set_ylim(bottom = y2.min(), top = y2.max())
        cx.set_ylim(bottom = y3.min(), top = y3.max())

        


#######################
# Close Instruments
#######################
time.sleep(0.05)
srs.write('SCNENBL 0')
ls.close()
srs.close()
save_file.close()
