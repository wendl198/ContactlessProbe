import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize

#this program is used to predict the impedance and voltage that results from given capacitance, resisitance, etc

L = 24e-6
R = 5.12
f = 1.5e6
omega = 2*np.pi*f

def real_Z(C2,omega=omega):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    return R/A

def real_Z_50(C2,omega=omega):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    return R/A-100

def imag_Z(C1,C2,omega=omega):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A-1/(omega*C1)

def imag_Z_omega(omega,C1,C2):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A-1/(omega*C1)

def imag_Z_partial(C2,omega=omega):
    A = (1-L*C2*omega**2)**2 + (R*C2*omega)**2
    B = L-(R**2*C2)-(C2*(L*omega)**2)
    return omega*B/A

# C2_guess = optimize.fsolve(real_Z_50,1e-9)[0]

# cs = np.logspace(-10,-5,1000)
# cs_small = np.linspace(4.69e-10,.46915e-9,10000)
# c_res = L/(R**2+(L*omega)**2)
# print(c_res)
C1_guess = .47e-9
C2_guess = .33e-9

A = (1-L*C2_guess*omega**2)**2 + (R*C2_guess*omega)**2
B = L-(R**2*C2_guess)-(C2_guess*(L*omega)**2)
C1_guess = A/B/omega**2


# freq_guess = 2*np.pi*optimize.fsolve(imag_Z_omega,1.5e6,args=(C1_guess,C2_guess))[0]
# print(freq_guess/1e6)#this can be weird if the imaginary part doesn't cross zero 
freq = np.linspace(.5e6,4e6,1000)

A = (1-L*C2_guess*omega**2)**2 + (R*C2_guess*omega)**2
B = L-(R**2*C2_guess)-(C2_guess*(L*omega)**2)
C1_guess = A/B/omega**2
# print(C1_guess)
ZL = real_Z(C2_guess,omega=2*np.pi*freq) +1j*imag_Z(C1_guess,C2_guess,omega=2*np.pi*freq)
Z0 = 100
z = ZL/Z0
reflect = (z-1)/(z+1)



fig2 = plt.figure(constrained_layout = True)
ax = fig2.add_subplot(2, 2, 1)
bx = fig2.add_subplot(2, 2, 2)
cx = fig2.add_subplot(2, 2, 3)
dx = fig2.add_subplot(2, 2, 4)
ax.set_xlabel('Frequency (Hz)')
bx.set_xlabel('Frequency (Hz)')
cx.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Real Impedance (Ohm)')
bx.set_ylabel('Imag Impedance (Ohm)')
cx.set_ylabel('Impedance Magnitude (Ohm)')
dx.set_xlabel('Frequency (Hz)')
ax.plot(freq, real_Z(C2_guess,omega=2*np.pi*freq))
ax.plot(freq,100+np.zeros(len(freq)))
bx.plot(freq, abs(imag_Z(C1_guess,C2_guess,omega=2*np.pi*freq)))
cx.plot(freq, np.abs(ZL))
cx.plot(freq,100+np.zeros(len(freq)))
dx.plot(freq,np.real(reflect),label='real')
dx.plot(freq,np.imag(reflect),label='imag')
dx.plot(freq,np.abs(reflect),label='mag')
dx.legend()
ax.set_yscale('log')
bx.set_yscale('log')
cx.set_yscale('log')
plt.show()