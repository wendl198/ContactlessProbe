import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import optimize

def full_lorenzian_fit_with_skew(fs, f0,Q,Smax,A1,A2,A3):#fs is the data, f0 is the resonance freq
    return A1 + A2*fs + (Smax+A3*fs)/np.sqrt(1+4*(Q*(fs/f0-1))**2)#this is eq 10 from Measurement of resonant frequency and quality factor of microwave resonators: Comparison of methods Paul J. Petersan; Steven M. Anlage

def simple_lorenzian_fit(fs, f0,Q,Smax,A1):
    return A1 + Smax/np.sqrt(1+4*(Q*(fs/f0-1))**2)

def find_lead_num(s):
    old_out = float(s[:2])
    for i in range(3,len(s)):
        try:
            new_out = float(s[:i])
            old_out = new_out
        except:
            return old_out

def calc_mu(omega,rho_a,rho_c,length=2e-3,width=1e-3,tolerance = 1e-6):
    mu_0 = 4*np.pi*1e-7
    if width>length:
        b = length/2
        a = width/2
    else:
        a = length/2
        b = width/2
    total_sum = 0
    n = 1
    change = np.inf

    # alpha_m_coef = np.pi/2/a
    # gamma_m_coef = np.pi/2/b
    while np.abs(change)>tolerance:
        alpha_n = np.sqrt(-1j*(omega*mu_0*(length/np.pi)**2/rho_c-1j*rho_a/rho_c*(length*n/width)**2))
        gamma_n = np.sqrt(-1j*(omega*mu_0*(width/np.pi)**2/rho_a-1j*rho_c/rho_a*n**2))

        change = (np.tan(np.pi*alpha_n/2)/alpha_n+np.tan(np.pi*gamma_n/2)/gamma_n)/n**2
        total_sum += change
        n += 2
    return total_sum*16/(np.pi)**3

def calc_power(omega,sigma_x,sigma_y,H_0,length=2e-3,width=1e-3,N_m=1,tolerance = 1e-4):
    mu = calc_mu(omega,sigma_x,sigma_y,length=length,width=width,tolerance = tolerance)
    return 1j*.5*omega*4*np.pi*1e-7*H_0*mu/(1+N_m*(mu-1))



# this allows you to input the file name, or its index in the list of files. 
# It also works for any read_path in read_paths

read_paths = [
    'C:\\Users\\Contactless\\Desktop\\Contactless Probe\\RawData\\HeProbe',
    'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/HeProbe/',
    'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/HeProbe/OVDSTO',
    'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/CSeriesTesting/',
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
            input_str = input("Enter file's index(s) seperated by ',': ")
            if len(input_str) == 0:
                raise Exception("Skip this file path")
            try:
                input_strs = [filenames[int(input_str)]]
            except:
                inds = input_str.split(',')
                input_strs = []
                cs = []
                for ind in inds:
                    input_strs.append(filenames[int(ind)])
                    cs.append(find_lead_num(filenames[int(ind)]))
        else:
            input_strs = [filenames[0]]
        all_data = []
        for input_str in input_strs:
            all_data.append(np.genfromtxt(os.path.join(read_path, input_str), delimiter='\t'))
        break
    except Exception as e:
        print(e)
        pass
try:#with temp and sweep num
    times = []
    temps = []
    vxs = []
    vys = []
    vmags = []
    freqs = []
    sweep_nums = []
    for i in range(len(all_data)):
        times.append(np.array(all_data[i][1:,0]))
        temps.append(np.array(all_data[i][1:,1]))
        vxs.append(np.array(all_data[i][1:,2])*1000) #mV
        vys.append(np.array(all_data[i][1:,3])*1000) #mV
        vmags.append(np.array(all_data[i][1:,4])*1000) #mV
        freqs.append(np.array(all_data[i][1:,5])/1000) #kHz
        sweep_nums.append(np.array(all_data[i][1:,6]))
except:#single sweep data reading
    times = []
    temps = []
    vxs = []
    vys = []
    vmags = []
    freqs = []
    sweep_nums = []
    for i in range(len(all_data)):
        times.append(np.array(all_data[i][1:,0]))
        temps.append(np.zeros(len(times)))
        # vxs.append(np.array(all_data[i][1:,1])*1000) #mV
        # vys.append(np.array(all_data[i][1:,2])*1000) #mV
        vmags.append(np.array(all_data[i][1:,3])*1000) #mV
        freqs.append(np.array(all_data[i][1:,4])/1000) #kHz
        sweep_nums.append(np.ones(len(times)))

avg_Qs = []
avg_res = []
avg_mins = []
refinedavgmins = []

t_bounds = [
    ( 0,100),
    ( 0,100),
    ( 0,110),
    ( 0,11),
    ( 2,11),
    ( 0,11),
    ( 0,11),
    ( 0,11),
    ( 0,11),
    ( 0,11),
    ( 0,11),
    ( 2,11)
]
for j in range(len(all_data)):
    max_sweep = int(np.max(sweep_nums[j]))
    if max_sweep <1:
        print('No Scans found')
    avg_temps = np.zeros(max_sweep)
    avg_times = np.zeros(max_sweep)
    Qs = np.zeros(max_sweep)
    res_freqs = np.zeros(max_sweep)
    avg_vmagsmins = np.zeros(max_sweep)
    # fig2 = plt.figure(constrained_layout = True)
    # ax = fig2.add_subplot(1, 1, 1)
    

    for i in range(1,max_sweep+1):
        inds = np.logical_not(sweep_nums[j] != i)
        plot_times = times[j][inds]
        plot_temps = temps[j][inds]
        # plot_vxs = vxs[j][inds]
        # plot_vys = vys[j][inds]
        plot_vmags = vmags[j][inds]
        plot_freqs = freqs[j][inds]

        # guesses_simple = [plot_freqs[np.argmin(plot_vmags)],30,0,0]

        guesses1 = [plot_freqs[np.argmin(plot_vmags)],186,-2.35e3,5e2,-3.3e-2,1.2]
        pbounds1 = np.array([[min(plot_freqs),1,-1e4,0,-1,-10],[max(plot_freqs),1e3,1e4,2e3,1,10]]) # [[Lower bounds],[upper bounds]]
        bestfit = optimize.curve_fit(full_lorenzian_fit_with_skew,plot_freqs,plot_vmags,guesses1, bounds=pbounds1)
        bestpars = bestfit[0]
        # print('[',end='')
        # for b in range(len(bestpars)-1):
        #     print(str(bestpars[b])+',',end='')
        # print(str(bestpars[-1]),end='],\n')
        for m, bestpar in enumerate(bestpars):
            if pbounds1[0][m] != 0 and pbounds1[1][m] != 0:
                if np.abs((bestpar-pbounds1[0][m])/pbounds1[0][m])<.005 or np.abs((pbounds1[1][m]-bestpar)/pbounds1[1][m])<.005:
                    print(bestpar,pbounds1[0][m],pbounds1[1][m])
                    print((bestpar-pbounds1[0][m])/pbounds1[0][m],(pbounds1[1][m]-bestpar)/pbounds1[1][m])
                    print()

        avg_vmagsmins[i-1] = np.min(plot_vmags)

        res_freqs[i-1] = bestpars[0]
        Qs[i-1] = bestpars[1]
        avg_times[i-1] = np.average(plot_times)
        if np.average(plot_temps) == 0:
            avg_temps[i-1] = np.average(plot_times)
            
        else:
            avg_temps[i-1] = np.average(plot_temps)


        # ax.plot(plot_freqs,plot_vmags)
    avg_Qs.append(np.average(Qs))
    avg_res.append(np.average(res_freqs))
    avg_mins.append(np.average(avg_vmagsmins))
    breakup_scans = True
    # breakup_scans = True
    if breakup_scans:
        scan_temps = []
        scan_freqs = []
        scan_Q = []
        scan_ind = -1
        increasing  = False
        for w, T in enumerate(avg_temps):
            if increasing:
                if T >avg_temps[w-1]:
                    scan_temps[scan_ind].append(T)
                    scan_freqs[scan_ind].append(res_freqs[w])
                    scan_Q[scan_ind].append(Qs[w])
                else:
                    increasing = False

            elif  w == 0 or T>avg_temps[w-1]:
                scan_temps.append([T])
                scan_freqs.append([res_freqs[w]])
                scan_Q.append([Qs[w]])
                scan_ind +=1
                increasing = True

        res = 1.8699e3
        Q = 109
        
        fig1 = plt.figure(constrained_layout = True)
        ax = fig1.add_subplot(2, 1, 1)
        bx = fig1.add_subplot(2, 1, 2)
        ax.set_xlabel('Temp (K)')
        ax.set_ylabel('Resonance Freq (kHz)')
        bx.set_xlabel('Temp (K)')
        bx.set_ylabel('Q Factor')
        # ax.set_title('As Grown Hg1201 with 15sec scan lengths')
        # ax.set_title('Capacitance = '+str(cs[j]))
        # ax.scatter(avg_temps,res_freqs)
        sc = 1
        for ind in range(len(scan_freqs)):
            if len(scan_freqs[ind])>10:
                ax.scatter(scan_temps[ind],scan_freqs[ind],label = 'Scan '+str(sc),s=4)
                bx.scatter(scan_temps[ind],scan_Q[ind],label = 'Scan '+str(sc),s=4)
                sc+=1
        # ax.scatter(scan_temps[1],scan_freqs[1],label = r'$1\frac{K}{min}$ ramp',s=4)
        # ax.scatter(scan_temps[3],scan_freqs[3],label = r'$2\frac{K}{min}$ ramp',s=4)
        # bx.scatter(scan_temps[1],scan_Q[1],label = r'$1\frac{K}{min}$ ramp',s=4)
        # bx.scatter(scan_temps[3],scan_Q[3],label = r'$2\frac{K}{min}$ ramp',s=4)
        ax.legend()
        bx.legend()
        
        
        # fig2 = plt.figure(constrained_layout = True)
        # cx = fig2.add_subplot(2, 1, 1)
        # dx = fig2.add_subplot(2, 1, 2)
        # cx.set_xlabel('Temp (K)',fontsize = 12)
        # dx.set_ylabel(r'$\frac{1}{Q_0}-\frac{1}{Q}$',fontsize = 15)
        # dx.set_xlabel('Temp (K)',fontsize = 12)
        # cx.set_ylabel(r'$\frac{f_0-f}{f_0}$',fontsize = 15)
        # cx.set_title('As Grown Hg1201 with 15sec scan lengths',fontsize = 12)
        # # p1 = 1/Q-1/np.array(scan_Q[1])
        # # p2 = 1/Q-1/np.array(scan_Q[3])
        # sc = 1
        # for ind in range(len(scan_freqs)):
        #     if len(scan_freqs[ind])>10:
        #         cx.scatter(scan_temps[ind],-1*(np.array(scan_freqs[ind])-res)/res,label = 'Scan '+str(sc),s=4)
        #         dx.scatter(scan_temps[ind],1/Q-1/np.array(scan_Q[ind]),label = 'Scan '+str(sc),s=4)
        #         sc+=1

        # dx.scatter(scan_temps[3],(np.array(scan_freqs[3])-res)/res,label = r'$2\frac{K}{min}$ ramp',s=4)
        # dx.scatter(scan_temps[1],(np.array(scan_freqs[1])-res)/res,label = r'$1\frac{K}{min}$ ramp',s=4)
        # cx.scatter(scan_temps[1],(-1/Q+1/np.array(scan_Q[1]))**-1,label = r'$1\frac{K}{min}$ ramp',s=4)
        # cx.scatter(scan_temps[3],(-1/Q+1/np.array(scan_Q[3]))**-1,label = r'$2\frac{K}{min}$ ramp',s=4)


        # cx.legend()
        # dx.legend()



    else:
        fig1 = plt.figure(constrained_layout = True)
        ax = fig1.add_subplot(3, 1, 1)
        bx = fig1.add_subplot(3, 1, 2)
        cx = fig1.add_subplot(3,1,3)
        ax.set_xlabel('Temp (K)')
        ax.set_ylabel('Resonance Freq (kHz)')
        bx.set_xlabel('Temp (K)')
        bx.set_ylabel('Q Factor')
        cx.set_xlabel('Time (min)')
        cx.set_ylabel('Temp (K)')
        # # ax.set_title('As Grown Hg1201 with 15sec scan lengths')
        ax.scatter(avg_temps,res_freqs)
        bx.scatter(avg_temps,Qs)
        cx.scatter(avg_times,avg_temps)

        fig2 = plt.figure(constrained_layout = True, figsize = (6,6))
        cx = fig2.add_subplot(2, 1, 1)
        dx = fig2.add_subplot(2, 1, 2)
        cx.set_ylabel('Avg Minimum of Vmag (mV)')
        cx.set_xlabel('Time (min)')
        cx.scatter(avg_times,avg_vmagsmins)
        dx.scatter(avg_times,avg_temps)
        dx.set_xlabel('Time (min)')
        dx.set_ylabel('Temps (K)')
        refinevmagmins = True
        if refinevmagmins:
            refinedavgmins.append(np.average(avg_vmagsmins[np.logical_and(avg_temps>=t_bounds[j][0],avg_temps<=t_bounds[j][1])]))
            




# rhos = np.linspace(4e-7,2e-6,200)
# mus = np.zeros(len(rhos),dtype=np.complex128)
# omega = 1.8699e6*2*np.pi
# a = 1.4e-3
# for i, rho in enumerate(rhos):
#     mus[i] = calc_mu(omega,rho,rho,a,a)


# fig4 = plt.figure(constrained_layout = True)
# ax1 = fig4.add_subplot(2, 1, 1)
# ax2 = fig4.add_subplot(2, 1, 2)
# ax1.set_xlabel(r'Resistivity m$\Omega$cm')
# ax2.set_xlabel(r'Resistivity m$\Omega$cm')
# ax1.set_ylabel(r'$\mu$ Real part (A.U.)')
# ax2.set_ylabel(r'$\mu$ Imaginary Part (A.U.)')
# ax1.plot(rhos*1e5,np.real(mus))
# ax2.plot(rhos*1e5,np.imag(mus))    

# for i in range(len(cs)):
#     print(cs[i],avg_res[i],avg_Qs[i],avg_mins[i])
# fig2 = plt.figure(constrained_layout = True)
# ax = fig2.add_subplot(1, 1, 1)
# ax.scatter(cs,avg_mins)
            
# fig4 = plt.figure(constrained_layout = True)
# ax1 = fig4.add_subplot(1, 1, 1)
# ax1.scatter(cs,refinedavgmins)
# ax1.set_xlabel('Capacitance (nF)')
# ax1.set_ylabel('Minimum Voltage (mV)')
# 0,1,2,3,4,5,6,7,8,9,10,11
plt.show()