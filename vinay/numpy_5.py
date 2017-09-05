import numpy as np



def test_run():
	a = np.random.randint(0,10,size=(2,3))
	print a
	print "----------------"
	print a[:,2]
	print "----------------"
	print a[0,:]
	print "----------------"
	b = a
	a[0,:] = 1
	print a
	print "----------------"
	b[:,2] = 9
	print b
	print "----------------"
	a[:,2] = [4,6]
	print a


if __name__ == "__main__":
	test_run()

