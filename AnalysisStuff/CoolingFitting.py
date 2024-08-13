import numpy as np
import matplotlib.pyplot as plt
# matplotlib inline
plt.rcParams["font.family"] = "Times New Roman"
import pandas as pd


# filepath = '/Users/blake/Documents/ContactlessProbeData/FirstTestTime.csv'
filepath = '/Users/blake/Documents/ContactlessProbeData/IncompleteTime.csv'

probe_dat = pd.read_csv(filepath) #Retrieve data

Xdat = probe_dat.to_numpy()
print(Xdat.size)
# print(Xdat)
fitstart = 300
plotstart = 300
for i in range(Xdat.size):
    if Xdat[i,1] <= 78 or (Xdat[i,1] <= 80 and Xdat[i,1] >= Xdat[i-1,1]):
        fitend = i
        plotend = i
        break
# fitend = 2500
# plotend = 4000

fitorder = 1

# f = plt.figure(1)
# plt.title('Warming Data')
# plt.plot(Xdat[6000:,0]/60,Xdat[6000:,1])
# plt.xlabel('Time (min)')
# plt.ylabel('Temperature (K)')
# f.show()

#p = numpy.polyfit(x,y,degree)
# x[0]**n * p[0] + ... + x[0] * p[n-1] + p[n] = y[0]
p = np.polyfit(Xdat[fitstart:fitend,0]/60,np.log(Xdat[fitstart:fitend,1]-77.3),fitorder)

#for special characters:
#plt.title(r'$\sigma_i=15$')

print(p)

# g = plt.figure(2)
# plt.title('Cooling Data')
# plt.plot(Xdat[250:2500,0]/60,Xdat[250:2500,1])
# plt.xlabel('Time (min)')
# plt.ylabel('Temperature (K)')
# g.show()
# input()

plt.title('Cooling Data')
if fitorder == 1:
    plt.plot(Xdat[plotstart:plotend,0]/60,Xdat[plotstart:plotend,1],Xdat[plotstart:plotend,0]/60,77.3+np.exp(p[1]+p[0]*Xdat[plotstart:plotend,0]/60))
elif fitorder == 2:
    plt.plot(Xdat[plotstart:plotend,0]/60,Xdat[plotstart:plotend,1],Xdat[plotstart:plotend,0]/60,77.3+np.exp(p[2]+p[1]*Xdat[plotstart:plotend,0]/60+p[0]*(Xdat[plotstart:plotend,0]/60)**2))
plt.xlabel('Time (min)')
plt.ylabel('Temperature (K)')
plt.legend(['Data','Fit'])
plt.show()