import numpy as np
import math
import DTLearner
class BagLearner(object):

    def __init__(self, learner = DTLearner, kwargs= {"leaf_size":5}, bags = 10, boost = False,verbose = False):
        self.verbose = verbose
        self.kwargs = kwargs
        self.bags = bags
        self.boost = boost
        self.learner = learner
        self.learners = []
        for i in range(0,self.bags):
            self.learners.append(learner(**kwargs))

    def author(self):
        return 'vsrinath6' # replace tb34 with your Georgia Tech username

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        if self.boost:
            pass
        else:
            for learner in self.learners:
                random_index = np.random.randint(0,dataX.shape[0],dataX.shape[0])
                learner_dataX = dataX[random_index,:]
                learner_dataY = dataY[random_index]
                learner.addEvidence(learner_dataX,learner_dataY)


    def query(self,points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        y_pred = []
        for learner in self.learners:
            y_pred.append(learner.query(points))
        return np.mean(y_pred, axis=0)


if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
