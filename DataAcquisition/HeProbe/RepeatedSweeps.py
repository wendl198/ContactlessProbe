import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import pyvisa
import time
from scipy import optimize
import warnings
import traceback

warnings.filterwarnings("ignore")

def get_parameters(f):
    try:
        f.seek(0) #resets pointer to top of the file
        lines = f.readlines()
        lines[9] = lines[9].split()
        lines[9].pop(0) #this removes the word, but still returns a list if empty
        return (lines[0].split()[1],#RampRate
                lines[1].split()[1],#StartTemp
                lines[2].split()[1],#FinalTemp
                float(lines[3].split()[1]),#SweepTime
                float(lines[4].split()[1]),#FreqWidth
                float(lines[5].split()[1]),#SignalAmp
                int(lines[6].split()[1]),#RampingStatus
                [lines[7].split()[1],lines[7].split()[2],lines[7].split()[3]],#PID paratmeters
                int(lines[8].split()[1]),#Autoscale boolean
                lines[9],#time scale
                int(lines[10].split()[1]),#ramp boolean
                int(lines[11].split()[1]), #3 part scan boolean
                float(lines[12].split()[1])) #central scan width
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
    lines[6] = 'Status: ' + str(new_status) +' 0=idle,1=intialscan,2=repeatedscan,>2=end\n'
    file1 = open(parameter_path,"w")#write mode
    file1.writelines(lines)
    file1.close()
    #status is an integer [0,2]
    # No Ramp = 0
    # StartRamp = 1
    # Stop = 2

def intiate_scan(instrument,start_freq,end_freq,signal_amp,scan_time,repeat,wait_time = 0.01):
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
        instrument.write('SCNEND 2') #0 is an individual scan, 1 repeats
    else:
        instrument.write('SCNEND 0') #0 is an individual scan, 1 repeats
        
    instrument.write('SCNRST') #reset scan
    instrument.write('SCNENBL ON') #intiate scan

def full_lorenzian_fit_with_skew(fs, f0,Q,Smax,A1,A2,A3):#fs is the data, f0 is the resonance freq
    return A1 + A2*fs + (Smax+A3*fs)/np.sqrt(1+4*(Q*(fs/f0-1))**2)#this is eq 10 from Measurement of resonant frequency and quality factor of microwave resonators: Comparison of methods Paul J. Petersan; Steven M. Anlage


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
                    10:14,
                    30:15,
                    100:16,
                    300:17,
                    1e3:18,
                    3e3:19,
                    10e3:20,
                    30e3:21}
timeconsts_keys = np.array(list(timeconsts_dict.keys()))
timeconsts_keys.sort()


# adjustable parameters
pause_time = .75 #time in sec
time_con = 10e-3
i = timeconsts_dict[timeconsts_keys[np.logical_not(timeconsts_keys<time_con)][0]]


set_command_list = [
    'SCNENBL OFF' #ready scan
    'SCNPAR F', #set freq scan
    'SCNLOG 0',#set linear scan with 0 log scan with 1
    'SCNINRVL 1', #fastest freq scan time update resolution 0 =8ms 2=31ms, 1 = 16ms
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
srs.write('SCNENBL 0')

#set intial lakeshore parameters
parameter_file = open(parameter_path, 'r')
parameters = get_parameters(parameter_file)
ls.write('RAMP 1,0,'+ parameters[0]) #the ramping is intially off
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1]) #this is the starting temp for the ramp
time.sleep(0.05)
ls.write('Range 1,0') #this turns the heater off
time.sleep(0.05)
ls.write('CSET 1,A,1,0,2')# configure loop
time.sleep(0.05)
ls.write('TLIMIT 500')


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
intitial_time = time.perf_counter()#get intitial time
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

        #ramp control
        if parameters[10]:#start/update ramp
            ls.write('PID 1,'+ parameters[7][0]+','+ parameters[7][1]+',' + parameters[7][2])#this sets the setpoint to the final temp
            time.sleep(0.05)
            ls.write('Range 1,1') #this turns the heater to low
            time.sleep(0.05)
            if not(int(ls.query('RAMP? 1')[0])): #if ramp is off, start ramp
                ls.write('RAMP 1,1,'+ parameters[0])
                time.sleep(0.05)
                ls.write('SETP 1,'+ parameters[2])#this sets the setpoint to the final temp
            
        else:#stop ramp
            ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
            time.sleep(0.05)
            ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping
            time.sleep(0.1)
            ls.write('Range 1,0') #this turns the heater off

        srs.write('SCNENBL 0')

        #######################
        # Plotting only temp v time
        #######################

        # update data
        # while idle, want to only update temp v time,

        ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)
        bx.set_title('CurrFreq ='+str(values['freq']),fontsize = 12)
        cx.set_title('Temp Setpoint ='+str(ls.query('SETP? 1'))[1:6],fontsize = 12)

        times = np.append(p1.get_xdata(),values['time'])
        y1 = np.append(p1.get_ydata(),values['Temp'])

        p1.set_xdata(times)
        p1.set_ydata(y1)
        if parameters[8]:
            ax.set_xlim(left = 0, right = values['time'])
            ax.set_ylim(bottom = y1.min(), top = y1.max())
        else:
            if len(parameters[9]) == 2:
                t0 = float(parameters[9][0])
                if t0> times[-1]:
                    t0 = times[-1]-.1
                t1 = float(parameters[9][1])
                inds = np.logical_and(times >= t0, times <= t1)
                ax.set_xlim(left = t0,right = t1)
            elif len(parameters[9]) == 1:
                t0 = float(parameters[9][0])
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

    while parameters[6] == 1: #freq only ramp mode
        srs.write('FREQINT 500 KHZ')
        intiate_scan(srs,500,4000,parameters[5],30,False)
        vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Vmag, freq]
        #print(vs)
        values['Vx'] = float(vs[0])
        values['Vy'] = float(vs[1])
        values['Vmag'] = float(vs[2])
        values['freq'] = float(vs[3])
        p4.set_xdata([values['freq']])
        p5.set_xdata([values['freq']])
        p6.set_xdata([values['freq']])
        p4.set_ydata([values['Vx']])
        p5.set_ydata([values['Vy']])
        p6.set_ydata([values['Vmag']])
        
        srs.write('SCNRUN') #start scan
        time.sleep(0.1)
        freqs = [values['freq']/1000]

        bx.set_title('',fontsize = 12)

        

        
        while srs.query('SCNSTATE?').strip() == '2':#scanning
            
            vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Vmag, freq]
            values['Vx'] = float(vs[0])
            values['Vy'] = float(vs[1])
            values['Vmag'] = float(vs[2])
            values['freq'] = float(vs[3]) 
            R = values['Vmag']*1000 #this is the Voltage Magnitude in mV
            sens_inds = np.logical_not(sens_keys<R)
            range_inds = np.logical_not(input_range_keys<R)
            if np.all(sens_inds == False):
                j = sens_dict[sens_keys[-1]]
            else:
                j = sens_dict[sens_keys[np.logical_not(sens_keys<R)][0]]
            if np.all(sens_inds == False):
                k = input_range_dict[input_range_keys[-1]]
            else:
                k = input_range_dict[input_range_keys[np.logical_not(input_range_keys<R)][0]]

            
            srs.write('IRNG '+str(k))
            srs.write('SCAL '+str(j))
            values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
            values['Temp'] = float(ls.query('KRDG? a')) #temp in K

            #######################
            # Plotting
            #######################

            # update data

            ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)
            cx.set_title('Temp Setpoint ='+str(ls.query('SETP? 1'))[1:6],fontsize = 12)

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
            p1.set_ydata(y1)
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
                if len(parameters[9]) == 2:
                    t0 = float(parameters[9][0])
                    if t0> times[-1]:
                        t0 = times[-1]-.1
                    t1 = float(parameters[9][1])
                    inds = np.logical_and(times >= t0, times <= t1)
                    ax.set_xlim(left = t0,right = t1)
                elif len(parameters[9]) == 1:
                    t0 = float(parameters[9][0])
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

            plt.pause(0.031)

        parameters = get_parameters(parameter_file)
        f_center = p6.get_xdata()[np.argmin(p6.get_ydata()[1:])]
        freqs = np.array(p4.get_xdata())
        R_max  = np.max(p6.get_ydata()[np.logical_and(freqs>=f_center-parameters[4]/2, freqs<=f_center+parameters[4]/2)])
        j = sens_dict[sens_keys[np.logical_not(sens_keys<R_max)][0]]
        k = input_range_dict[input_range_keys[np.logical_not(input_range_keys<R_max)][0]]
        srs.write('IRNG '+str(k))
        srs.write('SCAL '+str(j))
        #start temp scan
        if parameters[6] == 1: #allow for manual change of status
            change_status(2,parameter_file)
            parameters = get_parameters(parameter_file)
            srs.write('SCNENBL 0')
            print('Switching to Temp Ramp')

    while parameters[6] == 2: #temp ramp mode
        try:
            if not(f_center-parameters[4]/2>=0 and f_center+parameters[4]/2<=4000):#check if the freq scan will be valid
                change_status(1,parameter_file)
                parameters = get_parameters(parameter_file)
                time.sleep(.1)
                raise Exception('f_center is not in range [0,4MHz]\nAttempting to refind f_center')
    

            parameters = get_parameters(parameter_file)

            #ramp control
            if parameters[10]:#start/update ramp
                ls.write('PID 1,'+ parameters[7][0]+','+ parameters[7][1]+',' + parameters[7][2])#this sets the setpoint to the final temp
                time.sleep(0.05)
                ls.write('Range 1,1') #this turns the heater to low
                time.sleep(0.05)
                if not(int(ls.query('RAMP? 1')[0])): #if ramp is off, start ramp
                    ls.write('RAMP 1,1,'+ parameters[0])
                    time.sleep(0.05)
                    ls.write('SETP 1,'+ parameters[2])#this sets the setpoint to the final temp
                
            else:#stop ramp
                ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
                time.sleep(0.05)
                ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping
                time.sleep(0.1)
                ls.write('Range 1,0') #this turns the heater off

            buffer_file = open(os.path.join(save_path, "buffer.dat"), "w+")
            sweep_num += 1 #this will help identify sweeps from each other
            sweep_str = str(sweep_num)

            if parameters[11]:
                intiate_scan(srs,f_center-parameters[4]/2,f_center-parameters[12]/2,parameters[5],parameters[3]/3,False)
                srs.write('SCNRUN') #start scan
                
                while srs.query('SCNSTATE?').strip() == '2':#scanning
                    vs = srs.query('SNAPD?').split(',') 
                    write_str = '\t'.join((str((time.perf_counter()-intitial_time)/60),  str(float(ls.query('KRDG? a'))), vs[0], vs[1], vs[2], vs[3][:-1], sweep_str))+"\n"
                    save_file.write(write_str)
                    save_file.flush()
                    buffer_file.write(write_str)
                    buffer_file.flush()

                intiate_scan(srs,f_center-parameters[12]/2,f_center+parameters[12]/2,parameters[5],parameters[3]/3,False)
                srs.write('SCNRUN') #start scan
                
                while srs.query('SCNSTATE?').strip() == '2':#scanning
                    vs = srs.query('SNAPD?').split(',') 
                    write_str = '\t'.join((str((time.perf_counter()-intitial_time)/60),  str(float(ls.query('KRDG? a'))), vs[0], vs[1], vs[2], vs[3][:-1], sweep_str))+"\n"
                    save_file.write(write_str)
                    save_file.flush()
                    buffer_file.write(write_str)
                    buffer_file.flush()
                
                intiate_scan(srs,f_center+parameters[12]/2,f_center+parameters[4]/2,parameters[5],parameters[3]/3,False)
                srs.write('SCNRUN') #start scan
                
                while srs.query('SCNSTATE?').strip() == '2':#scanning
                    vs = srs.query('SNAPD?').split(',') 
                    write_str = '\t'.join((str((time.perf_counter()-intitial_time)/60),  str(float(ls.query('KRDG? a'))), vs[0], vs[1], vs[2], vs[3][:-1], sweep_str))+"\n"
                    save_file.write(write_str)
                    save_file.flush()
                    buffer_file.write(write_str)
                    buffer_file.flush()

            else:

                intiate_scan(srs,f_center-parameters[4]/2,f_center+parameters[4]/2,parameters[5],parameters[3],False)
                srs.write('SCNRUN') #start scan
                
                while srs.query('SCNSTATE?').strip() == '2':#scanning
                    vs = srs.query('SNAPD?').split(',') 
                    write_str = '\t'.join((str((time.perf_counter()-intitial_time)/60),  str(float(ls.query('KRDG? a'))), vs[0], vs[1], vs[2], vs[3][:-1], sweep_str))+"\n"
                    save_file.write(write_str)
                    save_file.flush()
                    buffer_file.write(write_str)
                    buffer_file.flush()
                
            srs.write('SCNENBL 0')
            parameters = get_parameters(parameter_file)

            #ramp control
            if parameters[10]:#start/update ramp
                ls.write('PID 1,'+ parameters[7][0]+','+ parameters[7][1]+',' + parameters[7][2])#this sets the setpoint to the final temp
                time.sleep(0.05)
                ls.write('Range 1,1') #this turns the heater to low
                time.sleep(0.05)
                if not(int(ls.query('RAMP? 1')[0])): #if ramp is off, start ramp
                    ls.write('RAMP 1,1,'+ parameters[0])
                    time.sleep(0.05)
                    ls.write('SETP 1,'+ parameters[2])#this sets the setpoint to the final temp
                
            else:#stop ramp
                ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
                time.sleep(0.05)
                ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping
                time.sleep(0.1)
                ls.write('Range 1,0') #this turns the heater off

            #this part can afford to be slower because it is called 300x less

            #######################
            # Retrieve Data
            #######################
            buffer_file.seek(0) #resets pointer to top of the file
            lines = buffer_file.readlines()
            buffer_file.close()
            new_data = [[],[],[],[],[],[]]#[time,temp,vx,vy,vmag,freq]
            for line in lines:
                data = line.split()
                if int(data[-1]) == sweep_num:
                    for i, dat in enumerate(data[:-1]):
                        new_data[i].append(float(dat))
            new_data= np.array(new_data)

            #######################
            # fitting
            #######################
            plot_freqs = new_data[5]/1000
            plot_vmags = new_data[4]*1000

            guesses1 = [plot_freqs[np.argmin(plot_vmags)],30,400,400,.1,-.4]
            pbounds1 = np.array([[min(plot_freqs),1,-.5e3,0,-1,-1],[max(plot_freqs),200,.5e3,.5e3,1,1]]) # [[Lower bounds],[upper bounds]]
            bestfit = optimize.curve_fit(full_lorenzian_fit_with_skew,plot_freqs,plot_vmags,guesses1, bounds=pbounds1)
            bestpars = bestfit[0]

            f_center = bestpars[0]
            srs.write('FREQINT '+str(round((f_center-parameters[4]/2),0))+ ' KHZ')
            #######################
            # Plotting
            #######################
            #append time data
            ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)
            cx.set_title('Temp Setpoint ='+str(ls.query('SETP? 1'))[1:6],fontsize = 12)

            times = np.append(p1.get_xdata(),new_data[0])
            y1 = np.append(p1.get_ydata(),new_data[1])
            p1.set_xdata(times)
            p1.set_ydata(y1)

            #show voltage for previous scan
            p4.set_xdata(plot_freqs)
            p5.set_xdata(plot_freqs)
            p6.set_xdata(plot_freqs)
            p4.set_ydata(1000*new_data[2])
            p5.set_ydata(1000*new_data[3])
            p6.set_ydata(plot_vmags)

            #Q factor and res freq data
            if sweep_num == 1:
                p2.set_xdata([(T_avg := np.average(new_data[1]))])
                p3.set_xdata([T_avg])
                p2.set_ydata([bestpars[0]])
                p3.set_ydata([bestpars[1]])
            else:
                p2.set_xdata(np.append(p2.get_xdata(),(T_avg := np.average(new_data[1]))))
                p3.set_xdata(np.append(p3.get_xdata(),T_avg))
                p2.set_ydata(np.append(p2.get_ydata(),bestpars[0]))
                p3.set_ydata(np.append(p3.get_ydata(),bestpars[1]))
            

            #update limits
            bx.set_xlim(left = y1.min(), right = y1.max())
            cx.set_xlim(left = y1.min(), right = y1.max())
            bx.set_ylim(bottom = np.min(p2.get_ydata()), top = np.max(p2.get_ydata()))
            cx.set_ylim(bottom = np.min(p3.get_ydata()), top = np.max(p3.get_ydata()))
            dx.set_xlim(left = plot_freqs[0], right = plot_freqs[-1])
            ex.set_xlim(left = plot_freqs[0], right = plot_freqs[-1])
            fx.set_xlim(left = plot_freqs[0], right = plot_freqs[-1])
            dx.set_ylim(bottom = 1000*np.min(new_data[2]), top = 1000*np.max(new_data[2]))
            ex.set_ylim(bottom = 1000*np.min(new_data[3]), top = 1000*np.max(new_data[3]))
            fx.set_ylim(bottom = np.min(plot_vmags), top = np.max(plot_vmags))
            if parameters[8]:
                ax.set_xlim(left = 0, right = times[-1])
                ax.set_ylim(bottom = y1.min(), top = y1.max())
            else:
                if len(parameters[9]) == 2:
                    t0 = float(parameters[9][0])
                    if t0> times[-1]:
                        t0 = times[-1]-.5
                    t1 = float(parameters[9][1])
                    inds = np.logical_and(times >= t0, times <= t1)
                    ax.set_xlim(left = t0,right = t1)
                elif len(parameters[9]) == 1:
                    t0 = float(parameters[9][0])
                    if t0> times[-1]:
                        t0 = times[-1]-.5
                    inds = np.logical_not(times<t0)
                    ax.set_xlim(left = t0,right = times[-1])
                else:
                    inds = np.logical_not(times<0)
                    ax.set_xlim(left = 0, right = times[-1])
                ax.set_ylim(bottom = y1[inds].min(), top = y1[inds].max())

            plt.pause(0.1)#show plot

        except Exception as error:
            parameters = get_parameters(parameter_file)
            print('Error: '+str(error))
            traceback.print_exc()
            if parameters[6] == 2:
                change_status(1,parameter_file)
                parameters = get_parameters(parameter_file)
                time.sleep(.1)

        

#######################
# Close Instruments
#######################
ls.write('RAMP 1,0,'+ parameters[0])#turn off ramping
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1]) #set temp back to start
time.sleep(0.05)
ls.write('Range 1,0') #this turns the heater off
time.sleep(0.05)
srs.write('SCNENBL 0')
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