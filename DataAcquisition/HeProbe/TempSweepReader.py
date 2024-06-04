import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import optimize

def full_lorenzian_fit_with_skew(fs, f0,Q,Smax,A1,A2,A3):#fs is the data, f0 is the resonance freq
    return A1 + A2*fs + (Smax+A3*fs)/np.sqrt(1+4*(Q*(fs/f0-1))**2)#this is eq 10 from Measurement of resonant frequency and quality factor of microwave resonators: Comparison of methods Paul J. Petersan; Steven M. Anlage

def simple_lorenzian_fit(fs, f0,Q,Smax,A1):
    return A1 + Smax/np.sqrt(1+4*(Q*(fs/f0-1))**2)


# this allows you to input the file name, or its index in the list of files. 
# It also works for any read_path in read_paths

read_paths = [
    'C:\\Users\\Contactless\\Desktop\\Contactless Probe\\RawData\\HeProbe',
    'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/HeProbe/',
    'C:\\Users\\Contactless\\Desktop\\Contactless Probe\\RawData\\'
    ]
for read_path in read_paths:
    try:
        filenames = os.listdir(read_path)
        if len(filenames) != 1:
            print('Available files:')
            for index, item in enumerate(filenames):
                print(f"{item}: {index}")
            print('Skip path with enter')
            input_str = input("Enter file's name or index: ")
            if len(input_str) == 0:
                a = ''+1#error
            try:
                input_str = filenames[int(input_str)]
            except:
                input_str +=".dat"
        else:
            input_str = filenames[0]
        print(os.path.join(read_path, input_str))
        file_path = os.path.join(read_path, input_str)
        all_data = np.genfromtxt(file_path, delimiter='\t')
        break
    except:
        pass
try:#with temp and sweep num
    times = np.array(all_data[1:,0])
    temps = np.array(all_data[1:,1])
    vxs = np.array(all_data[1:,2])*1000 #mV
    vys = np.array(all_data[1:,3])*1000 #mV
    vmags = np.array(all_data[1:,4])*1000 #mV
    freqs = np.array(all_data[1:,5])/1000 #kHz
    sweep_nums = np.array(all_data[1:,6])
except:#single sweep data reading
    times = np.array(all_data[1:,0])
    temps = np.zeros(len(times))
    # vxs = np.array(all_data[1:,1])*1000 #mV
    # vys = np.array(all_data[1:,2])*1000 #mV
    vmags = np.array(all_data[1:,3])*1000 #mV
    freqs = np.array(all_data[1:,4])/1000 #kHz
    sweep_nums = np.ones(len(times))

max_sweep = int(np.max(sweep_nums))
if max_sweep <1:
    print('No Scans found')
    exit()
avg_temps = np.zeros(max_sweep)
Qs = np.zeros(max_sweep)
res_freqs = np.zeros(max_sweep)
avg_times = np.zeros(max_sweep)

for i in range(1,max_sweep+1):
    inds = np.logical_not(sweep_nums != i)
    plot_times = times[inds]
    plot_temps = temps[inds]
    # plot_vxs = vxs[inds]
    # plot_vys = vys[inds]
    plot_vmags = vmags[inds]
    plot_freqs = freqs[inds]

    # guesses_simple = [plot_freqs[np.argmin(plot_vmags)],30,0,0]

    guesses1 = [plot_freqs[np.argmin(plot_vmags)],30,400,400,.1,-.4]
    pbounds1 = np.array([[min(plot_freqs),1,-.5e3,0,-1,-1],[max(plot_freqs),200,.5e3,.5e3,1,1]]) # [[Lower bounds],[upper bounds]]
    bestfit = optimize.curve_fit(full_lorenzian_fit_with_skew,plot_freqs,plot_vmags,guesses1, bounds=pbounds1)
    bestpars = bestfit[0]
    # print(bestpars)
    avg_times[i-1] = np.average(plot_times)
    res_freqs[i-1] = bestpars[0]
    Qs[i-1] = bestpars[1]
    
    if np.average(plot_temps) == 0:
        avg_temps[i-1] = np.average(plot_times)
    else:
        avg_temps[i-1] = np.average(plot_temps)

        

fig1 = plt.figure(constrained_layout = True)
ax = fig1.add_subplot(2, 1, 1)
bx = fig1.add_subplot(2, 1, 2)
ax.set_xlabel('Temp (K)')
ax.set_ylabel('Res Freq')
bx.set_xlabel('Temp (K)')
bx.set_ylabel('Q')
# ax.set_title('Frequency Sweeps Number '+str(ind))
# ax.plot(plot_freqs,plot_vmags,label = 'Data')
# ax.plot(plot_freqs,full_lorenzian_fit_with_skew(plot_freqs,*bestpars),label = 'Fit')
ax.scatter(avg_temps,res_freqs)
bx.scatter(avg_temps,Qs)

fig2 = plt.figure(constrained_layout = True)
cx = fig2.add_subplot(1, 1, 1)
cx.set_xlabel('Time (min)')
cx.set_ylabel('Temp (K)')
cx.scatter(avg_times,avg_temps)

fig3 = plt.figure(constrained_layout = True)
ax1 = fig3.add_subplot(2, 1, 1)
bx1 = fig3.add_subplot(2, 1, 2)
ax1.set_xlabel('Time (min)')
ax1.set_ylabel('Res Freq')
bx1.set_xlabel('Time (min)')
bx1.set_ylabel('Q')
# ax1.set_title('Frequency Sweeps Number '+str(ind))
# ax1.plot(plot_freqs,plot_vmags,label = 'Data')
# ax1.plot(plot_freqs,full_lorenzian_fit_with_skew(plot_freqs,*bestpars),label = 'Fit')
ax1.scatter(avg_times,res_freqs)
bx1.scatter(avg_times,Qs)

plt.show()
