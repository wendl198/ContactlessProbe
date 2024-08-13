#this program is for MMPS data v contactless probe data comparision

import numpy as np
import matplotlib.pyplot as plt

mpms_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/2023_4_2_polished_more.dc.dat'
probe_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/2023_4_2_3.dat'
probe_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/empty_6_6_23.dat'

all_data1 = np.genfromtxt(mpms_path,delimiter=',')
# t1 = np.array(all_data[1:,0])
# field = np.array(all_data1[1:,2])
last= np.argmax(all_data1[:-2,3])

T1 = np.array(all_data1[:last,3])
ind1 = np.logical_and(T1 >= 70, T1 <= 105)
T1 = T1[ind1]
moment = np.array(all_data1[0:last,4])
moment = moment[ind1]



all_data2 = np.genfromtxt(probe_path, delimiter='\t')
indexes = np.logical_and(all_data2[:,1] >= T1.min(), all_data2[:,1] <= 105)
t2 = np.array(all_data2[indexes,0])
T2 = np.array(all_data2[indexes,1])
x = np.array(all_data2[indexes,2])*1000
y = np.array(all_data2[indexes,3])*1000
dT2 = np.zeros(len(T2))
for i in range(1,len(T2)):
    dT2[i] = T2[i]-T2[i-1]

# ind2 = np.logical_and(T2 >= 77.3, dT2 > 0)
ind2 = np.logical_and(t2 >= 44, t2 <= 69)
ind3 = np.logical_and(t2 >= 197, t2 <= 244)
ind4 = np.logical_and(t2 >= 156, t2 <= 170)
ind5 = np.logical_and(t2 >= 92, t2 <= 116)

ind6 = np.logical_and(t2 >= 69, t2 <= 92)
ind7 = np.logical_and(t2 >= 116, t2 <= 156)
ind8 = np.logical_and(t2 >= 170, t2 <= 197)

steel_phase = 0
phase = np.arctan(y/x)-steel_phase

# fig = plt.figure(constrained_layout = True)
# ax = fig.add_subplot(2, 1, 1)
# bx = fig.add_subplot(2, 1, 2)
# ax.plot(T1,moment)
# ax.set_ylabel('Long Moment [emu]',fontsize = 15)
# ax.set_xlabel('Temperature [K]',fontsize = 15)
# ax.set_title('MPMS Data')
# # ax.legend(['Temp Data'])
# bx.plot(T2[ind2],phase[ind2],color='orange')
# bx.set_xlabel('Temperature [K]',fontsize = 15)
# bx.set_ylabel('Phase [rad]',fontsize = 15)
# bx.set_title('Calibration Measurement')
# bx.legend(['Vx','Vy'])

fig = plt.figure(constrained_layout = True)
ax = fig.add_subplot(1, 1, 1)
ax.scatter(T1,moment,color='blue')
ax.set_ylabel(r'Magnetic Susceptibility $\chi_{DC}$ [A.U.]',fontsize = 15)
ax.set_xlabel('Temperature [K]',fontsize = 15)
bx = ax.twinx()
bx.scatter(99.4,1.428,color='blue')
bx.plot(T2[ind3],phase[ind3],color='green')
bx.plot(T2[ind5],phase[ind5],color='orange')
bx.plot(T2[ind4],phase[ind4],color='red')
# bx.plot(T2[ind6],phase[ind6],color='yellow')
# bx.plot(T2[ind5],phase[ind5],color='purple')
bx.set_xlabel('Temperature [K]',fontsize = 15)
bx.set_ylabel('Phase [AU]',fontsize = 15)
bx.set_title('Calibration Measurement')
bx.legend(['SQUID Data',r'Ramp Rate = 0.5 $\frac{K}{min}$',r'Ramp Rate = 1 $\frac{K}{min}$',r'Ramp Rate = 2 $\frac{K}{min}$'])

# fig2 = plt.figure(constrained_layout = True)

# cx = fig2.add_subplot(1, 1, 1)
# cx.scatter(T2[ind2],x[ind2],color='red')
# cx2 = cx.twinx()
# cx2.scatter(T2[ind2],y[ind2],color = 'blue')

# cx.legend(['Vx'])
# cx2.legend(['Vy'])

# cx.plot(t2[ind2],x[ind2])




fig3 = plt.figure(constrained_layout = True)
dx = fig3.add_subplot(1, 1, 1)
dx.scatter(t2,T2)

fig4 = plt.figure(constrained_layout = True)
ex = fig4.add_subplot(1, 1, 1)

ex.set_ylabel(r'Derivative of Magnetic Susceptibility $\chi_{DC}$ [A.U.]',fontsize = 15)
ex.set_xlabel('Temperature [K]',fontsize = 15)
fx = ex.twinx()
fx.scatter(99.4,-1.4e-4,color='blue')
fx.scatter(T2[ind4],np.gradient(phase[ind4]),color='red',s=1)
fx.scatter(T2[ind5],np.gradient(phase[ind5]),color='orange',s=1)
fx.scatter(T2[ind3],np.gradient(phase[ind3]),color='green',s=1)


fx.set_xlabel('Temperature [K]',fontsize = 15)
fx.set_ylabel('Derivative of Phase [AU]',fontsize = 15)
fx.set_title('Calibration Measurement')
fx.legend(['MPMS Data',r'Ramp Rate = 2 $\frac{K}{min}$',r'Ramp Rate = 1 $\frac{K}{min}$',r'Ramp Rate = 0.5 $\frac{K}{min}$'])
ex.scatter(T1,np.gradient(moment),color='blue')
ex.plot(T1,np.gradient(moment),color='blue')
fx.set_ylim(-1e-4,8.5e-4)
fx.set_xlim(77,97)
ex.set_xlim(77,97)

plt.show()