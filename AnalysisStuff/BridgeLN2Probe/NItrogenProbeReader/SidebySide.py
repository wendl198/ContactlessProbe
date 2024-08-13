import numpy as np
import matplotlib.pyplot as plt

#####################
# Import Data
#####################
path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/'
path_suffix = '.dat'
# filenames = ['EmptyCal7_25',
#              'Empty_cal_7_25_2',
#              'Empty_Cal_7_26',
#              "Empty_Cal_7_27'",
#              'Empty_Cal_7_28'
# ]

filenames = ['Empty_Cal_7_26',
             "Empty_Cal_7_27'",
             'Empty_Cal_7_28',
             'Empty_Cal_7_30'
]
# filenames = ['Empty_Cal_7_26','BW71_1_2']

#collect data
all_data = []
for i, file in enumerate(filenames):
    data = np.genfromtxt(path_prefix + file+ path_suffix, delimiter='\t')
    all_data.append([np.array(data[1:,0]),
                   np.array(data[1:,1]),
                   np.array(data[1:,2])*1000,
                   np.array(data[1:,3])*1000
                   ])#[time,temp,Vx,Vy]

# temp and time filtering
Tmin = 0    #lower temp bound
Tmax = 300  #upper temp bound
tmin = 0    #lower time bound
tmax = 1500 #upper time bound
for i, data in enumerate(all_data):
    Ti = np.logical_and(data[1]>Tmin, data[1]<Tmax)
    ti = np.logical_and(data[0]>tmin, data[0]<tmax)
    indexes = Ti*ti
    all_data[i][0] = data[0][indexes]
    all_data[i][1] = data[1][indexes]
    all_data[i][2] = data[2][indexes]
    all_data[i][3] = data[3][indexes]




# Voltage v time (custom time)
fig1 = plt.figure(constrained_layout = True)
ax = fig1.add_subplot(3, 1, 2)
bx = fig1.add_subplot(3, 1, 3)
for data in all_data:
    ax.scatter(data[0],data[2])
    bx.scatter(data[0],data[3])
ax.set_xlabel('Time (min)')
bx.set_xlabel('Time (min)')
ax.set_ylabel('Vx (mV)')
bx.set_ylabel('Vy (mV)')
ax.legend(filenames)
bx.legend(filenames)

cx = fig1.add_subplot(3, 1, 1)
for data in all_data:
    cx.scatter(data[0],data[1])
cx.set_xlabel('Time (min)')
cx.set_ylabel('Temperature (K)')
cx.legend(filenames)

#Phase v time
# fig2= plt.figure(constrained_layout = True)
# dx = fig2.add_subplot(1, 1, 1)
# for data in all_data:
#     dx.scatter(data[0],np.angle(data[2]+1j*data[3]))
# dx.set_xlabel('Time (min)')
# dx.set_ylabel('Phase (K)')
# dx.legend(filenames)

plt.show()