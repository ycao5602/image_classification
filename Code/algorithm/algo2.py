# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 11:22:18 2018

@author: chenc
improves the accuracy from 0.8395 to 0.9235 0.9355 0.946
"""



# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
#from sklearn.datasets import load_iris
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV
from sklearn import svm
from scipy.spatial.distance import cdist
from scipy import exp
from sklearn.decomposition import IncrementalPCA as PCA
#from cvxopt import blas
#from cvxopt.base import matrix
#from random import sample
'''
class MidpointNormalize(Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))
'''    
dset=2

if dset==1:
    dataset = np.load('../input_data/mnist_dataset.npz')
    size_image=28
    dim_image=1 
else:
    dataset = np.load('../input_data/cifar_dataset.npz')
    size_image=32
    dim_image=3
#size_image=28
#dim_image=1

Xtr = dataset ['Xtr']
Str = dataset ['Str'].ravel()
Xts = dataset ['Xts']
Yts = dataset ['Yts'].ravel()
scaler = StandardScaler()
Xts = scaler.fit_transform(Xts.T).T
Xtr = scaler.fit_transform(Xtr.T).T
if dset==2:
    #Xtr=Xtr.reshape(10000,dim_image,size_image,size_image).transpose([0,2, 3, 1]).mean(3).reshape(10000,size_image*size_image)
    #Xts=Xts.reshape(2000,dim_image,size_image,size_image).transpose([0,2, 3, 1]).mean(3).reshape(2000,size_image*size_image)
    pca = PCA(n_components=100)
    pca.fit(Xtr)
    Xtr=pca.transform(Xtr)
    Xts=pca.transform(Xts)
    print(sum(pca.explained_variance_ratio_))


#Xts = scaler.fit_transform(Xts.T).T
#Xtr = scaler.fit_transform(Xtr.T).T
xplot=scaler.fit_transform(pca.inverse_transform(Xts).T).T
##1plt.jet()
plt.figure()
for i in range(0,30):
    image=xplot[i,].reshape(dim_image,size_image,size_image).transpose([1, 2, 0])
    plt.subplot(5, 6, i+1)
    plt.imshow(image[:,:,:],interpolation='bicubic')
    plt.title(Yts[i])
Y=Yts
Xts.shape

S=0.84#parameter from rhos

indices = np.random.choice(Xts.shape[0], 
                           int(Xts.shape[0]*0.8), replace=False)
#no dimension reduction 0.8179 0.765 classic model
gamma= 620/ (size_image**2 * Xtr.std())
def my_kernel(X, Y):
    """
    We create a custom kernel:
        should give 87% if it matches the original RBF kernel
    """
    
    if np.array_equal(X,Y):
        N = X.shape[0]
        M=(1-S)*np.ones((N,N))+S*np.eye(N)
    else:
        M=10
    
    pairwise_sq_dists = cdist(X, Y, 'sqeuclidean')
    K = exp(-gamma*pairwise_sq_dists)*M
    #sigma=(2*0.0087)**(-0.5)
    #X = matrix(X)
    #N,n = X.size
    #Q = matrix(0.0, (N,N))
    #ones = matrix(1.0, (N,1))
    #blas.syrk(X, Q, alpha = 1.0/sigma)
    #a = Q[::N+1]
    #blas.syr2(a, ones, Q, alpha = -0.5)  
    #Q = exp(Q)
    return K
# error on the training data and minimising the norm of the weights. It is analageous to the ridge parameter in ridge regression (in fact in practice there is little difference in performance or theory between linear SVMs and ridge regression, so I generally use the latter - or kernel ridge regression if there are more attributes than observations).
#For large values of C, the optimization will choose a smaller-margin hyperplane if that hyperplane does a better job of getting all the training points classified correctly.
search=1 #search for parameters
if search:
    C_range = np.logspace(2**-5,2**5, 3)
    gamma_range = np.logspace(2**-15,2**3, 4)
    param_grid = dict(gamma=gamma_range, C=C_range)
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2)
    grid = GridSearchCV(svm.SVC(), param_grid=param_grid, cv=cv)
    grid.fit(Xtr,Str)
    print("The best parameters are %s with a score of %0.2f"
          % (grid.best_params_, grid.best_score_))
    
clf = svm.SVC(C=2.4,gamma=0.000225)
clf.fit(Xtr,Str)
print(clf.score(Xtr,Str))
clf.score(Xts,Yts)