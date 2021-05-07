# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 16:25:14 2021

@author: JMDai
"""
import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sparse

mat = scipy.io.loadmat('Mtrans.mat')
M=mat['M']
M=np.array(M)
[nn,nn1]=np.shape(M)
X=np.zeros(nn)
X[3065]=1.0;

T=20 # number time steps 

#M=csr_matrix(M)


depth=np.loadtxt("odepth.dat")
olon=np.loadtxt("olon.dat")
olat=np.loadtxt("olat.dat")
#mask2=np.load("mask.dat")
islake_row=np.loadtxt("islake_row.dat")
islake_col=np.loadtxt("islake_col.dat")

islake_row=islake_row-1
islake_col=islake_col-1

#depth[np.isnan(depth)]=0

glc=np.loadtxt("GLcoast.dat")
fig = plt.figure(figsize=(10, 8))
lon=glc[:,0]
lat=glc[:,1]
plt.plot(lon, lat,color='black')
plt.xlim([np.amin(olon)-0.25, np.amax(olon)+0.25])
plt.ylim([np.amin(olat)-0.2, np.amax(olat)+0.2])
plt.title('Lake Ontario')
PD=np.ones(np.shape(depth))*0.0
PD[depth==0]=np.nan
mask=np.ones(np.shape(depth))
mask[depth==0]=0.0

PD[depth==0]=np.nan

M1=np.copy(M)
#M3=M
islake_row = islake_row.astype(int)
islake_col = islake_col.astype(int)

masking = (depth>0)

for i in range (1,T):
    t=sparse.csr_matrix(X)*sparse.csr_matrix(M1)
    M1=sparse.csr_matrix(M)*sparse.csr_matrix(M1)

    #PD[mask==1]=t
    #PD=np.insert(PD,islake, t)
    t=t.todense()
    #PD=np.where(mask==1, t, PD)
   # PD[mask==1]=t
   
    PD[islake_row,islake_col]=t
    #np.putmask(PD,masking,t) 
    
   # print(np.shape(PD))
    plt.pcolor(olon,olat,PD,cmap='BuGn')
    plt.savefig(f"test{i}.svg")
    plt.pause(0.05)


#M2=M1.todense()
#test=M2-M3
#len(depth[depth>0])










#plt.show()




#for i in range (1,T):
#    M3=np.matmul(M,M3)







