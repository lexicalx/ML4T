import numpy as np



def test_run():
	a = np.random.randint(0,10,size=(5))
	print "1d array:\n",a
	indices = np.array([1,1,2,3])
	print "Array values using indices:\n",a[indices]
	
	print "-------------------"
	a = np.random.randint(0,10,size=(2,3))
	print "Array:\n",a
	mean = a.mean()
	print "Mean:\n",mean
	print "Elements less than mean:\n",a[a<mean]
	
	print "-------------------"
	a[a<mean] = mean
	print "Array with elements less than mean replaced by mean:\n",a

	print "-------------------"
	print "Multiply by 2:\n",a*2
	print "-------------------"
	print "Divide by 2:\n",a/2

	b = np.random.randint(10,20,size=(2,3))
	print "-------------------"
	print "a Array:\n",a
	print "-------------------"
	print "b Array:\n",b
	print "-------------------"
	print "Adding a+b:\n",a+b
	print "-------------------"
	print "Subtracting b-a:\n",b-a
	print "-------------------"
	print "Multiplying a*b:\n",a*b
	print "-------------------"
	print "Dividing b/a:\n",b/a
	print "-------------------"
	#print "Matrix multiplication a.b\n",np.dot(a,b)

if __name__ == "__main__":
	test_run()

