import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.special import jv

def get_skin_depth(rho,frequency=100000):
    return (rho/(3.947841760435743e-06 *frequency))**.5

def get_cylind_chis(r,skin_depth):
    rk =(1-1j)*r/skin_depth
    return 2/rk*jv(1,rk)/jv(0,rk)-1

freqs = np.linspace(400e3,3e7,1000)
chis = np.zeros(len(freqs),dtype=np.complex128)
chis = get_cylind_chis(1.5e-3,get_skin_depth(2e-5,freqs))
fig = plt.figure(constrained_layout = True)
ax = fig.add_subplot(3, 1, 1)
ax.plot(freqs,np.real(chis),label ='Real Part of Chi')
ax.plot(freqs,np.imag(chis),label = 'Imaginary Part of Chi')
ax.set_xlabel('Freq (Hz)')
ax.set_ylabel('Chi')
ax.set_title('Chi behavior')
ax.set_xscale('log')

bx = fig.add_subplot(3, 1, 2)
bx.plot(freqs,np.abs(chis))
bx.set_xlabel('Freq')
bx.set_ylabel('Chi Magnitude')
bx.set_xscale('log')


cx = fig.add_subplot(3, 1, 3)
cx.plot(freqs,np.gradient(np.abs(chis)))
cx.set_xlabel('Freq')
cx.set_ylabel('Derivative of Chi Magnitude')
cx.set_xscale('log')
plt.show()