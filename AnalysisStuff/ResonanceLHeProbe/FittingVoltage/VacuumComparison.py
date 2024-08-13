import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import optimize
from scipy import interpolate


def show_data(data,fit_info = (False,None,False,None),filename='',show = False,mag_only = True):
    if show:
        if mag_only:
            fig1 = plt.figure(constrained_layout = True)
            ax = fig1.add_subplot(1, 1, 1)
            ax.scatter(data['freq'],data['vmag']*data['vamp'],color='green',label=filename)
            if fit_info[0]:
                bestpars1 = fit_info[1]
                ax.plot(data['freq'],data['vamp']*(bestpars1[3]+bestpars1[4]*data['freq']+(bestpars1[2]+bestpars1[5]*data['freq'])/np.sqrt(1+4*(bestpars1[1]*(data['freq']/bestpars1[0]-1))**2)),label='Full Lorenzian Fit')
                
            if fit_info[2]:
                bestpars2 = fit_info[3]
                ax.plot(data['freq'],data['vamp']*(bestpars2[3]+bestpars2[2]/np.sqrt(1+4*(bestpars2[1]*(data['freq']/bestpars2[0]-1))**2)),label = 'Refined Fit')
            ax.legend()  
            ax.set_xlabel('Frequency (kHz)')
            ax.set_ylabel('Voltage Magnitude (mV)')
            ax.set_title('Lorenzian Fit for '+filename)
        else:
            fig0 = plt.figure(constrained_layout = True)
            ax1 = fig0.add_subplot(3, 1, 1)
            ax2 = fig0.add_subplot(3, 1, 2)
            ax3 = fig0.add_subplot(3, 1, 3)
            ax1.set_xlabel('Frequency (kHz)')
            ax2.set_xlabel('Frequency (kHz)')
            ax3.set_xlabel('Frequency (kHz)')
            ax1.set_ylabel('Vx (mV)')
            ax2.set_ylabel('Vx (mV)')
            ax3.set_ylabel('Voltage Magnitude (mV)')
            ax1.plot(data['freq'],data['vx'])
            ax2.plot(data['freq'],data['vy'])
            ax3.plot(data['freq'],data['vmag']*data['vamp'])


path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/'
path_suffix = '.dat'

# filenames = [
#              'double1nf',
#             #  'double.47nf',
#             #  'double3.9nf',
#             #  '.5nfseries1nfparallel',
#             #  '2nfserise1nfparallel2',
#             #  '1nfseries3.9nfparallel'
#               ]
 

path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/0.2nf1nfTest/'
filenames = os.listdir(path_prefix)
path_suffix = ''

data_paths = []
for f in filenames:
         data_paths.append(path_prefix + f + path_suffix)
         
datas = []
i = 0
for data in data_paths:
    try:
        all_data = np.genfromtxt(data, delimiter='\t')
        headings = np.genfromtxt(data, delimiter='\t', dtype=str, max_rows=1)
        datas.append({})
        # print(all_data)
        datas[i]['time'] = np.array(all_data[2:,0])
        datas[i]['vamp'] = float(headings[-1].split(' ')[-2])
        datas[i]['vx'] = np.array(all_data[2:,1])*-1000
        datas[i]['vy'] = np.array(all_data[2:,2])*-1000
        datas[i]['vmag'] = np.array(all_data[2:,3])*1000/datas[i]['vamp']
        datas[i]['freq'] = np.array(all_data[2:,4])
        # datas[i]['turns'] = float(filenames[i][:-9])
        i+=1
    except PermissionError:
        print("Can't read folder",data)

for i in range(len(datas)):
    pass

fitted = {}
for dat in datas[0]:
    if dat == 'vx' or dat == 'vy':
        fitted[dat] = np.abs((datas[1][dat] - np.interp(datas[1]['freq'],datas[0]['freq'],datas[0][dat]))*100/datas[1][dat])
    else:
        fitted[dat] = datas[1][dat]
show_data(fitted,fit_info = (False,None,False,None),filename=filenames[i],show = True, mag_only = False)
plt.show()