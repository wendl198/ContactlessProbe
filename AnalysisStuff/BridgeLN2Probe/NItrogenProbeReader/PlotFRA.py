import numpy as np
import matplotlib.pyplot as plt

def average_data(V,freqs):
    combos = []
    fs = [*set(freqs)]
    fs.sort()
    for i, f in enumerate(fs):
        combos.append([])
        for j, freq in enumerate(freqs):
            if f == freq:
                combos[i].append(V[j])
    vout = []
    vstd = []
    for combo in combos:
        vout.append(np.mean(combo))
        vstd.append(np.std(combo))
    return np.array(vout),np.array(vstd)



#####################
# Import Data
#####################
path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/'
path_suffix = '.dat'
# filename1 = 'FRA12'
# filename2 = 'EmptyFRA'
filename1 = 'FRABW69_1'
filename2 = 'Empty3'
# filename1 = 'BW79_1FRA4'
# filename2 = 'EmptyFRA_BW79_1'
data_path1 = path_prefix + filename1 + path_suffix
data_path2 = path_prefix + filename2 + path_suffix

all_data = np.genfromtxt(data_path1, delimiter='\t')
t1 = np.array(all_data[1:,0])
T1 = np.array(all_data[1:,1])
freq1 = np.array(all_data[1:,2])
x1 = np.array(all_data[1:,3])*1000
x1,x1err = average_data(x1,freq1)
y1 = np.array(all_data[1:,4])*1000
y1,y1err = average_data(y1,freq1)
freq1 = [*set(freq1)]
freq1.sort()
R1 = np.sqrt(x1**2+y1**2)

# fig1 = plt.figure(constrained_layout = True)
# ax = fig1.add_subplot(2, 1, 1)
# bx = fig1.add_subplot(2, 1, 2)
# ax.errorbar(freq1,x1,x1err,fmt="o")
# bx.errorbar(freq1,y1,y1err,fmt="o")
# ax.set_xlabel('Frequency (kHz)')
# bx.set_xlabel('Frequency (kHz)')
# ax.set_ylabel('Vx (mV)')
# bx.set_ylabel('Vy (mV)')




all_data = np.genfromtxt(data_path2, delimiter='\t')
t2 = np.array(all_data[1:,0])
T2 = np.array(all_data[1:,1])
freq2 = np.array(all_data[1:,2])
x2 = np.array(all_data[1:,3])*1000
x2,x2err = average_data(x2,freq2)
y2 = np.array(all_data[1:,4])*1000
y2,y2err = average_data(y2,freq2)
freq2 = [*set(freq2)]
freq2.sort()
R2 = np.sqrt(x2**2+y2**2)

fig2 = plt.figure(constrained_layout = True)
ax = fig2.add_subplot(2, 1, 1)
bx = fig2.add_subplot(2, 1, 2)
ax.errorbar(freq1,x1,x1err,fmt="o")
bx.errorbar(freq1,y1,y1err,fmt="o")
ax.errorbar(freq2,x2,x2err,fmt="o")
bx.errorbar(freq2,y2,y2err,fmt="o")
ax.set_xlabel('Frequency (kHz)')
bx.set_xlabel('Frequency (kHz)')
ax.set_ylabel('Vx (mV)')
bx.set_ylabel('Vy (mV)')


fig3 = plt.figure(constrained_layout = True)
cx = fig3.add_subplot(1, 1, 1)
cx.scatter(freq2,np.sqrt((x1-x2)**2+(y1-y2)**2))
cx.set_xlabel('Frequency (kHz)')
cx.set_ylabel('signal Strength (mV)')

# fig4 = plt.figure(constrained_layout = True)
# dx = fig4.add_subplot(2, 1, 1)
# ex = fig4.add_subplot(2, 1, 2)
# dx.scatter(t1,T1)
# dx.set_xlabel('Time (min)')
# dx.set_ylabel('Temp (K)')
# ex.scatter(t1,T1)
# ex.set_xlabel('Time (min)')
# ex.set_ylabel('Temp (K)')

fig5 = plt.figure(constrained_layout = True)
fx = fig5.add_subplot(2, 1, 1)
gx = fig5.add_subplot(2, 1, 2)
fx.scatter(freq1,x1-x2)
gx.scatter(freq1,y1-y2)
fx.set_xlabel('Frequency (kHz)')
gx.set_xlabel('Frequency (kHz)')
fx.set_ylabel('Delta Vx (mV)')
gx.set_ylabel('Delta Vy (mV)')

plt.show()