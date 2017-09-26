import numpy as np
import BagLearner as bl
import LinRegLearner as lrl
class InsaneLearner(object):

    def __init__(self, verbose = False):
        self.verbose = verbose

    def author(self):
        return 'vsrinath6' # replace tb34 with your Georgia Tech username

    def addEvidence(self,dataX,dataY):
        self.learner = bl.BagLearner(learner=bl.BagLearner, kwargs={'learner':lrl.LinRegLearner,'bags':20,'kwargs':{}}, bags=2,verbose= False)
        self.learner.addEvidence(dataX,dataY)

    def query(self,points):
        return self.learner.query(points)

if __name__=="__main__":
    print "the secret clue is 'zzyzx'"