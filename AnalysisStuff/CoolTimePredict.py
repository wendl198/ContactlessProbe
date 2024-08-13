from math import log
import datetime
import math
import numpy as np
from scipy import optimize

def guesscooltime(t,T,T_final):
    t= t-t[0] #t must be numpy array
    def model(x,a,b):
        return a*math.e**(x*b)+77.3#a>0 and b<0 when cooling
    guesses1 = [T[0]-77.3,-1e-1]
    parameterlowerbounds1 = np.array([0,-1e1])# a is the intial temp value when t=0
    parameterupperbounds1 = np.array([3e2,0])
    pbounds1 = np.array([parameterlowerbounds1,parameterupperbounds1])
    bestfit = optimize.curve_fit(model,t,T,guesses1,bounds=pbounds1)
    bestpars1 = bestfit[0]
    # parametererr = np.sqrt(np.diag(bestfit[1]))
    #what to find t_0 in T_final = A * e^(b*t_0) + 77.3
    #t_o=ln[(T_final-77.3)/A]/b
    print(bestpars1)
    print(np.log((T_final-77.3)/bestpars1[0])/bestpars1[1])

fitorder = 1

currTemp = float(input('Current Temp = '))
if fitorder == 1:
    A = -0.11950928 #this was dertermined experimentally
    t = minutes=log(.7/(currTemp-77.3))/A
elif fitorder == 2:
    A = -1.97438605e-04#this was dertermined experimentally
    B = -1.04434771e-01#this was dertermined experimentally
    C = -log(.7/(currTemp-77.3))#C>0 when currTemp>78K
    t = (-B-(B**2-2*A*C)**.5)/(2*A)
print('Temp will reach 78k in',str(t),'minutes.')
finishtime = datetime.datetime.now()+datetime.timedelta(minutes=t)
print('or at',finishtime.strftime("%H:%M:%S.%f %d-%b-%Y"))