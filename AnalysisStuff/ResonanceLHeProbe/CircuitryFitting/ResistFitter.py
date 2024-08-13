import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize

L = 24e-6
R = 6.5

C1 = 1e-9/(1/.1+1/.33)#series
C2 = .22e-9#parallel
Z0 = 100
def real_Z(C2,omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    return R/A

def imag_Z(C1,C2,omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A-1/(omega*C1)

def imag_Z_parallel(C2,omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A

def imag_Z_series(C1,omega):
    return -1/(omega*C1)

def full_Z(omega, C1, C2, L, R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return R/A +1j*(omega*B/A-1/(omega*C1))

freq = np.linspace(1.5e6,2.5e6,1000)
C1s = np.linspace(.05e-9,.1e-9,8)


'''
#scan cap or rest to see relfection
Rs = np.linspace(6,7,11)
fig4 = plt.figure(constrained_layout = True)
ax1 = fig4.add_subplot(3, 1, 1)
bx1 = fig4.add_subplot(3, 1, 2)
cx1 = fig4.add_subplot(3, 1, 3)

ax1.set_xlabel('Frequency (Hz)')
bx1.set_xlabel('Frequency (Hz)')
cx1.set_xlabel('Frequency (Hz)')
ax1.set_ylabel('Real Reflection')
bx1.set_ylabel('Imag Reflection')
cx1.set_ylabel('Reflection Magnitude')

# cx1 = fig2.add_subplot(1, 1, 1)
# cx1.set_xlabel('Frequency (Hz)')
# cx1.set_ylabel('Impedance Magnitude (Ohm)')

# cx1.plot([freq[0],freq[-1]],[1,1])

# fig3 = plt.figure(constrained_layout = True)
# implot = fig3.add_subplot(1, 1, 1)

for C1 in C1s:
# for R in Rs:
    ZL = full_Z(2*np.pi*freq,C1,C2,L,R)
    
    z = ZL/Z0
    reflect = (z-1)/(z+1)
    # lbl_str = 'R = {}'.format(R)
    lbl_str = 'C1 = {}'.format(C1)
    
    ax1.plot(freq, np.real(reflect),label = lbl_str)
    bx1.plot(freq, np.imag(reflect),label = lbl_str)
    cx1.plot(freq, np.abs(reflect),label = lbl_str)
'''
    
fig5 = plt.figure(constrained_layout = True)
zx = fig5.add_subplot(1, 1, 1)
C1s = np.linspace(.03e-9,.2e-9,100)
m = np.zeros(len(C1s))
R = 15
for i, C1 in enumerate(C1s):
    ZL = full_Z(2*np.pi*freq,C1,C2,L,R)
    z = ZL/Z0
    reflect = (z-1)/(z+1)
    m[i] = np.min(np.abs(reflect))
zx.plot(C1s,m)
# cx1.legend()
# cx1.set_yscale('log')
# # C1 = C1s[0]
# ZL = full_Z(2*np.pi*freq,C1,C2,L,R)
# z = ZL/Z0
# reflect = (z-1)/(z+1)



'''
#Find best resistance

fig2 = plt.figure(constrained_layout = True)
ax = fig2.add_subplot(3, 1, 1)
bx = fig2.add_subplot(3, 1, 2)
cx = fig2.add_subplot(3, 1, 3)

ax.set_xlabel('Frequency (Hz)')
bx.set_xlabel('Frequency (Hz)')
cx.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Real Impedance (Ohm)')
bx.set_ylabel('Imag Impedance (Ohm)')
cx.set_ylabel('Impedance Magnitude (Ohm)')

# cx = fig2.add_subplot(1, 1, 1)
# cx.set_xlabel('Frequency (Hz)')
# cx.set_ylabel('Impedance Magnitude (Ohm)')

cx.plot([freq[0],freq[-1]],[100,100])

# fig3 = plt.figure(constrained_layout = True)
# implot = fig3.add_subplot(1, 1, 1)

for R in Rs:
    ZL = full_Z(2*np.pi*freq,C1,C2,L,R)
    # Z0 = 50
    # z = ZL/Z0
    # reflect = (z-1)/(z+1)
    lbl_str = 'R = {}'.format(R)
    
    # dx.set_xlabel('Frequency (Hz)')
    ax.plot(freq, real_Z(C2,omega=2*np.pi*freq,R=R),label = lbl_str)
    # ax.plot(freq,50+np.zeros(len(freq)))
    # bx.plot(freq, -imag_Z(C1,C2,omega=2*np.pi*freq,R=R),color='black',label = 'Negative')
    bx.plot(freq, imag_Z(C1,C2,omega=2*np.pi*freq,R=R),label = lbl_str)
    # implot.plot(freq, imag_Z(C1,C2,omega=2*np.pi*freq,R=R),label = lbl_str)
    cx.plot(freq, np.abs(ZL),label = lbl_str)
    # cx.plot(freq,50+np.zeros(len(freq)))
    # ax.set_yscale('log')
    # bx.set_yscale('log')
    
    # ax.set_title()
# ax.legend()
# bx.legend()
cx.legend()
cx.set_yscale('log')
'''


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
freq = np.linspace(1.5e6,2.5e6,10000)

def get_vmag_mins(Rs,A,C1=0.1407e-9,C2=.22e-9,L = 24e-6,Z0=100):
    freq = np.linspace(.5e6,3e6,1000)
    output = np.zeros(len(Rs))
    for i, R in enumerate(Rs):
        ZL = full_Z(2*np.pi*freq,C1,C2,L,R)/Z0
        reflect = (ZL-1)/(ZL+1)
        output[i] = A*np.min(np.abs(reflect))
    return output
A = 519.78853223#see fitVmagmin_v_cap.py

Rs = np.linspace(.5,20,100)

fig6 = plt.figure(constrained_layout = True)
ex = fig6.add_subplot(1, 1, 1)
ex.plot(Rs,get_vmag_mins(Rs,A,C1=0.1407e-9,C2=.22e-9))
ex.plot([Rs[0],Rs[-1]],[195.3,195.3])
ex.set_xlabel('Resistance (ohms)')
ex.set_ylabel('Minimum Voltage')

fig6 = plt.figure(constrained_layout = True)
ex = fig6.add_subplot(1, 1, 1)
ex.plot(Rs,get_vmag_mins(Rs,A,C1=1e-9/(1/.1+1/.33),C2=.22e-9))
ex.plot([Rs[0],Rs[-1]],[120,120])
ex.set_xlabel('Resistance (ohms)')
ex.set_ylabel('Minimum Voltage')

fig6 = plt.figure(constrained_layout = True)
ex = fig6.add_subplot(1, 1, 1)
ZL = full_Z(2*np.pi*freq,0.057e-9,.22e-9,L,4.2)/Z0
reflect = (ZL-1)/(ZL+1)
ex.plot(freq,A*np.abs(reflect))
# ex.plot([Rs[0],Rs[-1]],[120,120])
ex.set_xlabel('Resistance (ohms)')
ex.set_ylabel('Minimum Voltage')


fig6 = plt.figure(constrained_layout = True)
ex = fig6.add_subplot(1, 1, 1)

ZL = full_Z(2*np.pi*freq,1e-9/(1/.1+1/.33),.22e-9,L,6.85)/Z0
reflect = (ZL-1)/(ZL+1)
ex.plot(freq,A*np.abs(reflect))
# ex.plot([Rs[0],Rs[-1]],[120,120])
ex.set_xlabel('Resistance (ohms)')
ex.set_ylabel('Minimum Voltage')
plt.show()