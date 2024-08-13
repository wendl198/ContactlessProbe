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

def calc_mu(omega,sigma_x,sigma_y,length=2e-3,width=1e-3,tolerance = 1e-4):
    mu_0 = 4*np.pi*1e-7
    if width>length:
        b = length/2
        a = width/2
    else:
        a = length/2
        b = width/2
    total_sum = 0
    m = 1
    change = np.inf
    alpha_m_coef = np.pi/2/a
    gamma_m_coef = np.pi/2/b
    while np.abs(change)>tolerance:
        alpha_m = m * alpha_m_coef
        gamma_m = m * gamma_m_coef
        beta_m = np.sqrt(1j*omega*mu_0*sigma_x+alpha_m**2*sigma_x/sigma_y)
        delta_m = np.sqrt(1j*omega*mu_0*sigma_y+gamma_m**2*sigma_y/sigma_x)
        change = (np.tanh(beta_m*b)/(alpha_m*beta_m)+np.tanh(delta_m*a)/(gamma_m*delta_m))/m
        total_sum += change
        m+=2
    return total_sum*4/np.pi

def calc_power(omega,sigma_x,sigma_y,H_0,length=2e-3,width=1e-3,N_m=1,tolerance = 1e-4):
    mu = calc_mu(omega,sigma_x,sigma_y,length=length,width=width,tolerance = tolerance)
    return 1j*.5*omega*4*np.pi*1e-7*H_0*mu/(1+N_m*(mu-1))

def full_Z(omega, C1, C2, L, R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return R/A +1j*(omega*B/A-1/(omega*C1))

def reflection_coeff(omega, C1, C2, L, R, Z0=50):
    ZL = full_Z(omega, C1, C2,L,R)
    return (ZL/Z0-1)/(ZL/Z0+1)

def full_lorenzian_fit_with_skew(fs, f0,Q,Smax,A1,A2,A3):#fs is the data, f0 is the resonance freq
    return A1 + A2*fs + (Smax+A3*fs)/np.sqrt(1+4*(Q*(fs/f0-1))**2)#this is eq 10 from Measurement of resonant frequency and quality factor of microwave resonators: Comparison of methods Paul J. Petersan; Steven M. Anlage

def simple_lorenzian_fit(fs, f0,Q,Smax,A1):
    return A1 + Smax/np.sqrt(1+4*(Q*(fs/f0-1))**2)

def plot_polyfit(x_data,poly_coefficents):
    l = len(x_data)
    output = np.zeros(l)
    for i,a in enumerate(poly_coefficents[::-1]):
        for j in range(l):
            output[j] += a*x_data[j]**i 
    return output

def VxVyfit_2ndorderbackground(omega, C1, C2, L, R, A0, A1, A2, B0, B1, B2):
    complex_ref_coef = reflection_coeff(omega, C1, C2, L, R) +A0 +A1*omega+A2*omega**2 +1j*(B0 +B1*omega+B2*omega**2)
    return np.append(np.real(complex_ref_coef),np.imag(complex_ref_coef))

def quad(freq,A0,A1,A2):
    return A0 + A1*freq + A2*freq**2

def full_Z(omega, C1, C2, L, R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return R/A +1j*(omega*B/A-1/(omega*C1))

def reflection_coeff(omega, C1, C2, L, R, Z0=100):
    ZL = full_Z(omega, C1, C2,L,R)
    return (ZL/Z0-1)/(ZL/Z0+1)

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
 

# path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/InitialRandomTesting/'
# path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/LChange/'
# path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/TurnTesting/'
# path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/AfterCircCalData/'#ColdTest/'
# path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/BackgroundTest/'
path_prefix = 'C:/Users/blake/Documents/VSCode/Python/Greven/RawData/QFactorTesting/NoSeriesCap/'
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

fits = []
fits2 = []
for i in range(len(datas)):
    res_freq_ind = np.argmin(datas[i]['vmag'])#just a guess
    f_guess = datas[i]['freq'][res_freq_ind]

    guesses1 = [f_guess,10,-.3,.26,0,0]
    pbounds1 = np.array([[max(min(datas[i]['freq']),500e3),1,-1,-1,-1,-1],[min(max(datas[i]['freq']),4000e3),1e4,1,1,1,1]]) # [[Lower bounds],[upper bounds]]
    bestfit = optimize.curve_fit(full_lorenzian_fit_with_skew,datas[i]['freq'],datas[i]['vmag'],guesses1, bounds=pbounds1)
    bestpars1 = bestfit[0]
    inds = np.logical_not(abs(datas[i]['freq']-bestpars1[0])/bestpars1[0]>.05)
    bestfit = optimize.curve_fit(simple_lorenzian_fit,datas[i]['freq'][inds],datas[i]['vmag'][inds],bestpars1[:4], bounds=[pbounds1[0][:4],pbounds1[1][:4]])
    bestpars2 = bestfit[0]
    fits.append((bestpars1[0],bestpars1[1]))
    fits2.append((bestpars2[0],bestpars2[1]))
    show_data(datas[i],fit_info = (True,bestpars1,False,bestpars2),filename=filenames[i],show = True, mag_only = False)
    fit_res_freq_ind = np.argmin(datas[i]['freq']-bestpars2[0])



ind = 0


#bounds
# circ_low_bounds = [1e-12,1e-12,100e-9,1e-3]
# circ_high_bounds = [10e-9,10e-9,1e3,1e2]
# background_low_bounds = [-1e1,-1e-3,-1e-8,-1e1,-1e-3,-1e-8]
# background_high_bounds = [1e1,1e-3,1e-8,1e1,1e-3,1e-8]

# low_bounds = np.append(circ_low_bounds,background_low_bounds)
# high_bounds = np.append(circ_high_bounds,background_high_bounds)
# bounds = [low_bounds,high_bounds]



# # #prefit
# fitted = {}
# for dat in datas[ind]:
#     if dat != 'vamp':
#         l = len(datas[ind][dat])
#         fitted[dat] = datas[ind][dat][np.logical_or(datas[ind]['freq']<1.9e6, datas[ind]['freq']>2e6)]
#     else:
#         fitted[dat] = datas[ind][dat]
# prefit_bounds = [background_low_bounds[:3],background_high_bounds[:3]]
# # show_data(datas[ind],fit_info = (False,bestpars1,False,bestpars2),filename='',show = True, mag_only = False)

# # #guesses with prefit
# vx_prefit = optimize.curve_fit(quad,fitted['freq']*2*np.pi, fitted['vx']/datas[ind]['vamp']-1,bounds=prefit_bounds)
# vy_prefit = optimize.curve_fit(quad,fitted['freq']*2*np.pi, fitted['vy']/datas[ind]['vamp'],bounds=prefit_bounds)
# vx_background_guesses = vx_prefit[0]
# vy_background_guesses = vy_prefit[0]
# circ_guesses = [33e-12,235e-12,24e-6,.5] #C_par,C_ser,L,R
# guesses = np.append(circ_guesses,np.append(vx_background_guesses,vy_background_guesses))


# bestfit = optimize.curve_fit(VxVyfit_2ndorderbackground, datas[ind]['freq']*2*np.pi, np.append(datas[ind]['vx']/datas[ind]['vamp'],datas[ind]['vy']/datas[ind]['vamp']), guesses, bounds=bounds, maxfev=10000)
# bestpars = bestfit[0]
# updated_guess = np.append(circ_guesses,bestpars[4:])
# bestfit = optimize.curve_fit(VxVyfit_2ndorderbackground, datas[ind]['freq']*2*np.pi, np.append(datas[ind]['vx']/datas[ind]['vamp'],datas[ind]['vy']/datas[ind]['vamp']), updated_guess, bounds=bounds, maxfev=10000)
# bestpars = bestfit[0]
# fit_info = VxVyfit_2ndorderbackground(datas[ind]['freq']*2*np.pi,*bestpars)
# l = len(fit_info)
# vx_fit = fit_info[:l//2]
# vy_fit = fit_info[l//2:l]

# print(bestpars)

# guess_fit = VxVyfit_2ndorderbackground(datas[ind]['freq']*2*np.pi,*guesses)
# l = len(guess_fit)
# vx_guess = guess_fit[:l//2]
# vy_guess = guess_fit[l//2:l]


# no_circ = np.append([np.inf,0,0,0],bestpars[4:])
# sub_2nd_order = VxVyfit_2ndorderbackground(datas[ind]['freq']*2*np.pi,*no_circ)
# vy_nocirc = sub_2nd_order[l//2:l]
# vx_nocirc = sub_2nd_order[:l//2]


# fig4 = plt.figure(constrained_layout = True)
# ax1 = fig4.add_subplot(3, 1, 1)
# ax2 = fig4.add_subplot(3, 1, 2)
# ax3 = fig4.add_subplot(3, 1, 3)
# # ax1 = fig4.add_subplot(2, 1, 1)
# # ax2 = fig4.add_subplot(2, 1, 2)
# ax1.set_xlabel('Frequency (kHz)')
# ax2.set_xlabel('Frequency (kHz)')
# ax3.set_xlabel('Frequency (kHz)')
# ax1.set_ylabel('Vx (mV)')
# ax2.set_ylabel('Vx (mV)')
# ax3.set_ylabel('Voltage Magnitude (mV)')
# ax1.scatter(datas[ind]['freq'],datas[ind]['vx']/datas[ind]['vamp'])
# ax2.scatter(datas[ind]['freq'],datas[ind]['vy']/datas[ind]['vamp'])
# ax3.scatter(datas[ind]['freq'],datas[ind]['vmag']*datas[ind]['vamp'])
# ax1.plot(datas[ind]['freq'],vx_fit,c='green')
# ax2.plot(datas[ind]['freq'],vy_fit,c='green')
# # ax1.plot(datas[ind]['freq'],vx_guess,c='red')
# # ax2.plot(datas[ind]['freq'],vy_guess,c='red')
# ax1.plot(datas[ind]['freq'],quad(datas[ind]['freq']*2*np.pi,*vx_background_guesses)+1,c='orange')
# ax2.plot(datas[ind]['freq'],quad(datas[ind]['freq']*2*np.pi,*vy_background_guesses),c='orange')
# ax3.plot(datas[ind]['freq'],vx_nocirc)
# ax3.plot(datas[ind]['freq'],vy_nocirc)
# ax3.plot(datas[ind]['freq'],np.real(reflection_coeff(datas[ind]['freq']*2*np.pi,*circ_guesses)))
# ax3.plot(datas[ind]['freq'],np.imag(reflection_coeff(datas[ind]['freq']*2*np.pi,*circ_guesses)))
# print(vx_nocirc)

#fitting background attemps
"""
fitted = {}
for dat in datas[2]:
    if dat != 'vamp':
        l = len(datas[2][dat])
        fitted[dat] = np.append(datas[2][dat][:int(l//2-250)] , datas[2][dat][int(l//2+75):])
    else:
        fitted[dat] = datas[2][dat]
# show_data(datas[2],fit_info = (False,bestpars1,False,bestpars2),filename='WideRange',show = True, mag_only = False)

inps = 2
if inps == 2:
    def vx_fit(freq,A,B):
        return A + B*freq 
    guesses3 = [fitted['vx'][0],1e-1]
    pbounds3 = np.array([[-1e3,-1],[1e3,1]]) # [[Lower bounds],[upper bounds]]
    guesses4 = [fitted['vy'][0],-1e-1]
    pbounds4 = np.array([[-1e3,-1],[1e3,1]]) # [[Lower bounds],[upper bounds]]
if inps == 3:
    def vx_fit(freq,A,B,C):
        return A + B*freq + C*freq**2
    guesses3 = [fitted['vx'][0],1e-1,0]
    pbounds3 = np.array([[-1e3,-1,-1],[1e3,1,1]]) # [[Lower bounds],[upper bounds]]
    guesses4 = [fitted['vy'][0],-1e-1,0]
    pbounds4 = np.array([[-1e3,-1,-1],[1e3,1,1]]) # [[Lower bounds],[upper bounds]]
elif inps ==4:
    def vx_fit(freq,A,B,C,D):
        return A + B*freq + C/(freq-D)
    guesses3 = [fitted['vx'][0],-1e-1,0,-2e6]
    pbounds3 = np.array([[-1e3,-1,-1,-1e7],[1e3,1,1,1e7]]) # [[Lower bounds],[upper bounds]]
    guesses4 = [fitted['vy'][0],-1e-1,0,0]
    pbounds4 = np.array([[-1e3,-1,-1,-1e7],[1e3,1,1,1e7]]) # [[Lower bounds],[upper bounds]]
elif inps == 5:
    def vx_fit(freq,A,B,C,D,E):
        return A + B*freq + C*(freq/100)**2 + D*(freq/100)**3 + E*(freq/100)**4
    guesses3 = [fitted['vx'][0],-1e-1,0,0,0]
    pbounds3 = np.array([[-1e3,-1,-1,-1,-1],[1e3,1,1,1,1]]) # [[Lower bounds],[upper bounds]]
    guesses4 = [fitted['vy'][0],-1e-1,0,0,0]
    pbounds4 = np.array([[-1e3,-1,-1,-1,-1],[1e3,1,1,1,1]]) # [[Lower bounds],[upper bounds]]

bestfit = optimize.curve_fit(vx_fit,datas[i]['freq'],datas[i]['vx'],guesses3, bounds=pbounds3)
bestpars3 = bestfit[0]
bestfit = optimize.curve_fit(vx_fit,datas[i]['freq'],datas[i]['vy'],guesses4, bounds=pbounds4)
bestpars4 = bestfit[0]
vy_background = vx_fit(fitted['freq'],*bestpars4)
vx_background = vx_fit(fitted['freq'],*bestpars3)
k = 3
vx_spline = interpolate.make_interp_spline(fitted['freq'],fitted['vx'],k=k)
vy_spline = interpolate.make_interp_spline(fitted['freq'],fitted['vy'],k=k)
vx_background = vx_spline(datas[2]['freq'])
vy_background = vy_spline(datas[2]['freq'])
vmag_background = np.sqrt(vx_background**2+vy_background**2)

print(bestpars3,bestpars4)
fig4 = plt.figure(constrained_layout = True)
ax1 = fig4.add_subplot(3, 1, 1)
ax2 = fig4.add_subplot(3, 1, 2)
ax3 = fig4.add_subplot(3, 1, 3)
ax1.set_xlabel('Frequency (kHz)')
ax2.set_xlabel('Frequency (kHz)')
ax3.set_xlabel('Frequency (kHz)')
ax1.set_ylabel('Vx (mV)')
ax2.set_ylabel('Vx (mV)')
ax3.set_ylabel('Voltage Magnitude (mV)')
ax1.scatter(datas[2]['freq'],datas[2]['vx'])
ax2.scatter(datas[2]['freq'],datas[2]['vy'])
ax3.scatter(datas[2]['freq'],datas[2]['vmag']*datas[2]['vamp'])
ax1.scatter(fitted['freq'],fitted['vx'])
ax2.scatter(fitted['freq'],fitted['vy'])
ax3.scatter(fitted['freq'],fitted['vmag']*fitted['vamp'])
ax1.plot(datas[2]['freq'],vx_background,c='green')
ax2.plot(datas[2]['freq'],vy_background,c='green')

fig5 = plt.figure(constrained_layout = True)
bx1 = fig5.add_subplot(3, 1, 1)
bx2 = fig5.add_subplot(3, 1, 2)
bx3 = fig5.add_subplot(3, 1, 3)
bx1.set_xlabel('Frequency (kHz)')
bx2.set_xlabel('Frequency (kHz)')
bx3.set_xlabel('Frequency (kHz)')
bx1.set_ylabel('Vx (mV)')
bx2.set_ylabel('Vx (mV)')
bx3.set_ylabel('Voltage Magnitude (mV)')
sub = True
if sub:
    bx1.scatter(datas[2]['freq'],datas[2]['vx']-np.interp(datas[2]['freq'],datas[2]['freq'],vx_background))
    bx2.scatter(datas[2]['freq'],datas[2]['vy']-np.interp(datas[2]['freq'],datas[2]['freq'],vy_background))
    bx3.scatter(datas[2]['freq'],datas[2]['vmag']*datas[2]['vamp']-np.interp(datas[2]['freq'],datas[2]['freq'],vmag_background))
else:
    bx1.scatter(datas[2]['freq'],datas[2]['vx'])
    bx2.scatter(datas[2]['freq'],datas[2]['vy'])
    bx3.scatter(datas[2]['freq'],datas[2]['vmag']*datas[2]['vamp'])
"""


#center around res freq
fig3 = plt.figure()
zx = fig3.add_subplot(1, 1, 1)
for i in range(len(datas)):
    # if i < 7 and i>0:
        # zx.scatter(datas[i]['freq'],datas[i]['vmag']*datas[i]['vamp'],label=filenames[i]+'Q='+str(int(fits[i][1])))
    if int(filenames[i][8])>4 and int(filenames[i][8])<8:
        zx.scatter(datas[i]['freq'],datas[i]['vmag'],label=filenames[i]+'Q='+str(int(fits[i][1])))
zx.legend()  
zx.set_xlabel('Frequency from resonance peak (kHz)')
zx.set_ylabel('Voltage Magnitude (mV)')
zx.set_xlim(2500,3500)
d = 20
zx.set_xlim(fits[0][0]-d,fits[0][0]+d)



#TURNs plot
# fig4 = plt.figure(constrained_layout = True)
# yx = fig4.add_subplot(1, 1, 1)
# turns = []
# peaks = []
# for i in range(len(datas)):
    
#     turns.append(datas[i]['turns'])
#     peaks.append(fits[i][0])

# # yx.legend()
# sorted_turns,sorted_peaks = cosort_lists(turns,peaks)

# yx.plot(sorted_turns,sorted_peaks,c='blue')
# yx.set_xlabel('Turns ()')
# yx.set_ylabel('Resoance Peak (kHz)')
# d = 20
# yx.set_xlim(fits[0][0]-d,fits[0][0]+d)
# def line(x,a,b):
#     return a + b*x
# def linear_fit(x_data,y_data):
#     y_dif = (y_data[-1]-y_data[0])
#     x_dif = (x_data[-1]-x_data[0])
#     slope = y_dif/x_dif
#     guesses = [y_data[0]-slope*x_data[0],slope]
#     print(guesses)
#     bestfit = optimize.curve_fit(line,x_data,y_data,guesses)
#     return bestfit[0]


# def quad_fit(x_data,y_data):
#     def quad(x,a,b,c):
#         return c + b*x + a*x**2
    # guesses3 = [fitted['vx'][0],1e-1,0]
    # pbounds3 = np.array([[-1e3,-1,-1],[1e3,1,1]]) # [[Lower bounds],[upper bounds]]


#50 ohm temrinator stuff
# fig6 = plt.figure(constrained_layout = True)
# cx1 = fig6.add_subplot(3, 1, 1)
# cx2 = fig6.add_subplot(3, 1, 2)
# cx3 = fig6.add_subplot(3, 1, 3)
# cx1.set_xlabel('Frequency (kHz)')
# cx2.set_xlabel('Frequency (kHz)')
# cx3.set_xlabel('Frequency (kHz)')
# cx1.set_ylabel('Vx (mV)')
# cx2.set_ylabel('Vx (mV)')
# cx3.set_ylabel('Voltage Magnitude (mV)')
# for i in range(3):
#     if np.abs(datas[i]['vx'][0])<300:
#         cx1.scatter(datas[i]['freq'],datas[i]['vx'])
#         cx2.scatter(datas[i]['freq'],datas[i]['vy'])
#         cx3.scatter(datas[i]['freq'],datas[i]['vmag']*datas[i]['vamp'])

# fig7 = plt.figure(constrained_layout = True)
# dx1 = fig7.add_subplot(3, 1, 1)
# dx2 = fig7.add_subplot(3, 1, 2)
# dx3 = fig7.add_subplot(3, 1, 3)
# dx1.set_xlabel('Frequency (kHz)')
# dx2.set_xlabel('Frequency (kHz)')
# dx3.set_xlabel('Frequency (kHz)')
# dx1.set_ylabel('Vx (mV)')
# dx2.set_ylabel('Vx (mV)')
# dx3.set_ylabel('Voltage Magnitude (mV)')
# for i in range(3):
#     if np.abs(datas[i]['vx'][0])>300:
#         dx1.scatter(datas[i]['freq'],datas[i]['vx'])
#         fit = np.polyfit(datas[i]['freq'],datas[i]['vx'],2)
#         dx1.plot(datas[i]['freq'],plot_polyfit(datas[i]['freq'],fit),c='red')
#         dx2.scatter(datas[i]['freq'],datas[i]['vy'])
#         fit = np.polyfit(datas[i]['freq'],datas[i]['vy'],1)
#         dx2.plot(datas[i]['freq'],plot_polyfit(datas[i]['freq'],fit),c='red')
#         print(fit)
#         # fit = linear_fit(datas[i]['freq'],datas[i]['vy'])
#         # print(fit)
#         # dx2.plot(datas[i]['freq'],line(datas[i]['freq'],*fit),c='red')
#         # dx2.scatter(datas[i]['freq'],datas[i]['vy']-line(datas[i]['freq'],*fit))
#         dx3.scatter(datas[i]['freq'],datas[i]['vmag']*datas[i]['vamp'])





# print(fits)
plt.show()