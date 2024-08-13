import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import optimize
from scipy import interpolate


#this program calculates the mu(omega) to match Fig 4 from this paper: https://journals-aps-org.ezp2.lib.umn.edu/prb/pdf/10.1103/PhysRevB.50.488
#(Microwave response of anisotropic high-temperature-superconductor crystals C. E. Gough and N. J. Exon)
mu_0 = 4*np.pi*1e-7
def calc_mu(omega,rho_a,rho_c,length=2e-3,width=1e-3,tolerance = 1e-4):
    
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
    while n<50:
        alpha_n = np.sqrt(-1j*(omega*mu_0*(length/np.pi)**2/rho_c-1j*rho_a/rho_c*(length*n/width)**2))
        gamma_n = np.sqrt(-1j*(omega*mu_0*(width/np.pi)**2/rho_a-1j*rho_c/rho_a*n**2))

        change = (np.tan(np.pi*alpha_n/2)/alpha_n+np.tan(np.pi*gamma_n/2)/gamma_n)/n**2
        total_sum += change
        n += 2

    return total_sum*16/(np.pi)**3
    
def calc_power(omega,sigma_x,sigma_y,H_0,length=2e-3,width=1e-3,N_m=1,tolerance = 1e-4):
    mu = calc_mu(omega,sigma_x,sigma_y,length=length,width=width,tolerance = tolerance)
    return 1j*.5*omega*4*np.pi*1e-7*H_0*mu/(1+N_m*(mu-1))


omega = 1.8699e6*2*np.pi


rhos = np.linspace(4e-7,5e-6,4000)
mus = np.zeros(len(rhos),dtype=np.complex128)

a = 1.4e-3
for i, rho in enumerate(rhos):
    mus[i] = calc_mu(omega,rho,rho,a,a)


# fig4 = plt.figure(constrained_layout = True)
# ax1 = fig4.add_subplot(2, 1, 1)
# ax2 = fig4.add_subplot(2, 1, 2)
# ax1.set_xlabel('resisitivity')
# ax2.set_xlabel('resisitivity')
# ax1.set_ylabel('Real part')
# ax2.set_ylabel('Imaginary Part')
# ax1.plot(rhos,np.real(mus))
# ax2.plot(rhos,np.abs(np.imag(mus)))

#recreate plot from paper

rhos = np.logspace(-6.6,-4)
mus = np.zeros(len(rhos),dtype=np.complex128)
a = 1.4e-3
for i, rho in enumerate(rhos):
    mus[i] = calc_mu(omega,rho,rho,a,a)

mus2 = np.zeros(len(rhos),dtype=np.complex128)
mus3 = np.zeros(len(rhos),dtype=np.complex128)
coef = 1.1
a1 = a*coef
a2 = a/coef
for i, rho in enumerate(rhos):
    mus2[i] = calc_mu(omega,rho,rho,a1,a2)
    mus3[i] = calc_mu(omega,rho,rho,a2,a1)
fig4 = plt.figure(constrained_layout = True)
ax1 = fig4.add_subplot(1, 1, 1)

ax1.set_ylabel(r'Effective $\mu(\omega)$',fontsize = 16)
#rho in denom
ax1.set_xlabel(r'$\frac{\omega \mu_0 a^2}{\rho}$',fontsize = 20)
ax1.plot(mu_0*omega*a*a/rhos,np.real(mus),label = 'Real Part')
ax1.plot(mu_0*omega*a*a/rhos,np.abs(np.imag(mus)),label = 'Imaginary Part')
ax1.plot(mu_0*omega*a*a/rhos,np.real(mus2),label = 'Real Part2')
ax1.plot(mu_0*omega*a*a/rhos,np.abs(np.imag(mus2)),label = 'Imaginary Part2')
ax1.plot(mu_0*omega*a*a/rhos,np.real(mus3),label = 'Real Part3')
ax1.plot(mu_0*omega*a*a/rhos,np.abs(np.imag(mus3)),label = 'Imaginary Part3')
ax1.set_xlim(0,100)

#rho in num
# ax1.set_xlabel(r'$\frac{\rho}{\omega \mu_0 a^2}$',fontsize = 20)
# ax1.plot(rhos/(mu_0*omega*a*a),np.real(mus),label = 'Real Part')
# ax1.plot(rhos/(mu_0*omega*a*a),np.abs(np.imag(mus)),label = 'Imaginary Part')
# ax1.set_xlim(0,.5)

# ax1.set_ylim(0,1)
ax1.legend(fontsize=16)
ax1.tick_params(axis='both', which='major', labelsize=12)

plt.show()