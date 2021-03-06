import numpy as np

class DTLearner(object):

    def __init__(self, leaf_size=1, verbose = False):
        self.leaf_size = leaf_size
        self.verbose = verbose
        self.leaf_node = -1
        self.tree = None
        np.seterr(divide='ignore', invalid='ignore')

    def author(self):
        return 'vsrinath6' # replace tb34 with your Georgia Tech username

    def build_tree(self, dataX, dataY):
        if dataX.shape[0] <= self.leaf_size:
            return np.asarray([[self.leaf_node, np.mean(dataY), np.nan, np.nan]])
        elif np.all(dataY == dataY[0]):
            return np.asarray([[self.leaf_node, np.mean(dataY), np.nan, np.nan]])
        else:
            #Get corelation coefficients for all X to Y
            #Get best feature index based on corr_coefs
            corr_coefs = np.corrcoef(dataX, dataY, rowvar=False)
            corr_coefs = corr_coefs[corr_coefs.shape[0]-1,:-1]
            if np.any(np.isnan(corr_coefs)):
                if (self.verbose):
                    print "dataX - rows :{}".format(dataX.shape[0])
                    print "corr_coefs: {}".format(corr_coefs)
                best_feature_index = 0
            else:
                best_feature_index = np.nanargmax(corr_coefs)

            ## get split_val from median of best feature
            split_val = np.median(dataX[:,best_feature_index])

            if(self.verbose):
                print "dataX - rows :{}".format(dataX.shape[0])
                print "corr_coefs: {}".format(corr_coefs)
                print "best_feature_index :{}".format(best_feature_index)
                print "split_val :{}".format(split_val)

            # all X values are the same, then return leaf node with mean of y
            # np.all(dataX[:,best_feature_index] == dataX[0],best_feature_index)
            if np.all(dataX[:,best_feature_index] == dataX[0,best_feature_index]):
                if(self.verbose):
                    print dataX[:,best_feature_index]
                    print "++++++++++++++++++++++++++++"
                    print dataX[0, best_feature_index]
                    print "all rows of the best feature for X have same value. Returning leaf."
                return np.asarray([[self.leaf_node, np.mean(dataY), np.nan, np.nan]])


            left_tree_X = dataX[dataX[:, best_feature_index] <= split_val]
            left_tree_Y = dataY[dataX[:, best_feature_index] <= split_val]

            right_tree_X = dataX[dataX[:, best_feature_index] > split_val]
            right_tree_Y = dataY[dataX[:, best_feature_index] > split_val]

            if(self.verbose):
                print "==========================================="
                print "Splitting on {} at tree node gives {} left nodes and {} right nodes".format(split_val,len(left_tree_X),len(right_tree_X))

            #if median is not a good split, then use mean
            if len(left_tree_X)==0 or len(right_tree_X)==0:
                split_val = np.mean(dataX[:,best_feature_index])
                left_tree_X = dataX[dataX[:, best_feature_index] <= split_val]
                left_tree_Y = dataY[dataX[:, best_feature_index] <= split_val]

                right_tree_X = dataX[dataX[:, best_feature_index] > split_val]
                right_tree_Y = dataY[dataX[:, best_feature_index] > split_val]

                if(self.verbose):
                    print "Using mean - Splitting on {} at tree node gives {} left nodes and {} right nodes".format(
                        split_val, len(left_tree_X), len(right_tree_X))

                if len(left_tree_X) == 0 or len(right_tree_X) == 0:
                    if(self.verbose):
                        print("Tree not splitting for split_val {} for Y. Returning leaf").format(split_val)
                    return np.asarray([[self.leaf_node, np.mean(dataY), np.nan, np.nan]])

            ##Build left tree and then right tree
            left_tree = self.build_tree(left_tree_X,left_tree_Y)
            right_tree = self.build_tree(right_tree_X, right_tree_Y)
            # print "left_tree :{}".format(left_tree)
            root = [best_feature_index,split_val,1,left_tree.shape[0]+1]
            tree = np.vstack((root,left_tree,right_tree))
            return tree

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        self.tree = self.build_tree(dataX,dataY)
        if (self.verbose):
            print "==========================================="
            print "Tree size: {}".format(len(self.tree))
            print "Leaf size: {}".format(self.leaf_size)


    def get_y_pred(self, x_test):
        row = int(0)
        while self.is_not_leaf(row):
            row = int(row)
            attribute_index = int(self.tree[row,0])
            split_val = self.tree[row,1]
            x_test_attr_val = x_test[attribute_index]
            if x_test_attr_val <= split_val:
                row = row + self.tree[row, 2]
            else:
                row = row + self.tree[row, 3]
            if(self.verbose):
                print "-----------------------------------------"
                print "attribute_index:{}".format(attribute_index)
                print "split_val:{}".format(split_val)
                print "x_test_attr_val : {}".format(x_test_attr_val)
        y_pred_val = self.tree[int(row),1]
        return y_pred_val


    def is_not_leaf(self,row):
        return not (self.tree[int(row),0] == -1)
        
    def query(self,points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        num_points = points.shape[0]
        y_pred = np.empty(num_points)
        for point_index in range(0, num_points):
            y_pred[point_index] = self.get_y_pred(points[point_index])
        return y_pred


if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
