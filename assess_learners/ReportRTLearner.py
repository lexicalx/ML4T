"""
Test a learner.  (c) 2015 Tucker Balch
"""

import numpy as np
import math
import LinRegLearner as lrl
import RTLearner as rtl
import sys
import timeit

if __name__=="__main__":
    if len(sys.argv) != 2:
        print "Usage: python testlearner.py <filename>"
        sys.exit(1)
    inf = open(sys.argv[1])
    data = np.array([map(float,s.strip().split(',')) for s in inf.readlines()])

    # compute how much of the data is training and testing
    train_rows = int(0.6* data.shape[0])
    test_rows = data.shape[0] - train_rows

    # separate out training and testing data
    trainX = data[:train_rows,0:-1]
    trainY = data[:train_rows,-1]
    testX = data[train_rows:,0:-1]
    testY = data[train_rows:,-1]

    for leaf_size in range(1,50):
        # create a learner and train it
        learner = rtl.RTLearner(leaf_size,verbose = False) # create a LinRegLearner
        train_start = timeit.default_timer()
        learner.addEvidence(trainX, trainY)  # train it
        train_stop = timeit.default_timer()

        # evaluate in sample
        query_start = timeit.default_timer()
        predY = learner.query(trainX)  # get the predictions
        query_stop = timeit.default_timer()
        train_rmse = math.sqrt(((trainY - predY) ** 2).sum() / trainY.shape[0])
        train_c = np.corrcoef(predY, y=trainY)


        # evaluate out of sample
        predY = learner.query(testX)  # get the predictions
        test_rmse = math.sqrt(((testY - predY) ** 2).sum() / testY.shape[0])
        test_c = np.corrcoef(predY, y=testY)
        print "{},{},{},{},{},{},{}".format(leaf_size, train_rmse, train_c[0, 1], test_rmse, test_c[0, 1],(train_stop-train_start),(query_stop-query_start))
