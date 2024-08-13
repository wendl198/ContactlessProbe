import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize

#this program is used to help estimate initial capacitance values 
#for the resoance circuit such that the real part of the impedance 
#is close to the input impedance of the BNCs when the imaginary part of the impedance is 0

L = 24e-6
R = 6.5
f = 1.7e6
omega = 2*np.pi*f
guesses = [1,1]# in units of nF


def real_Z(C2,omega=omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    return R/A

def real_Z_100(C2,omega=omega,R = R):
    A = (1-L*C2*1e-9*omega**2)**2 + (R*C2*1e-9*omega)**2
    return R/A-100
def imag_Z(C1,C2,omega=omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A-1/(omega*C1)

def imag_Z_partial(C2,omega=omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A

def full_Z(omega, C1, C2, L, R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return R/A +1j*(omega*B/A-1/(omega*C1))

def reflection_coeff(omega, C1, C2, L, R, Z0=100):
    ZL = full_Z(omega, C1, C2,L,R)
    return (ZL/Z0-1)/(ZL/Z0+1)

def display_cap_pairs(freqs,L=24e-6,R=15,show_first = False):
    C1s = np.zeros((len(freqs),2))
    C2s = np.zeros((len(freqs),2))#there is an peak in the real impedance, and one value for c2 on each side of peak
    res_freqs = np.zeros(len(freqs))
    Bs = np.zeros((len(freqs),2))
    for i, freq in enumerate(freqs):
        omega = freq * 2 *np.pi
        C_max = 1e9/(L*omega**2)
        if (L*omega)**2/R<= 100:
            print('Resisitance is too high',omega,R,L,i)

        if i >0:
            C2s[i][0] = 1e-9*optimize.fsolve(real_Z_100,1e9*C2s[i-1][0],args=(omega,R),factor =1000)[0]
            C2s[i][1] = 1e-9*optimize.fsolve(real_Z_100,1e9*C2s[i-1][1],args=(omega,R),factor =1000)[0]
            
        else:
            a = 1
            while C2s[i][0] == 0 or C2s[i][0]>C_max*1e-9:
                C2s[i][0] = 1e-9*optimize.fsolve(real_Z_100,(1-np.exp(-a/4))*C_max,args=(omega,R),factor= 1000)[0]
                a+=1
                if a > 1000:
                    print(C_max,C2s[i])
                    C = np.logspace(np.log10(1e-11),np.log10(20e-9),1000)*1e9
                    fig1 = plt.figure(constrained_layout = True)
                    a1x = fig1.add_subplot(1, 1, 1)
                    a1x.plot(C,real_Z_100(C,omega,R))
                    a1x.set_xscale('log')
                    plt.show()
            a = 1
            while C2s[i][1] <= C_max*1e-9:
                C2s[i][1] = 1e-9*optimize.fsolve(real_Z_100,(1+np.exp(-a/2))*C_max,args=(omega,R),factor =1000)[0]
                a +=1
                if a > 1000:
                    print(C_max,C2s[i])
                    C = np.logspace(np.log10(1e-11),np.log10(20e-9),1000)*1e9
                    fig1 = plt.figure(constrained_layout = True)
                    a1x = fig1.add_subplot(1, 1, 1)
                    a1x.plot(C,real_Z_100(C,omega,R))
                    a1x.set_xscale('log')
                    plt.show()
        
        for j in range(2):#calc C1s from C2s
            A = (1-L*C2s[i][j]*omega**2)**2 + (R*C2s[i][j]*omega)**2
            B = L-(R**2*C2s[i][j])-(C2s[i][j]*(L*omega)**2)
            C1s[i][j] = A/B/omega**2
            #calc other stuff
            
            Bs[i][j] = B
        res_freqs = np.sqrt(1/(L*C2s[0]))/(2*np.pi)


        if (i == 0 or i == len(freqs)-1) and show_first:
            C = np.logspace(np.log10(1e-11),np.log10(20e-9),1000)*1e9
            fig1 = plt.figure(constrained_layout = True)
            a1x = fig1.add_subplot(1, 1, 1)
            a1x.plot(C,real_Z_100(C,omega,R))
            a1x.set_xscale('log')

    fig = plt.figure(constrained_layout = True)
    # ax = fig.add_subplot(1, 1, 1)
    ax = fig.add_subplot(2, 1, 1)
    bx = fig.add_subplot(2, 1, 2)
    ax.plot(freqs,C1s[:,0]*1e12,label='Series Capacitor')
    ax.plot(freqs,C2s[:,0]*1e12,label='Parallel Capacitor')
    ax.legend()
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Capacitance (pF)')
    bx.plot(freqs,C1s[:,1]*1e12,label='Series Capacitor')
    bx.plot(freqs,C2s[:,1]*1e12,label='Parallel Capacitor')
    bx.legend()
    bx.set_xlabel('Frequency (Hz)')
    bx.set_ylabel('Capacitance (pF)')

    # bx.plot(freqs,Bs,label='Parallel Capacitor')
    # bx.set_xlabel('Frequency (Hz)')
    # bx.set_ylabel('B Value')

# C1_guess = optimize.fsolve(imag_Z,1e-9,args=C2_guess)[0]
# print(C1_guess,C2_guess)
# print(imag_Z_partial(4.69070386e-10))
# res_freq_range = np.linspace(5e5,4e6,100)
# C2s = np.zeros(len(res_freq_range))
# for i, freq in enumerate(res_freq_range):
#     if i == 0:
#         C2s[i] = 1e-9*optimize.fsolve(real_Z_100,.5,args=(freq*2*np.pi))[0]
#     else:
#         C2s[i] = 1e-9*optimize.fsolve(real_Z_100,C2s[i-1]*1e9,args=(freq*2*np.pi))[0]

# fig1 = plt.figure(constrained_layout = True)
# ax = fig1.add_subplot(1, 1, 1)
# ax.plot(res_freq_range,C2s)
# ax.plot(res_freq_range,4.17e-10+np.zeros(len(res_freq_range)))

cs = np.logspace(-10,-5,1000)
cs_small = np.linspace(4.69e-10,.46915e-9,10000)
# c_res = L/(R**2+(L*omega)**2)
# print(c_res)

freq = np.linspace(1e6,4e6,1000)
C2_guess = 1e-9*optimize.fsolve(real_Z_100,.2)[0]


A = (1-L*C2_guess*omega**2)**2 + (R*C2_guess*omega)**2
B = L-(R**2*C2_guess)-(C2_guess*(L*omega)**2)
# print(A,B)
C1_guess = A/B/omega**2
# print(2*np.pi*freq,C1_guess,C2_guess,L,R)
ZL = full_Z(2*np.pi*freq,C1_guess,C2_guess,L,R)
Z0 = 100
z = ZL/Z0
reflect = (z-1)/(z+1)
# reflect = -(Z0-ZL)/(Z0+ZL)

# fig = plt.figure(constrained_layout = True)
# ax = fig.add_subplot(2, 1, 1)
# bx = fig.add_subplot(2, 1, 2)
# ax.plot(cs,real_Z(cs))
# ax.plot(cs,100+np.zeros(len(cs)),label = 'Real Part')
# ax.plot(cs,abs(imag_Z(cs,C2_guess)),label = 'Imaginary Part')
# ax.plot(cs,abs(imag_Z_partial(cs)),label = 'Imaginary Part')
# bx.plot(cs_small,abs(imag_Z_partial(cs_small)),label = 'Imaginary Part')
# ax.plot(freq,abs(imag_Z(C1_guess,C2_guess,omega=2*np.pi*freq)),label = 'Imaginary Part')
# bx.plot(freq,abs(imag_Z(C1_guess,C2_guess,omega=2*np.pi*freq)),label = 'Imaginary Part')

# # bx.set_yscale('log')
# # ax.set_xscale('log')
# # # ax.set_yscale('log')
# # # ax.legend()
# # ax.set_xlabel('Frequency (Hz)')
# # bx.set_xlabel('Frequency (Hz)')
# # ax.set_ylabel('Imaginary Part of Impedance (Ohm)')
# # bx.set_ylabel('Imaginary Part of Impedance (Ohm)')
# # C1_guess = .47e-9
# # C2_guess = .33e-9

fig2 = plt.figure(constrained_layout = True)
ax = fig2.add_subplot(3, 1, 1)
bx = fig2.add_subplot(3, 1, 2)
cx = fig2.add_subplot(3, 1, 3)
# dx = fig2.add_subplot(2, 2, 4)
ax.set_title('Impedance')
ax.set_xlabel('Frequency (MHz)')
bx.set_xlabel('Frequency (MHz)')
cx.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Real Part (Ohm)')
bx.set_ylabel('Imag Part (Ohm)')
cx.set_ylabel('Magnitude (Ohm)')

ax.plot(freq/1e6, real_Z(C2_guess,omega=2*np.pi*freq))
bx.plot(freq/1e6, imag_Z(C1_guess,C2_guess,omega=2*np.pi*freq))
cx.plot(freq/1e6, np.abs(ZL))

ax.plot(1e-6*freq[np.argmin(np.abs(ZL))]*np.ones(2),[np.max(real_Z(C2_guess,omega=2*np.pi*freq)),np.min(real_Z(C2_guess,omega=2*np.pi*freq))])
bx.plot(1e-6*freq[np.argmin(np.abs(ZL))]*np.ones(2),[np.max(imag_Z_partial(C2_guess,omega=2*np.pi*freq)),np.min(imag_Z_partial(C2_guess,omega=2*np.pi*freq))])
cx.plot(1e-6*freq[np.argmin(np.abs(ZL))]*np.ones(2),[np.max(ZL),100])

ax.plot(freq/1e6,100+np.zeros(len(freq)))
bx.plot([freq[0]/1e6,freq[-1]/1e6],[0,0])
cx.plot(freq/1e6,100+np.zeros(len(freq)))




ax.set_yscale('log')
# bx.set_yscale('log')
cx.set_yscale('log')



# fig3 = plt.figure(constrained_layout = True)
# dx = fig3.add_subplot(3, 1, 1)
# ex = fig3.add_subplot(3, 1, 2)
# fx = fig3.add_subplot(3, 1, 3)
# dx.plot(freq,np.real(reflect),label='real')
# ex.plot(freq,np.imag(reflect),label='imag')
# fx.plot(freq,np.abs(reflect),label='mag')
# dx.set_xlabel('Frequency (Hz)')
# ex.set_xlabel('Frequency (Hz)')
# fx.set_xlabel('Frequency (Hz)')
# dx.set_ylabel('Real Part')
# ex.set_ylabel('Imag Part')
# fx.set_ylabel('Magnitude')
# dx.set_title('Reflection Coefficent Simulation for C_ser = '+ str(round(C1_guess*1e12,0))+ 'pf, C_par = '+ str(round(C2_guess*1e12,0))+'pf')


# bx.plot(freq, real_Z(C2_guess,omega=2*np.pi*freq))
# cx.plot(freq, imag_Z(C1_guess,C2_guess,omega=2*np.pi*freq))
# dx.plot(freq, abs(imag_Z(C1_guess,C2_guess,omega=2*np.pi*freq)))

# dx.set_yscale('log')
# print(C1_guess,C2_guess)

# if no series cap
fig4 = plt.figure(constrained_layout = True)
ax4 = fig4.add_subplot(3, 1, 1)
bx4 = fig4.add_subplot(3, 1, 2)
cx4 = fig4.add_subplot(3, 1, 3)
ax4.set_title('Impedance')
ax4.set_xlabel('Frequency (MHz)')
bx4.set_xlabel('Frequency (MHz)')
cx4.set_xlabel('Frequency (MHz)')
ax4.set_ylabel('Real Part (Ohm)')
bx4.set_ylabel('Imag Part (Ohm)')
cx4.set_ylabel('Magnitude (Ohm)')
ax4.plot(freq/1e6, real_Z(C2_guess,omega=2*np.pi*freq))
bx4.plot(freq/1e6, imag_Z_partial(C2_guess,omega=2*np.pi*freq))
cx4.plot(freq/1e6, np.abs(real_Z(C2_guess,omega=2*np.pi*freq))+1j*imag_Z_partial(C2_guess,omega=2*np.pi*freq))
ax4.plot(1e-6/2/np.pi/np.sqrt(L*C2_guess)*np.ones(2),[np.max(real_Z(C2_guess,omega=2*np.pi*freq)),np.min(real_Z(C2_guess,omega=2*np.pi*freq))])
bx4.plot(1e-6/2/np.pi/np.sqrt(L*C2_guess)*np.ones(2),[np.max(imag_Z_partial(C2_guess,omega=2*np.pi*freq)),np.min(imag_Z_partial(C2_guess,omega=2*np.pi*freq))])
cx4.plot(1e-6/2/np.pi/np.sqrt(L*C2_guess)*np.ones(2),[np.max(np.abs(real_Z(C2_guess,omega=2*np.pi*freq))+1j*imag_Z_partial(C2_guess,omega=2*np.pi*freq)),np.min(np.abs(real_Z(C2_guess,omega=2*np.pi*freq))+1j*imag_Z_partial(C2_guess,omega=2*np.pi*freq))])
bx4.plot([freq[0]/1e6,freq[-1]/1e6],[0,0])
ax4.set_yscale('log')
cx4.set_yscale('log')



#Find best cap values
C1_actual = 20e-12

display_cap_pairs(np.linspace(0.5e6,4e6,100),2.4e-5,6.5,False)
plt.show()

# pbounds = np.array([[max(min(datas[i]['freq']),500),1,-1,-1,-1,-1],[min(max(datas[i]['freq']),2500),1e4,1,1,1,1]]) # [[Lower bounds],[upper bounds]]
# bestfit = optimize.curve_fit(full_lorenzian_fit_with_skew,datas[i]['freq'],datas[i]['vmag'],guesses, bounds=pbounds)
# bestpars = bestfit[0]