import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import os
import warnings
from scipy.optimize import curve_fit

def get_parameters(f):
    try:
        f.seek(0) #resets pointer to top of the file
        lines = f.readlines()
        lines[6] = lines[6].split()
        lines[6].pop(0) #this removes the word, but still returns a list
        return (lines[0].split()[1],#RampRate
                lines[1].split()[1],#StartTemp
                lines[2].split()[1],#FinalTemp
                int(lines[3].split()[1]),#RampingStatus
                [lines[4].split()[1],lines[4].split()[2],lines[4].split()[3]],#PID paratmeters
                int(lines[5].split()[1]),#Autoscale boolean
                lines[6]) #time scale
    except:
        print('Error Reading Parameters: Edit parameters.txt or redownload it from https://github.com/wendl198/ContactlessProbe.')
        print('Warning: Data is no longer being recorded.')
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
    del file1, lines
    #status is an integer [0,2]
    # No Ramp = 0
    # StartRamp = 1
    # Stop = 2

#######################
# Cooling Time Prediction
#######################

def model(x,a,b):
    return a*np.exp(x*b)+77.3 # a>0, and b<0 when cooling
parameterlowerbounds1 = np.array([0,-1e1]) # a is the intial temp value - 78 when t=0
parameterupperbounds1 = np.array([3e2,0])
pbounds1 = np.array([parameterlowerbounds1,parameterupperbounds1])
def guess_cool_time(t,T):
    bestfit = curve_fit(model,t-t[0],T,[T[0]-77.3,-1e-1],bounds=pbounds1) #t must be numpy array
    bestpars1 = bestfit[0]
    # parametererr = np.sqrt(np.diag(bestfit[1]))
    #what to find t_0 in T_final = a * e^(b*t_0) + 77.3
    #t_o=ln[(T_final-77.3)/a]/b
    del bestfit, t, T
    #print(bestpars1)
    return str(np.log((78-77.3)/bestpars1[0])/bestpars1[1])#time til 78K prediction


save_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\RawData'
parameter_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\parameters.txt'
default_path = 'C:\\Users\\mpms\\Desktop\\Contactless Probe\\default_parameters.txt'


# save_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData'
# parameter_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/parameters.txt'
# default_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/default_parameters.txt'

fit_points = 10 # number of data points that are fitted while cooling
pause_time = .5 #time in sec

#######################
# Open Files
#######################
save_file = open(os.path.join(save_path, input("Please type the file name here: ") + ".dat"), "a")
save_file.write("Time (min)" + "\t" + "T (K)" + "\t" + "Vx (V)" + "\t" + "Vy (V)"+"\n")
parameter_file = open(parameter_path, 'r')
#the idea is to keep the files open, to avoid constant opening and closing. Use .flush() to save data

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
ls.write('SETP 1,'+ parameters[1])

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
bx.set_xlabel('Time (min)')
bx.set_ylabel('Heater Percent (%)')
cx.set_xlabel('Time (min)')
cx.set_ylabel('Vx (mV)')
dx.set_xlabel('Time (min)')
dx.set_ylabel('Vy (mV)')

p1, = ax.plot(0,float(ls.query('KRDG? a')),'ko-')
p2, = bx.plot(0,float(ls.query('HTR? 1')),'ro-')
vs = srs.query('SNAPD?').split(',')
p3, = cx.plot(0,1000*float(vs[0]),'bo-') #plot in mV
p4,= dx.plot(0,1000*float(vs[1]),'go-')
del vs

values = {}
intitial_time = time.perf_counter()#get intitial time

T_min = np.inf
T_max = -1
h_min = np.inf
h_max = -1
vx_min = np.inf
vx_max = -2
vy_min = np.inf
vy_max = -2 


#######################
# Main Loop
#######################

while parameters[3] < 2:
    ########################
    # Update Parameters
    ########################
    del parameters #all local variables are deleted to prevent data pileup in secondary memory that slow processes down
    parameters = get_parameters(parameter_file)

    values['time'] = (time.perf_counter()-intitial_time)/60 #The time is now in minutes
    values['Temp'] = float(ls.query('KRDG? a')) #temp in K
    values['heater'] = float(ls.query('HTR? 1')) #this is the percentage of the heater
    vs = srs.query('SNAPD?').split(',') #this is [Vx, Vy, Resistance, Theta]
    values['Vx'] = float(vs[0])
    values['Vy'] = float(vs[1])
    del vs

    # update y axis limits
    if T_min > values['Temp']:
        del T_min
        T_min = values['Temp']
    elif T_max < values['Temp']:
        del T_max
        T_max = values['Temp']

    if h_min > values['heater']:
        del h_min
        h_min = values['heater']
    elif h_max < values['heater']:
        del h_max
        h_max = values['heater']

    if vx_min > values['Vx']:
        del vx_min
        vx_min = values['Vx']
    elif vx_max < values['Vx']:
        del vx_max
        vx_max = values['Vx']

    if vy_min > values['Vy']:
        del vy_min
        vy_min = values['Vy']
    elif vy_max < values['Vy']:
        del vy_max
        vy_max = values['Vy']

    ########################
    # Update Ramping Status
    ########################

    if parameters[3] == 0: #no ramp
        ls.write('RAMP 1,0,'+ parameters[0])# Turns off ramping
        time.sleep(0.05)
        ls.write('SETP 1,'+ parameters[1])# intializes temperature for ramping

        #next part is optional
        if values['Temp'] > 780:
            t = p1.get_xdata()
            if len(t)>fit_points+1:
                ax.legend().set_visible(True)
                ax.legend(['78k in ' + guess_cool_time(t[-fit_points:],p1.get_ydata()[-fit_points:]) + ' mins'])
            del t

    elif parameters[3] == 1: #ramp mode
        #ax.legend().set_visible(False)
        ls.write('RAMP 1,1,'+ parameters[0])
        time.sleep(0.05)
        ls.write('SETP 1,'+ parameters[2])#this sets the setpoint to the final temp
        time.sleep(0.05)
        ls.write('PID 1,'+ parameters[4][0]+','+ parameters[4][1]+',' + parameters[4][2])#this sets the setpoint to the final temp
    
    #######################
    # Plotting
    #######################

    # ax.plot(values['time'],values['Temp'],'ko--')
    # bx.plot(values['time'],values['heater'],'ro--')
    # cx.plot(values['time'],1000*values['Vx'],'bo--') #plot in mV
    # dx.plot(values['time'],1000*values['Vy'],'go--')

    p1.set_xdata(np.append(p1.get_xdata(),values['time']))
    p1.set_ydata(np.append(p1.get_ydata(),values['Temp']))
    p2.set_xdata(np.append(p2.get_xdata(),values['time']))
    p2.set_ydata(np.append(p2.get_ydata(),values['heater']))
    p3.set_xdata(np.append(p3.get_xdata(),values['time']))
    p3.set_ydata(np.append(p3.get_ydata(),1000*values['Vx']))
    p4.set_xdata(np.append(p4.get_xdata(),values['time']))
    p4.set_ydata(np.append(p4.get_ydata(),1000*values['Vy']))

    if parameters[5]:
        ax.set_xlim(left = 0, right = values['time'])
        bx.set_xlim(left = 0, right = values['time'])
        cx.set_xlim(left = 0, right = values['time'])
        dx.set_xlim(left = 0, right = values['time'])
    else:
        if len(parameters[6]) == 2:
            ax.set_xlim(left = float(parameters[6][0]),right = float(parameters[6][1]))
            bx.set_xlim(left = float(parameters[6][0]),right = float(parameters[6][1]))
            cx.set_xlim(left = float(parameters[6][0]),right = float(parameters[6][1]))
            dx.set_xlim(left = float(parameters[6][0]),right = float(parameters[6][1]))
        elif len(parameters[6]) == 1:
            ax.set_xlim(left = float(parameters[6][0]),right = values['time'])
            bx.set_xlim(left = float(parameters[6][0]),right = values['time'])
            cx.set_xlim(left = float(parameters[6][0]),right = values['time'])
            dx.set_xlim(left = float(parameters[6][0]),right = values['time'])
        else:
            ax.set_xlim(left = 0, right = values['time'])
            bx.set_xlim(left = 0, right = values['time'])
            cx.set_xlim(left = 0, right = values['time'])
            dx.set_xlim(left = 0, right = values['time'])
    warnings.filterwarnings("ignore") #often the bounds of the heater are [0,0], this shuts up the warning
    ax.set_ylim(bottom = T_min, top = T_max)
    bx.set_ylim(bottom = h_min, top = h_max)
    cx.set_ylim(bottom = 1000*vx_min, top = 1000*vx_max)
    dx.set_ylim(bottom = 1000*vy_min, top = 1000*vy_max)

    ax.set_title('CurrTemp ='+str(values['Temp']),fontsize = 12)
    bx.set_title('Setpoint ='+str(ls.query('SETP? 1'))[1:6],fontsize = 12)
   
    plt.pause(pause_time) #this displays the graph

    #######################
    # Save Data
    #######################

    save_file.write(str(values['time']) + "\t" +  str(values['Temp']) + "\t" + str(values['Vx']) + "\t" + str(values['Vy'])+"\n")
    save_file.flush()#this will save the data without closing the file

    #check if final temp is reached
    if float(parameters[2]) <= values['Temp']:
        change_status(0,parameter_file) #stop ramping, but still collect data

    del values['time'],values['Temp'],values['Vx'],values['Vy'],values['heater']#,values['T_sample'],values['R'],values['Th'], values['V_total']


#######################
# Close Instruments
#######################
ls.write('RAMP 1,0,'+ parameters[0])#turn off ramping
time.sleep(0.05)
ls.write('SETP 1,'+ parameters[1]) #set temp back to start
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
