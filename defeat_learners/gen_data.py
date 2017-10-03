"""
template for generating data to fool learners (c) 2016 Tucker Balch
"""

import numpy as np
import math

# this function should return a dataset (X and Y) that will work
# better for linear regression than decision trees
def best4LinReg(seed=5):
    np.random.seed(seed)
    X = np.random.uniform(low=-1, high=1, size=(100,3))
    Y = np.random.uniform(1,5)*X[:,0] + np.random.uniform(6,10)*X[:,1] + np.random.uniform(11,20)*X[:,2]
    return X, Y

def best4DT(seed=5):
    np.random.seed(seed)
    X = np.random.randint(low=0, high=10, size=(100, 3))
    Y = np.cos(X[:, 0]) + np.exp(X[:, 1])+ np.sin(X[:, 2])
    return X, Y

def author():
    return 'vsrinath6' #Change this to your user ID

if __name__=="__main__":
    print "they call me Tim."
