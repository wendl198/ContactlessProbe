import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import pyvisa
import time


def get_parameters(f):
    try:
        f.seek(0) #resets pointer to top of the file
        lines = f.readlines()
        lines[9] = lines[9].split()
        lines[9].pop(0) #this removes the word, but still returns a list if empty
        return (lines[0].split()[1],#RampRate
                lines[1].split()[1],#StartTemp
                lines[2].split()[1],#FinalTemp
                lines[3].split()[1],#SweepTime
                lines[4].split()[1],#FreqWidth
                lines[5].split()[1],#SignalAmp
                int(lines[6].split()[1]),#RampingStatus
                [lines[7].split()[1],lines[7].split()[2],lines[7].split()[3]],#PID paratmeters
                int(lines[8].split()[1]),#Autoscale boolean
                lines[9])#time scale
    except Exception as error:
        #print(error)
        print('Error Reading Parameters: Edit parameters.txt or redownload it from https://github.com/wendl198/ContactlessProbe.')
        print('Warning: Data is not currently being recorded.')
        time.sleep(1)
        return get_parameters(f) #this will recursively tunnel deeper until the problem is fixed. It will not record data
    #May be smart to install a better fail safe, but this is probably good enough for most users.

def change_status(new_status,f):
    f.seek(0)
    lines = f.readlines()
    lines[6] = lines[6][:-2] + str(new_status) +'\n'
    file1 = open(parameter_path,"w")#write mode
    file1.writelines(lines)
    file1.close()
    #status is an integer [0,2]
    # No Ramp = 0
    # StartRamp = 1
    # Stop = 2


def intiate_scan(instrument,start_freq,end_freq,signal_amp,scan_time,repeat,wait_time = 0.05):
    for com in set_command_list:
        instrument.write(com) #execute command
        time.sleep(wait_time)#wait
    instrument.write('SLVL '+str(signal_amp)+' MV') #intialize voltage
    time.sleep(wait_time)#wait
    instrument.write('FREQ '+ str(start_freq) + ' KHZ') #intialize frequency
    time.sleep(wait_time)#wait
    instrument.write('SCNFREQ 0, '+str(start_freq)+' KHZ') #scan freq range
    time.sleep(wait_time)#wait
    instrument.write('SCNFREQ 1, '+str(end_freq)+' KHZ')
    time.sleep(wait_time)#wait
    instrument.write('SCNSEC ' +str(scan_time)) #total scan time in seconds
    time.sleep(wait_time)#wait
    if repeat:
        instrument.write('SCNEND 1') #0 is an individual scan, 1 repeats
    else:
        instrument.write('SCNEND 0') #0 is an individual scan, 1 repeats
    time.sleep(wait_time)
    instrument.write('SCNENBL ON') #ready scan
    

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
timeconsts_dict = {1e-6:0,
                    3e-6:1,
                    10e-6:2,
                    30e-6:3,
                    100e-6:4,
                    300e-6:5,
                    1e-3:6,
                    3e-3:7,
                    10e-3:8,
                    30e-3:9,
                    100e-3:10,
                    300e-3:11,
                    1:12,
                    3:13,
                    10e-6:14,
                    30e-6:15,
                    100:16,
                    300:17,
                    1e3:18,
                    3e3:19,
                    10e3:20,
                    30e3:21}
timeconsts_keys = np.array(list(timeconsts_dict.keys()))
timeconsts_keys.sort()


# adjustable parameters
pause_time = .85 #time in sec
time_con = 10e-3
i = sens_dict[sens_keys[np.logical_not(sens_keys<time_con)][0]]



set_command_list = [
    'SCNRST', #reset scan
    'SCNPAR F', #set freq scan
    'SCNLOG 0',#set linear scan with 0 log scan with 1
    'SCNINRVL 2', #freq scan time update resolution 0 =8ms 2=31ms
    'ISRC 0', #read only A voltage
    'OFLT '+ str(i), #set time constant
    'CDSP 0, 0', #first data point is vx
    'CDSP 1, 1', #second is vy
    'CDSP 2, 2', #third is R
    'CDSP 3, 15', #fourth is freq
]

save_path = 'C:\\Users\\Contactless\\Desktop\\Contactless Probe\\RawData\\HeProbe\\'
parameter_path = 'C:\\Users\\Contactless\\Desktop\\Contactless Probe\\HeProbe\\HeProbeParameters.txt'
default_path = 'C:\\Users\\Contactless\\Desktop\\Contactless Probe\\HeProbe\\HeProbeDefaultParameters.txt'

rm = pyvisa.ResourceManager()
ls = rm.open_resource('GPIB0::16::INSTR')#this is the lake shore temp controller
time.sleep(0.1)
srs = rm.open_resource('GPIB0::13::INSTR')#this is the lock-in
time.sleep(0.1)
srs.write('SCNRST')

#set intial lakeshore parameters
parameter_file = open(parameter_path, 'r')
parameters = get_parameters(parameter_file)
ls.write('RAMP 1,0,'+ parameters[0]) #the ramping is intially off
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1]) #this is the starting temp for the ramp
time.sleep(0.05)
ls.write('Range 1,0') #this turns the heater off

#set scan parameters
# initial_command_list = [
#     'SCNRST', #reset scan
#     'SLVL '+parameters[6]+' MV', #intialize voltage
#     'FREQ '+ str(500) + ' KHZ' #intialize frequency
#     'SCNPAR F', #set freq scan
#     'SCNFREQ 0, '+str(500)+' KHZ', #scan freq range
#     'SCNFREQ 1, '+str(4000)+' KHZ',
#     'SCNSEC ' +str(parameters[4]), #total scan time in seconds
#     'SCNLOG 0',#set linear scan with 0 log scan with 1
#     'SCNEND 0',
#     'SCNINRVL 0',
#     'ISRC 0',
#     'CDSP 0, 0', #first data point is vx
#     'CDSP 1, 1', #second is vy
#     'CDSP 2, 2', #third is R
#     'CDSP 3, 15', #fourth is freq
#     'SCNENBL ON' #ready scan
# ]

# #set scan parameters
# command_list = [
#     'SCNRST', #reset scan
#     'SLVL '+str(signal_amp)+' MV', #intialize voltage
#     'FREQ '+ str(freq_range[0]) + ' KHZ' #intialize frequency
#     'SCNPAR F', #set freq scan
#     'SCNFREQ 0, '+str(freq_range[0])+' KHZ', #scan freq range
#     'SCNFREQ 1, '+str(freq_range[1])+' KHZ',
#     'SCNSEC ' +str(scan_time), #total scan time in seconds
#     'SCNLOG 0',#set linear scan with 0 log scan with 1
#     'SCNEND 0',
#     'SCNINRVL 0',
#     'ISRC 0',
#     'CDSP 0, 0', #first data point is vx
#     'CDSP 1, 1', #second is vy
#     'CDSP 2, 2', #third is R
#     'CDSP 3, 15', #fourth is freq
#     'SCNENBL ON' #ready scan
# ]






# for com in command_list:
#     srs.write(com) #execute command
#     time.sleep(0.05)#wait 50ms


fig = plt.figure(constrained_layout = True)
ax = fig.add_subplot(2, 3, 1)
bx = fig.add_subplot(2, 3, 2)
cx = fig.add_subplot(2, 3, 3)
dx = fig.add_subplot(2, 3, 4)
ex = fig.add_subplot(2, 3, 5)
fx = fig.add_subplot(2, 3, 6)
ax.set_xlabel('Time (min)')
bx.set_xlabel('Temperature (K)')
cx.set_xlabel('Temperature (K)')
dx.set_xlabel('Frequency (kHz)')
ex.set_xlabel('Frequency (kHz)')
fx.set_xlabel('Frequency (kHz)')
ax.set_ylabel('Temperature (K)')
bx.set_ylabel('Resonance Frequency (kHz)')
cx.set_ylabel('Q Factor')
dx.set_ylabel('Vx (mV)')
ex.set_ylabel('Vy (mV)')
fx.set_ylabel('Voltage Magnitude (mV)')

T0 = float(ls.query('KRDG? a'))
vx0,vy0,R0,f0 = srs.query('SNAPD?').split(',')
p1, = ax.plot(0,T0,'ko-')
p2, = bx.plot(0,0,'ro-')
p3, = cx.plot(0,0,'bo-') 
p4, = dx.plot(f1 := float(f0)/1000,1000*float(vx0),'go-') #plot in mV
p5, = ex.plot(f1,1000*float(vy0),'co-') #plot in mV
p6, = fx.plot(f1,1000*float(R0),'mo-') #plot in mV

values = {}
sweep_num = 0

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%m/%d/%Y %H:%M:%S")
save_file = open(os.path.join(save_path, input("Please type the file name here: ") + ".dat"), "a")
save_file.write("Time (min)"   + "\t"+ 'Temp (K)'+"\t"+"Vx (V)" + "\t" + "Vy (V)"+ "\t" + "R (V)"+ "\t" + 'Freq (Hz)'+"\t"+ "Sweep Number: Current Time is "+formatted_datetime+'\n')
intitial_time = time.perf_counter()#get intitial time


# print('Sweeping at ' + str((freq_range[1]-freq_range[0])/scan_time*60) +' kHz/min')
time.sleep(.05)


#######################
# Main Loop
#######################

while parameters[6] < 3:#main loop
    while parameters[6] == 0: #idlely collecting data
        ########################
        # Update Parameters
        ########################
        parameters = get_parameters(parameter_file)

        values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
        values['Temp'] = float(ls.query('KRDG? a')) #temp in K
        vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Vmag, freq]
        values['Vx'] = float(vs[0])
        values['Vy'] = float(vs[1])
        values['Vmag'] = float(vs[2])
        values['freq'] = float(vs[3])

        ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)
        ax.set_title('CurrFreq ='+str(values['freq']),fontsize = 12)
        cx.set_title('Temp Setpoint ='+str(ls.query('SETP? 1'))[1:6],fontsize = 12)

        ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
        time.sleep(0.05)
        ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping
        time.sleep(0.1)
        ls.write('Range 1,0') #this turns the heater off

        #######################
        # Plotting only temp v time
        #######################

        # update data
        # while idle, want to only update temp v time,
        times = np.append(p1.get_xdata(),values['time'])
        y1 = np.append(p1.get_ydata(),values['Temp'])

        p1.set_xdata(times)
        p1.set_ydata(y1)
        if parameters[8]:
            ax.set_xlim(left = 0, right = values['time'])
            ax.set_ylim(bottom = y1.min(), top = y1.max())
        else:
            if len(parameters[6]) == 2:
                t0 = float(parameters[6][0])
                if t0> times[-1]:
                    t0 = times[-1]-.1
                t1 = float(parameters[6][1])
                inds = np.logical_and(times >= t0, times <= t1)
                ax.set_xlim(left = t0,right = t1)
            elif len(parameters[6]) == 1:
                t0 = float(parameters[6][0])
                if t0> times[-1]:
                    t0 = times[-1]-.1
                inds = np.logical_not(times<t0)
                ax.set_xlim(left = t0,right = values['time'])
            else:
                inds = np.logical_not(times<0)
                ax.set_xlim(left = 0, right = values['time'])
            ax.set_ylim(bottom = y1[inds].min(), top = y1[inds].max())

        #######################
        # Save Data
        #######################

        save_file.write(str(values['time']) + "\t" +  str(values['Temp']) + "\t" + str(values['Vx']) + "\t" + str(values['Vy'])+ '\t' + str(values['Vmag']) + '\t' + str(values['freq']) + '\t' + str(-1)+"\n")
        save_file.flush()#this will save the data without closing the file


        plt.pause(pause_time) #this displays the graph

    while parameters[6] == 1: #ramp mode
        #ax.legend().set_visible(False)
        ########################
        # Update Parameters
        ########################
        parameters = get_parameters(parameter_file)

        values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
        values['Temp'] = float(ls.query('KRDG? a')) #temp in K
        vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Vmag, Theta]
        values['Vx'] = float(vs[0])
        values['Vy'] = float(vs[1])
        values['Vmag'] = float(vs[2])
        values['freq'] = float(vs[3])

        ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
        time.sleep(0.05)
        ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping
        
        intiate_scan(srs,500,4000,2000,30,False)
        srs.write('SCNRUN') #start scan
        time.sleep(0.1)
        freqs = []
        a = srs.query('SCNSTATE?').strip() 
        print(a,a== '2')
        while srs.query('SCNSTATE?').strip() == '2':#scanning
            plt.pause(time_con*3)#this cnverts time_con from ms to s
            s = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Vmag, freq]
            values['Vx'] = float(vs[0])
            values['Vy'] = float(vs[1])
            values['Vmag'] = float(vs[2])
            values['freq'] = float(vs[3]) 
            R = values['Vmag']*1000 #this is the Voltage Magnitude in mV
            j = sens_dict[sens_keys[np.logical_not(sens_keys<R)][0]]
            k = input_range_dict[input_range_keys[np.logical_not(input_range_keys<R)][0]]
            srs.write('IRNG '+str(k))
            srs.write('SCAL '+str(j))
            values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
            #######################
            # Plotting
            #######################

            # update data
            times = np.append(p1.get_xdata(),values['time'])
            freqs.append(values['freq']/1000)
            y1 = np.append(p1.get_ydata(),values['Temp'])
            y4 = np.append(p4.get_ydata(),1000*values['Vx']) # plot the voltages in mV
            y5 = np.append(p5.get_ydata(),1000*values['Vy'])
            y6 = np.append(p6.get_ydata(),1000*values['Vmag'])

            p1.set_xdata(times)
            p4.set_xdata(freqs)
            p5.set_xdata(freqs)
            p6.set_xdata(freqs)
            p4.set_ydata(y4)
            p5.set_ydata(y5)
            p6.set_ydata(y6)

            #update limits 
            dx.set_xlim(left = 500, right = values['freq']/1000)
            ex.set_xlim(left = 500, right = values['freq']/1000)
            fx.set_xlim(left = 500, right = values['freq']/1000)
            dx.set_ylim(bottom = y4.min(), top = y4.max())
            ex.set_ylim(bottom = y5.min(), top = y5.max())
            fx.set_ylim(bottom = y6.min(), top = y6.max())
            if parameters[8]:
                ax.set_xlim(left = 0, right = values['time'])
                ax.set_ylim(bottom = y1.min(), top = y1.max())
            else:
                if len(parameters[6]) == 2:
                    t0 = float(parameters[6][0])
                    if t0> times[-1]:
                        t0 = times[-1]-.1
                    t1 = float(parameters[6][1])
                    inds = np.logical_and(times >= t0, times <= t1)
                    ax.set_xlim(left = t0,right = t1)
                elif len(parameters[6]) == 1:
                    t0 = float(parameters[6][0])
                    if t0> times[-1]:
                        t0 = times[-1]-.1
                    inds = np.logical_not(times<t0)
                    ax.set_xlim(left = t0,right = values['time'])
                else:
                    inds = np.logical_not(times<0)
                    ax.set_xlim(left = 0, right = values['time'])
                ax.set_ylim(bottom = y1[inds].min(), top = y1[inds].max())

                #######################
                # Save Data
                #######################

                save_file.write(str(values['time']) + "\t" +  str(values['Temp']) + "\t" + str(values['Vx']) + "\t" + str(values['Vy'])+ '\t' + str(values['Vmag']) + '\t' + str(values['freq']) + '\t' + str(0)+"\n")
                save_file.flush()
        change_status(2,parameter_file)
        parameters = get_parameters(parameter_file)
    while parameters[6] == 2: #ramp mode
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
    # if float(parameters[2]) <= values['Temp']:
    #     change_status(0,parameter_file) #stop ramping, but still collect data



# for time_con in time_cons:
#     i = sens_dict[sens_keys[np.logical_not(sens_keys<R)][0]]
#     srs.write('OFLT '+ str(i)) #time cosntant
#     while srs.query('SCNSTATE?').strip()=='2':#scan is running
#         plt.pause(time_con*5)#this cnverts time_con from ms to s
#         values['Vx'],values['Vy'],values['R'],values['Freq'] = srs.query('SNAPD?').split(',') 
#         R = float(values['R'])*1000 #this is the Voltage Magnitude in mV
#         j = sens_dict[sens_keys[np.logical_not(sens_keys<R)][0]]
#         k = input_range_dict[input_range_keys[np.logical_not(input_range_keys<R)][0]]
#         srs.write('IRNG '+str(k))
#         srs.write('SCAL '+str(j))
#         values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
#         save_file.write(str(values['time'])  + "\t" + values['Vx'].strip() + "\t" + values['Vy'].strip()+ "\t" +  values['R'].strip() + "\t" + values['Freq'].strip()+ "\t"+str(time_con)+"\n")
#         save_file.flush()
        
#         ax.set_title('Current Frequency '+str(round(f:= (float(values['Freq'])/1000),1))+' kHz')

        
#         freqs = np.append(p1.get_xdata(),f)
#         y1 = np.append(p1.get_ydata(),1000*float(values['Vx'])) # plot the voltages in mV
#         y2 = np.append(p2.get_ydata(),1000*float(values['Vy']))
#         y3 = np.append(p3.get_ydata(),R)

#         p1.set_xdata(freqs)
#         p2.set_xdata(freqs)
#         p3.set_xdata(freqs)
#         p1.set_ydata(y1)
#         p2.set_ydata(y2)
#         p3.set_ydata(y3)

#         ax.set_xlim(left = freq_range[0], right = f)
#         bx.set_xlim(left = freq_range[0], right = f)
#         cx.set_xlim(left = freq_range[0], right = f)
#         ax.set_ylim(bottom = y1.min(), top = y1.max())
#         bx.set_ylim(bottom = y2.min(), top = y2.max())
#         cx.set_ylim(bottom = y3.min(), top = y3.max())

        

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
