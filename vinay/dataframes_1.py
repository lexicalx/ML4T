import pandas as pd
import matplotlib.pyplot as plt

def test_run():
	df = pd.read_csv("../data/AAPL.csv")
	print df.head(1)
	print "--------"
	print df.tail(1)
	print "--------"
	print df['Close'].max()
	print "--------"
	print df['Adj Close'].mean()
	df[['Close','Adj Close']].plot()
	plt.show()

if __name__ == "__main__":
	test_run()

