import numpy as np
from numpy import linalg as LA
import cmath
import math
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

"""
I was trying to model the current in a cylinderical sample due to an AC mag field inducing eddy currents.
This is done much better in this paper: DOI: 10.1109/MAP.2017.27742060
Not sure if I got this to work.

This was motivated by a question from Dinesh. Is there more sample heating as the sample becomes more conductive?
The answer is complicated and thus why this exists. I think the answer is, there exists a maximum conductivity 
that is conductive enough to let current flow, but not too conductive such that the mag field is strongly screened,
and hardly penetrates the sample.

Further analysis to find what this resisitivity is interesting to me, because I dont have that answer and the information 
may be useful. Probably not too tricky to simulate either
"""


a = 1e-3#radius in meters
h = 1e-3#height in m
rho = 200e-8#resisitivty ohm meters (e-8 is uohm cm)
mu = 4e-7*np.pi#permitivity 
omega = 2 * np.pi * 677e3
H0 = 1

riz = 1000
sumcount = 30

skin_d = (2*rho/(mu*omega))**.5
k = 1j /(2*skin_d**2)

bottom = 0
for l in range(sumcount):
    buns = math.factorial(l)**-2*(k*a**2)**l
    bottom += buns
    # print(buns)
    # print(bottom)
bottom /= H0

r = np.linspace(0,a,riz)
magfield = np.zeros(riz, dtype=np.complex_)
current = np.zeros(riz, dtype=np.complex_)

def H_field(r):
    magsum = 0
    for l in range(sumcount):
        magsum += math.factorial(l)**-2*(k*r**2)**l
    return magsum
def Current(r):
    cursum = 0
    for l in range(sumcount):
        cursum += math.factorial(l+1)**(-2)*(k)**(l+1)*2*(l+1)*r[dr]**(2*l)
    return cursum
for dr in range(riz):
    magsum = 0
    cursum = 0
    for l in range(sumcount):
        magsum += math.factorial(l)**-2*(k*r[dr]**2)**l
        cursum += math.factorial(l+1)**(-2)*(k)**(l+1)*2*(l+1)*r[dr]**(2*l)
    # print(sum)
    magfield[dr] = magsum/bottom
    current[dr] = cursum/bottom
    # if r[dr]<0:
    #     current[dr] *= -1
# current[0]=0
# print(r)


from scipy.special import jv
b = (1-1j)/skin_d
# print(magfield-jv(0,r*b)/jv(0,a*b))
print(jv(0,r*b))

# power = 2*np.pi*h*rho*np.trapz(r*current**2)
# print(np.absolute(power))

# # print(np.absolute(magfield)*2**-.5)
# # print(np.absolute(current)*2**-.5)

# # fig,(ax1, ax3) = plt.subplots(2, 1,figsize = (5,10))
# fig,ax1 = plt.subplots(1, 1,figsize = (7,7))
# # ax1.plot(r/a,np.absolute(magfield))#*2**-.5)
# ax1.set_xlim(0,1)
# ax1.plot(r/a,np.real(magfield))
# ax1.plot(r/a,np.imag(magfield))
# ax1.plot(r/a,np.absolute(magfield))
# ax1.legend(['Real Part', 'Imaginary Part','Total Magnitude'])
# ax1.set_xlabel('r/Sample Radius')
# ax1.set_ylabel('Magnetic Field')
# ax1.set_title('Cylinderical Conductor')

# # ax2.plot(r[1:]/a,np.real(current[1:]))
# # ax2.plot(r[1:]/a,np.imag(current[1:]))
# # ax2.set_xlabel('r/Sample Radius')
# # ax2.set_ylabel('Average Current')
# # ax2.set_title('Mag Field')

# # print((np.absolute(current)*2**-.5)**2)
# # print(np.log(r[1:riz-2]/a))
# # print(np.log(r[1:riz-2]/a)/np.log((np.absolute(current[1:riz-2])*2**-.5)**2))
# # ax3.plot((r[1:riz-2]/a),((np.absolute(current[1:riz-2])*2**-.5)**2))
# # ax3.set_xlim(0,1)
# # ax3.set_xlabel('r/Sample Radius')
# # ax3.set_ylabel('Power Density')
# # ax3.set_title('Mag Field')


# fig,ax4 = plt.subplots(1, 1,figsize = (7,7))
# ax4.plot(r[1:]/a,np.real(current[1:]))
# ax4.plot(r[1:]/a,np.imag(current[1:]))
# ax4.plot(r[1:]/a,np.absolute(current[1:]))
# ax4.legend(['Real Part', 'Imaginary Part','Total Magnitude'])
# ax4.set_xlabel('r/Sample Radius')
# ax4.set_xlim(0,1)
# ax4.set_ylabel('Current Density')
# ax4.set_title('Cylinderical Conductor')
# plt.show()



# colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]  # R -> G -> B
# n_bins = [3, 6, 10, 100]  # Discretizes the interpolation into bins
# cmap_name = 'my_list'
# fig, axs = plt.subplots(2, 2, figsize=(6, 9))
# fig.subplots_adjust(left=0.02, bottom=0.06, right=0.95, top=0.94, wspace=0.05)
# for n_bin, ax in zip(n_bins, axs.flat):
#     # Create the colormap
#     cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bin)
#     # Fewer bins will result in "coarser" colomap interpolation
#     im = ax.imshow(Z, origin='lower', cmap=cmap)
#     ax.set_title("N bins: %s" % n_bin)
#     fig.colorbar(im, ax=ax)

# p = ax.imshow(np.absolute(NewX),extent=[0, a, 0, b])
div = 100
plotableH = np.ones([div+2,div+2],dtype=np.complex_)
full = 0
total = 0
for i in range(div+2):
    for j in range(div+2):
        total += 1
        if np.sqrt((i-(div+2)/2)**2 + (j-(div+2)/2)**2)>(div+2)/2:
            plotableH[i][j] = 0
        else:
            full += 1
print(full/total)
