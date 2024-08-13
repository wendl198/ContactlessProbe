import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import optimize

#this program is very useful for optimizing the value of C1, by doing a room temp capacitance sweep, and then extend it to cryo temps

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


def get_vmag_mins(C1s,R,A,C2=.22e-9,L = 24e-6,Z0=100):
    freq = np.linspace(1.5e6,2.5e6,5000)
    output = np.zeros(len(C1s))
    for i, C1 in enumerate(C1s):

        ZL = full_Z(2*np.pi*freq,C1*1e-9,C2,L,R)/Z0
        reflect = (ZL-1)/(ZL+1)
        output[i] = A*np.min(np.abs(reflect))
    return output

def get_vmag_mins_fine(C1s,R,A,C2=.22e-9,L = 24e-6,Z0=100):
    freq = np.linspace(1.5e6,2.5e6,50000)
    output = np.zeros(len(C1s))
    for i, C1 in enumerate(C1s):

        ZL = full_Z(2*np.pi*freq,C1*1e-9,C2,L,R)/Z0
        reflect = (ZL-1)/(ZL+1)
        output[i] = A*np.min(np.abs(reflect))
    return output

# def get_vmag_mins3(C1s,R,A,C2,L,Z0=100):
#     freq = np.linspace(.5e6,3e6,1000)
#     output = np.zeros(len(C1s))
#     for i, C1 in enumerate(C1s):

#         ZL = full_Z(2*np.pi*freq,C1*1e-9,C2,L,R)/Z0
#         reflect = (ZL-1)/(ZL+1)
#         output[i] = A*np.min(np.abs(reflect))
#     return output

def full_Z(omega, C1, C2, L, R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return R/A +1j*(omega*B/A-1/(omega*C1))

def cosort_lists(list_to_sort,list_to_cosort):
    out1 = np.zeros(l1 := len(list_to_sort))
    out2 = np.zeros(len(list_to_cosort))
    sorted_inds = np.argsort(np.argsort(list_to_sort))
    for i in range(l1):
        for j, ind in enumerate(sorted_inds):
            if i == ind:
                out1[i] = list_to_sort[j]
                out2[i] = list_to_cosort[j]
                break
    return out1, out2


'''
#if you have a lot of files that you would like to auto read

# this allows you to input the file name, or its index in the list of files. 
# It also works for any read_path in read_paths

read_path = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/CSeriesTesting/'
filenames = os.listdir(read_path)

inds = np.arange(12)
input_strs = []
cs = []
for ind in inds:
    input_strs.append(filenames[int(ind)])
    cs.append(find_lead_num(filenames[int(ind)]))
all_data = []
for input_str in input_strs:
    all_data.append(np.genfromtxt(os.path.join(read_path, input_str), delimiter='\t'))

#read in room temp data
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
#custom bounds of when room temp data is useful
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

#calc the properties for each room temp measurement
for j in range(len(all_data)):
    max_sweep = int(np.max(sweep_nums[j]))
    if max_sweep <1:
        print('No Scans found')
    avg_temps = np.zeros(max_sweep)
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

        guesses1 = [plot_freqs[np.argmin(plot_vmags)],73,-2e3,7e2,-5e-2,.7]
        pbounds1 = np.array([[min(plot_freqs),1,-1e4,0,-1,-10],[max(plot_freqs),200,1e4,1e4,1,10]]) # [[Lower bounds],[upper bounds]]
        bestfit = optimize.curve_fit(full_lorenzian_fit_with_skew,plot_freqs,plot_vmags,guesses1, bounds=pbounds1)
        bestpars = bestfit[0]

        for m, bestpar in enumerate(bestpars):
            if pbounds1[0][m] != 0 and pbounds1[1][m] != 0:
                if np.abs((bestpar-pbounds1[0][m])/pbounds1[0][m])<.005 or np.abs((pbounds1[1][m]-bestpar)/pbounds1[1][m])<.005:
                    print(bestpar,pbounds1[0][m],pbounds1[1][m])
                    print((bestpar-pbounds1[0][m])/pbounds1[0][m],(pbounds1[1][m]-bestpar)/pbounds1[1][m])
                    print()

        avg_vmagsmins[i-1] = np.min(plot_vmags)

        res_freqs[i-1] = bestpars[0]
        Qs[i-1] = bestpars[1]
        if np.average(plot_temps) == 0:
            avg_temps[i-1] = np.average(plot_times)
        else:
            avg_temps[i-1] = np.average(plot_temps)

    
    refinevmagmins = True
    if refinevmagmins:
        refinedavgmins.append(np.average(avg_vmagsmins[np.logical_and(avg_temps>=t_bounds[j][0],avg_temps<=t_bounds[j][1])]))

'''

# set up plots
fig4 = plt.figure(constrained_layout = True)
ax1 = fig4.add_subplot(1, 1, 1)
ax1.set_xlabel('Capacitance (nF)',fontsize=15)
ax1.set_ylabel('Minimum Voltage (mV)',fontsize=15)
ax1.tick_params(axis='x', labelsize=15)
ax1.tick_params(axis='y', labelsize=15)

#plot results
# ax1.scatter(cs,refinedavgmins,label='300 K Data',c='black')

#add points by hand
# ax1.scatter([1/(1/.1+1/.33),1/(1/.1+1/.33+1/.22),1/(1+1/.1+1/.22)],[124,93,3],label='4 K Data',marker='^',c='red')
# ax1.scatter([1/(1/.1+1/.33+1+1),1/(1/.1+1/.33+1/.22+1),1/(1/.1+1/.33+1/.33+1),1/(1/.1+1/.1+1/.22+1)],[172,107,135,4.8],label = '4 K NewCaps data',c='purple')
# ax1.scatter([1/(1/.1+1/.33+1/.22+1),1/(1/.1+1+1+1),1/(1/.22+1/.33+1/1.8+1/4.7)],[510,290,195])
ax1.scatter([1/(1/.1+1/1.8+1/1.8+1/4.7),.05],[224,49.5],label = '7/26 points')

#fitting attempts and plotting




# c_cont = np.linspace(cs[0],cs[-1],5000)
c_cont = np.linspace(.005,.15,5000)#this is the range of C1 that you want to simulate

pbounds1 = np.array([[.1,1],[50,3000]]) # [[Lower bounds],[upper bounds]]

# cs,refinedavgmins = cosort_lists(cs,refinedavgmins)
# # cs = cs[:-1]
# # refinedavgmins = refinedavgmins[:-1]

#automated fit
# guesses1 = [15,500]
# bestfit = optimize.curve_fit(get_vmag_mins,cs,refinedavgmins,guesses1, bounds=pbounds1)
# bestpars1 = bestfit[0]

#by hand fitting
# the fitting function needs a list of capacitances and then v_mag_mins with the same length

guesses1 = [3,500]
bestfit = optimize.curve_fit(get_vmag_mins,[1/(1/.1+1/.33+1+1),1/(1/.1+1/.33+1/.22+1),1/(1/.1+1/.33+1/.33+1),1/(1/.1+1/.1+1/.22+1)],[172,107,135,4.8],guesses1, bounds=pbounds1)
bestpars2 = bestfit[0]

guesses1 = [5,900]
bestfit = optimize.curve_fit(get_vmag_mins,[1/(1/.1+1/.33),1/(1/.1+1/.33+1/.22),1/(1+1/.1+1/.22)],[124,93,3],guesses1, bounds=pbounds1)
bestpars3 = bestfit[0]

# guesses1 = [8,900]
# bestfit = optimize.curve_fit(get_vmag_mins,[1/(1/.1+1/.33+1/.22+1),1/(1/.1+1+1+1)],[510,290],guesses1, bounds=pbounds1)
# bestpars4 = bestfit[0]

# guesses1 = [4,1500]
# bestfit = optimize.curve_fit(get_vmag_mins,[1/(1/.1+1/.33+1/.22+1),1/(1/.1+1+1+1)],[510,290],guesses1, bounds=pbounds1)
# bestpars5 = bestfit[0]

guesses1 = [3,500]
bestfit = optimize.curve_fit(get_vmag_mins,[1/(1/.1+1/1.8+1/1.8+1/4.7),.05],[224,49.5],guesses1, bounds=pbounds1)
bestpars4 = bestfit[0]

guesses1 = [5,500]
bestfit = optimize.curve_fit(get_vmag_mins,[1/(1/.1+1/1.8+1/1.8+1/4.7),.05],[224,49.5],guesses1, bounds=pbounds1)
bestpars5 = bestfit[0]

# ax1.plot(c_cont,get_vmag_mins_fine(c_cont,*bestpars2),label = '4 K NewCaps fit',c='black')
# ax1.plot(c_cont,get_vmag_mins_fine(c_cont,*bestpars3),label = '4 K fit',c='cyan')
ax1.plot(c_cont,get_vmag_mins_fine(c_cont,*bestpars4),label = '4 K NewCaps2.1 fit')
ax1.plot(c_cont,get_vmag_mins_fine(c_cont,*bestpars5),label = '4 K NewCaps2.2 fit')




print(bestpars2,bestpars3)
print(bestpars4,bestpars5)






#given a new point[C1,V_mag_min], fit for best new C1
new_points = [
    # [1/(1/.1+1/.1+1/.22+1),247],
    # [1/(1/.1+1/.33+1/.22+1),510],
    # [1/(1/.1+1/1.8+1/1.8+1/4.7),224]
    ]
nearest_fits = [
    bestpars4]

for i, new_point in enumerate(new_points):
    nearest_fit = nearest_fits[i]

    def get_vmag_mins_res(C1s,R,A=nearest_fit[1],C2=.22e-9,L = 24e-6,Z0=100):
        freq = np.linspace(1.5e6,2.5e6,30000)
        output = np.zeros(len(C1s))
        for i, C1 in enumerate(C1s):

            ZL = full_Z(2*np.pi*freq,C1*1e-9,C2,L,R)/Z0
            reflect = (ZL-1)/(ZL+1)
            output[i] = A*np.min(np.abs(reflect))
        return output

    bestfit = optimize.curve_fit(get_vmag_mins_res,[new_point[0]],[new_point[1]],nearest_fit[0], bounds=[pbounds1[0][0],pbounds1[1][0]])
    bestpars4 = bestfit[0]
    ax1.scatter(new_point[0],new_point[1],label = 'New Point', c = 'magenta')
    ax1.plot(c_cont,get_vmag_mins_res(c_cont,*bestpars4),label = 'New Point Res Fit',c='green')

#part 2 of this program, I replaced C2 and now I want to re refined the analysis. Its capacitance value is slightly different though

# def get_vmag_mins2(C2s,R =bestpars3[0],A = bestpars3[1],C1=1/(1+1/.1+1/.22),L = 24e-6,Z0=100):
#     freq = np.linspace(1.5e6,2.5e6,30000)
#     output = np.zeros(len(C2s))
#     for i, C2 in enumerate(C2s):
#         ZL = full_Z(2*np.pi*freq,C1*1e-9,C2*1e-9,L,R)/Z0
#         reflect = (ZL-1)/(ZL+1)
#         output[i] = A*np.min(np.abs(reflect))
#     return output
# c_cont2 = np.linspace(.15,.3,5000)
# fig5 = plt.figure(constrained_layout = True)
# px = fig5.add_subplot(1, 1, 1)
# px.plot(c_cont2,get_vmag_mins2(c_cont2))

# guesses2 = [.2e-9]
# pbounds2 = np.array([[1e10],[1e-9]]) # [[Lower bounds],[upper bounds]]
# bestfit = optimize.curve_fit(get_vmag_mins,[1/(1/.1+1/.33),0.1407],[21,195.3],guesses2, bounds=pbounds2)
# bestpars6 = bestfit[0]
# print(bestpars6)
# guesses2 = [.3e-9]
# pbounds2 = np.array([[1e10],[1e-9]]) # [[Lower bounds],[upper bounds]]
# bestfit = optimize.curve_fit(get_vmag_mins,[1/(1/.1+1/.33),0.1407],[21,195.3],guesses2, bounds=pbounds2)
# bestpars7 = bestfit[0]
# print(bestpars7)
ax1.legend()
plt.show()