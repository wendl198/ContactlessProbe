import numpy as np
import matplotlib.pyplot as plt
import os

#####################
# Import Data
#####################
path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/'
path_prefix += 'HeProbe/'
path_suffix = '.dat'

# filename1 = 'double3.9nf'
# filename1 = 'double.47nf'
# filename1 = 'double1nf'
# path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/InitialRandomTesting/' #folder to open all files in
# filenames = os.listdir(path_prefix)
# path_suffix = ''

# filenames = [
#              'double1nf',
#             #  'double.47nf',
#             #  'double3.9nf',
#             #  '.5nfseries1nfparallel',
#             #  '2nfserise1nfparallel2',
#             #  '1nfseries3.9nfparallel'
#               ]
filenames = ['STOColdTestCalibrated3']
data_paths = []
for f in filenames:
    data_paths.append(path_prefix + f + path_suffix)
# data_path1 = path_prefix + filename1 + path_suffix

# filename1 = '.5nfseries1nfparallel'
# 
# data_path1 = path_prefix + filename1 + path_suffix
# filename2 = '2nfserise1nfparallel2'
# data_path2 = path_prefix + filename2 + path_suffix
datas = []
for i, data in enumerate(data_paths):
    all_data = np.genfromtxt(data, delimiter='\t')
    datas.append({})
    datas[i]['time'] = np.array(all_data[2:,0])
    datas[i]['vx'] = 1-np.array(all_data[2:,1])*1000/100 #Switching from reflected to transmitted voltage
    datas[i]['vy'] = -np.array(all_data[2:,2])*1000/100 #Switching from reflected to transmitted voltage
    datas[i]['vmag'] = np.array(all_data[2:,3])*1000
    datas[i]['freq'] = np.array(all_data[2:,4])/1000

# all_data2 = np.genfromtxt(data_path2, delimiter='\t')
# t2 = np.array(all_data2[2:,0])
# x2 = np.array(all_data2[2:,1])*1000
# y2 = np.array(all_data2[2:,2])*1000
# R2 = np.array(all_data2[2:,3])*1000
# freq2 = np.array(all_data2[2:,4])/1000


fig1 = plt.figure(constrained_layout = True)
ax = fig1.add_subplot(3, 1, 1)
bx = fig1.add_subplot(3, 1, 2)
cx = fig1.add_subplot(3, 1, 3)
for dat in datas:
    ax.scatter(dat['freq'],dat['vx'])
    bx.scatter(dat['freq'],dat['vy'])
    cx.scatter(dat['freq'],dat['vmag'])
ax.set_xlabel('Frequency (kHz)')
bx.set_xlabel('Frequency (kHz)')
cx.set_xlabel('Frequency (kHz)')
ax.set_ylabel('Vx (mV)')
bx.set_ylabel('Vy (mV)')
cx.set_ylabel('Voltage Magnitude (mV)')
ax.legend(filenames)
ax.set_title('Frequency Sweeps')


# fig1 = plt.figure(constrained_layout = True)
# ax = fig1.add_subplot(2, 1, 1)
# bx = fig1.add_subplot(2, 1, 2)
# ax.plot(freq1,x1,color='black')
# ax.plot(freq1[0],y1[0],color='red')
# a2x = ax.twinx()
# a2x.plot(freq1,y1,color='red')
# bx.plot(freq1,R1,color='blue')
# ax.set_xlabel('Frequency (kHz)')
# bx.set_xlabel('Frequency (kHz)')
# ax.set_ylabel('Vx (mV)')
# a2x.set_ylabel('Vx (mV)')
# bx.set_ylabel('Voltage Magnitude (mV)')
# ax.legend(['Vx','Vy'])
# ax.set_title('Frequency Sweeps')

plt.show()