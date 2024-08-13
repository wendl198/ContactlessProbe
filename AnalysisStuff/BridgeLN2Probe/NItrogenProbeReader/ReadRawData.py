import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#####################
# Import Data
#####################
path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/'
path_suffix = '.dat'
filename = "BW88_3"
filename = 'BW88_3with101cap'

data_path = path_prefix + filename + path_suffix

# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/emptytest2.1.dat'
# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/emptytest2.dat'
# data_path = 'C:\\Users\\blake\\Downloads\\Empty.xlsx'
# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/emptytest5.dat'
# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/newcoiltemp.dat'
# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/pid3.dat'
# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/4-14-23.dat'
# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/4-13-23.dat'
# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/empty_6_6_23.dat'
# data_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/KTO_110_B5_1.dat'



# probe_dat = pd.read_excel(data_path) #Retrieve data
# dat = probe_dat.to_numpy() 

# T = dat[:,0]
# x = dat[:,1]
# y = dat[:,3]
# input()

all_data = np.genfromtxt(data_path, delimiter='\t')
t = np.array(all_data[1:,0])
T = np.array(all_data[1:,1])
x = np.array(all_data[1:,2])*1000
y = np.array(all_data[1:,3])*1000

# remove 0 temp terms
a = 0 #lower bound
b = 300 #upper temp bound
indexes = np.logical_and(T >= a, T <= b)
t = t[indexes]
T = T[indexes]
x = x[indexes]
y = y[indexes]

indexes = np.logical_and(t >= 0, t <= 10000)
t = t[indexes]
T = T[indexes]
x = x[indexes]
y = y[indexes]


#for FullTest1.dat
# all_data = [[],[],[],[]]
# for line in open(data_path, 'r'):
#     if line.split()[0] != 'Time':
#         for i in range(4):
#             all_data[i].append(float(line.split()[i]))
# t = np.array(all_data[0])/60 
# T = np.array(all_data[1])
# x = np.array(all_data[2])*1000
# y = np.array(all_data[3])*1000



#####################
# Calculations
#####################

first = np.argmin(T[np.logical_not(T==0)]) # this is the index of the point when the heater turns on for the first time
# first = np.argmax(T)
# first = 0
x_avg = sum(x[first:])/len(x[first:])
y_avg = sum(y[first:])/len(y[first:])
x_err = np.std(x[first:])
y_err = np.std(y[first:])
# print('x',x_avg,x_err)
# print('y',y_avg,y_err)


#####################
# Plotting
#####################

## Full Data Set
# fig = plt.figure(constrained_layout = True)
# ax = fig.add_subplot(2, 1, 1)
# bx = fig.add_subplot(2, 1, 2)
# ax.plot(t,T)
# ax.set_xlabel('Time [min]',fontsize = 15)
# ax.set_ylabel('Temperature [K]',fontsize = 15)
# ax.set_title('Temp')
# ax.legend(['Temp Data'])
# bx.plot(t,x)
# bx.plot(t,y)
# bx.set_xlabel('Time [min]',fontsize = 15)
# bx.set_ylabel('Voltage [mV]',fontsize = 15)
# bx.set_title('Calibration Measurement')
# bx.legend(['Vx','Vy'])
# plt.show()

## Start at min temp
# fig = plt.figure(constrained_layout = True)
# ax = fig.add_subplot(2, 1, 1)
# bx = fig.add_subplot(2, 1, 2)
# ax.plot(t[first:],T[first:])
# ax.set_xlabel('Time [min]',fontsize = 15)
# ax.set_ylabel('Temperature [K]',fontsize = 15)
# ax.set_title('Temp')
# ax.legend(['Temp Data'])
# bx.plot(t[first:],x[first:]-x_avg)
# bx.plot(t[first:],y[first:]-y_avg)
# bx.set_xlabel('Time [min]',fontsize = 15)
# bx.set_ylabel('Voltage [mV]',fontsize = 15)
# bx.set_title('Voltage Signal')
# bx.legend(['Vx','Vy'])

## Seprate plots for Vx and Vy with average
# fig = plt.figure(constrained_layout = True)
# ax = fig.add_subplot(3, 1, 1)
# bx = fig.add_subplot(3, 1, 2)
# cx = fig.add_subplot(3, 1, 3)
# ax.plot(t[first:],T[first:])
# ax.set_xlabel('Time [min]',fontsize = 15)
# ax.set_ylabel('Temperature [K]',fontsize = 15)
# ax.set_title('Temp')
# bx.plot(t[first:],x[first:]-x_avg)
# bx.set_xlabel('Time [min]',fontsize = 15)
# bx.set_ylabel('X Voltage [mV]',fontsize = 15)
# bx.legend(['Avg = '+str(x_avg)])
# cx.plot(t[first:],y[first:]-y_avg)
# cx.set_xlabel('Time [min]',fontsize = 15)
# cx.set_ylabel('Y Voltage [mV]',fontsize = 15)
# cx.legend(['Avg = '+str(y_avg)])
# plt.show()

## No temp plot
# fig = plt.figure(constrained_layout = True)
# ax = fig.add_subplot(2, 1, 1)
# bx = fig.add_subplot(2, 1, 2)
# ax.plot(T[first:],x[first:]-x_avg)
# ax.set_xlabel('Time [min]',fontsize = 15)
# ax.set_ylabel('X Voltage [mV]',fontsize = 15)
# ax.legend(['Avg = '+str(x_avg)])
# bx.plot(T[first:],y[first:]-y_avg)
# bx.set_xlabel('Time [min]',fontsize = 15)
# bx.set_ylabel('Y Voltage [mV]',fontsize = 15)
# bx.legend(['Avg = '+str(y_avg)])
# plt.show()

#simple voltage v temp display
# fig = plt.figure(constrained_layout = True)
# # ax = fig.add_subplot(2, 1, 1)
# bx1 = fig.add_subplot(1, 1, 1)
# # ax.plot(t[first:],T[first:])
# # ax.set_xlabel('Time [min]',fontsize = 15)
# # ax.set_ylabel('Temperature [K]',fontsize = 15)
# bx1.set_title('Voltage Noise Dependance on Temperature',fontsize = 18)
# bx1.scatter(T[first:],x[first:],color='red',s=7)
# bx1.set_xlabel('Temperature [K]',fontsize = 15)
# bx1.set_ylabel('X Voltage [mV]',fontsize = 15)
# bx2 = bx1.twinx()
# bx2.scatter(T[first:],y[first:],color='blue',s=7)
# bx2.set_ylabel('Y Voltage [mV]',fontsize = 15)
# bx1.legend(['Vx'])
# bx2.legend(['Vy'])

# plt.show()


#Phase v time (custom time)
inds = np.logical_and(t >0, t<980)
fig2= plt.figure(constrained_layout = True)
cx = fig2.add_subplot(1, 1, 1)
cx.plot(t[inds],np.angle(x[inds]+1j*y[inds]))
cx.set_xlabel('Time [min]',fontsize = 15)
cx.set_ylabel('Phase [K]',fontsize = 15)

# Voltage v time (custom time)
fig3 = plt.figure(constrained_layout = True)
inds2 = np.logical_and(t >50, t<980)
ax = fig3.add_subplot(1, 1, 1)
bx = ax.twinx()
ax.scatter(t[inds2],x[inds2])
ax.scatter(t[inds2][0],x[inds2][0],color= 'orange')
ax.set_xlabel('Time [min]',fontsize = 15)
ax.set_ylabel('X Voltage [mV]',fontsize = 15)
ax.legend(['Vx','Vy'])
bx.scatter(t[inds2],y[inds2],color='orange')
bx.set_ylabel('Y Voltage [mV]',fontsize = 15)

fig4 = plt.figure(constrained_layout = True)
dx = fig4.add_subplot(1, 1, 1)
dx.scatter(t[inds2],T[inds2])
dx.set_xlabel('Time [min]',fontsize = 15)
dx.set_ylabel('Temperature (K)',fontsize = 15)
plt.show()