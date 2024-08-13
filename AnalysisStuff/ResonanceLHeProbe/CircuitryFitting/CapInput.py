import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize

L = 24e-6
R = 16
R = 6.5
R = 4
R = 5.12
f = 1.5e6
omega = 2*np.pi*f

C1s = [.141e-9]#series
C2 = .22e-9#parallel

def real_Z(C2,omega=omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    return R/A

def imag_Z(C1,C2,omega=omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A-1/(omega*C1)

def imag_Z_parallel(C2,omega=omega,R = R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A

def imag_Z_series(C1,omega=omega):
    return -1/(omega*C1)

def full_Z(omega, C1, C2, L, R):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return R/A +1j*(omega*B/A-1/(omega*C1))

freq = np.linspace(1e6,3e6,1000)
C1s = np.linspace(.06e-9,.07e-9,11)
fig2 = plt.figure(constrained_layout = True)
# ax = fig2.add_subplot(3, 1, 1)
# bx = fig2.add_subplot(3, 1, 2)
# cx = fig2.add_subplot(3, 1, 3)

# ax.set_xlabel('Frequency (Hz)')
# bx.set_xlabel('Frequency (Hz)')
# cx.set_xlabel('Frequency (Hz)')
# ax.set_ylabel('Real Impedance (Ohm)')
# bx.set_ylabel('Imag Impedance (Ohm)')
# cx.set_ylabel('Impedance Magnitude (Ohm)')

cx = fig2.add_subplot(1, 1, 1)
cx.set_xlabel('Frequency (Hz)')
cx.set_ylabel('Impedance Magnitude (Ohm)')
cx.plot([freq[0],freq[-1]],[100,100])

for C1 in C1s:
    ZL = full_Z(2*np.pi*freq,C1,C2,L,R)
    # Z0 = 50
    # z = ZL/Z0
    # reflect = (z-1)/(z+1)
    lbl_str = 'C1 = {}'.format(round(C1,14))
    
    # dx.set_xlabel('Frequency (Hz)')
    # ax.plot(freq, real_Z(C2,omega=2*np.pi*freq),label = lbl_str)
    # ax.plot(freq,50+np.zeros(len(freq)))
    # bx.plot(freq, -imag_Z(C1,C2,omega=2*np.pi*freq),color='black',label = 'Negative')
    # bx.plot(freq, imag_Z(C1,C2,omega=2*np.pi*freq),label = lbl_str)
    
    cx.plot(freq, np.abs(ZL),label = lbl_str)
    # cx.plot(freq,50+np.zeros(len(freq)))
    # ax.set_yscale('log')
    # bx.set_yscale('log')
    
    # ax.set_title()
# ax.legend()
# bx.legend()
cx.legend()
cx.set_yscale('log')
C1 = C1s[0]
ZL = full_Z(2*np.pi*freq,0.05e-9,C2,L,4)
Z0 = 100
z = ZL/Z0
reflect = (z-1)/(z+1)


fig3 = plt.figure(constrained_layout = True)
dx = fig3.add_subplot(3, 1, 1)
ex = fig3.add_subplot(3, 1, 2)
fx = fig3.add_subplot(3, 1, 3)
dx.plot(freq,np.real(reflect),label='real')
ex.plot(freq,np.imag(reflect),label='imag')
fx.plot(freq,np.abs(reflect),label='mag')
dx.set_xlabel('Frequency (Hz)')
ex.set_xlabel('Frequency (Hz)')
fx.set_xlabel('Frequency (Hz)')
dx.set_ylabel('Real Part')
ex.set_ylabel('Imag Part')
fx.set_ylabel('Magnitude')

plt.show()