def get_cylind_H(d,skin_depth,resolution):
    k = (1-1j)/skin_depth
    cylindH = np.ones([resolution+2,resolution+2],dtype=np.complex_)
    for i in range(1,resolution+1):
        for j in range(1,resolution+1):
            r = np.sqrt((i-(resolution+1)/2)**2 + (j-(resolution+1)/2)**2)*d/(resolution)
            if r<=d/2:
                cylindH[i][j] = jv(0,r*k)/jv(0,d/2*k)
    return cylindH

def get_cylind_H_2(d,skin_depth,resolution):
    k = (1-1j)/skin_depth
    cylindH = np.ones([resolution+2,resolution+2],dtype=np.complex_)
    for i in range(1,resolution+1):
        for j in range(1,resolution+1):
            r = np.sqrt((i-(resolution+1)/2)**2 + (j-(resolution+1)/2)**2)*d/(resolution+1)
            if r<=d/2:
                cylindH[i][j] = jv(0,r*k)/jv(0,d/2*k)
    return cylindH

def get_cylind_H_3(d,skin_depth,resolution):
    k = (1-1j)/skin_depth
    cylindH = np.ones([resolution+2,resolution+2],dtype=np.complex_)
    for i in range(1,resolution+1):
        for j in range(1,resolution+1):
            if ((i-(resolution+1)/2)**2 + (j-(resolution+1)/2)**2)*4<=resolution**2:
                cylindH[i][j] = jv(0,np.sqrt((i-(resolution+1)/2)**2 + (j-(resolution+1)/2)**2)*d/(resolution)*k)/jv(0,d/2*k)
    return cylindH

#below and above check speed and accuracy of get_cylind_H

rho = 1e-7
r = 1e-3
res = 200
skin_depth = get_skin_depth(rho)
k = (1 - 1j) / skin_depth
# H = 
# H_2 = get_cylind_H_2(r*2,skin_depth,200)

reses = np.arange(100,500,3)
diffs1 = np.zeros(len(reses))
diffs2 = np.zeros(len(reses))
actual = np.angle(2/r/k*jv(1,r*k)/jv(0,r*k)-1)
for i, res in enumerate(reses):
    diffs1[i] = np.angle(double_Integral(get_cylind_H(r*2,skin_depth,res),2*r)/(2*r)**2-1)-actual
    diffs2[i] = np.angle(double_Integral(get_cylind_H_2(r*2,skin_depth,res),2*r)/(2*r)**2-1)-actual


fig = plt.figure(constrained_layout = True, figsize=(4.5, 4.5))
ax = fig.add_subplot(1, 1, 1)
# ax.imshow(np.absolute(H))
# print(np.angle(2/r/k*jv(1,r*k)/jv(0,r*k)-1))
# print(np.angle(double_Integral(H,2*r)/(2*r)**2-1))
ax.plot(reses,abs(diffs1))
ax.plot(reses,abs(diffs2))
ax.legend(['Resolution','Resolution+1'])
ax.set_yscale('log')

iters = 300

t1 = time.time()
a = get_cylind_H(r*2,skin_depth,iters)
t2 = time.time()
b = get_cylind_H_3(r*2,skin_depth,iters)
t3 = time.time()
print(t2-t1,t3-t2)
fig = plt.figure(constrained_layout = True, figsize=(4.5, 4.5))
ax = fig.add_subplot(1, 1, 1)
a = ax.imshow(np.absolute(a)-np.absolute(b))
# print(np.angle(2/r/k*jv(1,r*k)/jv(0,r*k)-1))
# print(np.angle(double_Integral(H,2*r)/(2*r)**2-1))
fig.colorbar(a, ax=ax)

def get_shape_H_old(shape_data,s,skin_depth,resolution,H0=1):
    k=(1-1j)/skin_depth #k value 
    
    #This analysis is only useful if there are many more divisions per unit length than the inverse of 
    #the skin depth (Otherwise, valuable information is missed). This is 
    #the reason for increasing the resolution at small skin depths: div 
    #is res by default but becomes larger if the skin depth is sufficiently small.
    
    dx = s/(resolution) #stepsize: x direction
    # Because the input matrix shape_data must be square, dx=dy

    """This analysis solves the differential equation del^2(H)+k^2*H=0 over 
    an arbitary shaped sample. A second order approximation for H is used, which 
    is appropriate given the presence of the Laplacian."""

    k = (1+1j)/skin_depth
    dx = s/resolution #stepsize: x direction
    beta_x = 1/dx**2 #avoid repeated operations
    alpha_x = -2*beta_x+k**2/2
    # dy = s/resolution #stepsize: y direction
    Xmat = np.zeros([resolution,resolution],dtype=np.complex_) #Initialize A matrix
    print(np.absolute(k**2),beta_x)

    # corners
    Xmat[0][0] = alpha_x
    Xmat[resolution-1][resolution-1] = alpha_x

    #interior
    for i in range(1,resolution-1):
        Xmat[i][i]= alpha_x #alpha_x

        Xmat[i][i+1]= beta_x #beta_x
        Xmat[i][i-1]= beta_x #beta_x
        #this set the points to the right and left of the diagonal

    #remaining two exterior points
    Xmat[0][1] = beta_x
    Xmat[resolution-1][resolution-2] = beta_x

    C = np.zeros([resolution,resolution],dtype=np.complex_) #boundary conditions (The 
    #component of H parallel to the surface of the conductor is continuous 
    #provided there are no free surface currents.) 
    
    H_beta_x = -H0*beta_x
    k2 = k**2

    #corners
    if not(shape_data[0][0]):
        C[0][0] = 2*H_beta_x + k2
    else:
        C[0][0] = 2*H_beta_x
    if not(shape_data[resolution-1][0]):
        C[resolution-1][0] = 2*H_beta_x + k2
    else:
        C[resolution-1][0] = 2*H_beta_x
    if not(shape_data[0][resolution-1]):
        C[0][resolution-1] = 2*H_beta_x + k2
    else:
        C[0][resolution-1] = 2*H_beta_x
    if not(shape_data[resolution-1][resolution-1]):
        C[resolution-1][resolution-1] = 2*H_beta_x + k2
    else:
        C[resolution-1][resolution-1] = 2*H_beta_x
    

    #edges
    for i in range(1,resolution-1):
        if not(shape_data[0][i]):
            C[0][i] = H_beta_x + k2
        else:
            C[0][i] = H_beta_x
        if not(shape_data[resolution-1][i]):
            C[resolution-1][i] = H_beta_x + k2
        else:
            C[resolution-1][i] = H_beta_x
        if not(shape_data[i][0]):
            C[i][0] = H_beta_x + k2
        else:
            C[i][0] = H_beta_x
        if not(shape_data[i][resolution-1]):
            C[i][resolution-1] = H_beta_x + k2
        else:
            C[i][resolution-1] = H_beta_x
        
    #interior
    for i in range(1,resolution-1):
        for j in range(1,resolution-1):
            if shape_data[i][j]:
                C[i][j] = k2
    # print(Xmat,C)

    X = solve_sylvester(Xmat,Xmat,C)
                
    NewX= np.zeros([resolution+2,resolution+2],dtype=np.complex_) 
    for i in range(resolution+2): #This for loop defines the field at the surface 
        #of the conductor (It must be H0).
        
        for j in range(resolution+2):
            if ((i ==0) or (i==(resolution+1)) or (j ==0) or (j==(resolution+1))):
                NewX[i][j] =H0 
            else:
                NewX[i][j]=X[i-1][j-1]
    return NewX


# Check get_area function with circle

rho = 1e-7  # resistivity
# spacial_res = 400
iter = 12000
r = .5e-3  # define the radius of the circle
d=2*r
skin_depth = get_skin_depth(rho)
k = (1 - 1j) / skin_depth

# Set the circular mask

# fig = plt.figure(constrained_layout = True, figsize=(4.5, 4.5))
# ax = fig.add_subplot(1, 1, 1)
# ax.imshow(mask)
# print(get_area(mask,d)/(np.pi*r**2))
reses = np.arange(100,500,3)
diffs1 = np.zeros(len(reses))
diffs2 = np.zeros(len(reses))
actual = np.angle(2/r/k*jv(1,r*k)/jv(0,r*k)-1)
for k, res in enumerate(reses):
    mask = np.zeros((res+2, res+2))  # initialize the mask to ones
    for i in range(1,res+1):
        for j in range(1,res+1):
            if np.sqrt((i-(res+1)/2)**2 + (j-(res+1)/2)**2)*2 <= res: #this makes a circle
                mask[i, j] = 1 # ouinside is ones
    diffs1[k] = get_area(mask,d)/(np.pi*r**2)
    diffs2[k] = get_area_2(mask,d)/(np.pi*r**2)


fig = plt.figure(constrained_layout = True, figsize=(4.5, 4.5))
ax = fig.add_subplot(1, 1, 1)
# ax.imshow(np.absolute(H))
# print(np.angle(2/r/k*jv(1,r*k)/jv(0,r*k)-1))
# print(np.angle(double_Integral(H,2*r)/(2*r)**2-1))
ax.plot(reses,diffs1-1)
ax.plot(reses,diffs2-1)
ax.plot(reses,[0]*len(reses))




#check tri_mask area

fig = plt.figure(constrained_layout = True)
ax = fig.add_subplot(1, 1, 1)
# ax.plot(info)
ax.imshow(np.absolute(tri_mask))
print(get_area(tri_mask,sides_lengths[3])/(sides_lengths[3]**2*np.sqrt(3)/4)-1)
info = np.zeros(len(tri_mask))
for i, row in enumerate(tri_mask):
    info[i] = np.sum(row)
i = np.logical_not(info ==0)
print(len(info[i]),info.max()/2*np.sqrt(3))
# fig = plt.figure(constrained_layout = True)
# ax = fig.add_subplot(1, 1, 1)
# ax.plot(info)
# ax.imshow(np.absolute(tri_mask))