import numpy as np


def test_run():
	#a = np.random.random((5,4))
	#print a.shape[0]
	#print a.shape[1]
	#print len(a.shape)		
	#print a.size
	#print a.dtype

	np.random.seed(693)
	a = np.random.randint(0,10,size=(5,4))
	print "Array:\n",a
	print "Sum of all elements:\n",a.sum()
	print "Sum of each row:\n",a.sum(axis=1)
	print "Sum of each column:\n",a.sum(axis=0)

	print "Max of each row:\n",a.max(axis=1)
	print "Min of each column:\n",a.min(axis=0)
	print "Mean of all elements:\n",a.mean()

if __name__ == "__main__":
	test_run()
