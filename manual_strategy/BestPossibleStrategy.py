import numpy as np
from util import get_data, plot_data
import pandas as pd
import datetime as dt
import math
from marketsimcode import compute_portvals
import matplotlib.pyplot as plt

class BestPossibleStrategy(object):
    def __init__(self, verbose=False):
        self.verbose = verbose
        np.seterr(divide='ignore', invalid='ignore')

    def author(self):
        return 'vsrinath6'  # replace tb34 with your Georgia Tech username

    def testPolicy(self, symbol="AAPL", sd=dt.datetime(2010, 1, 1), ed=dt.datetime(2011, 12, 31), sv=100000):
        syms = [symbol]
        dates = pd.date_range(sd, ed+ dt.timedelta(days=1))
        prices_all = get_data(syms, dates)  # automatically adds SPY
        prices = prices_all[syms]  # only portfolio symbols
        prices = prices.fillna(method='ffill', inplace=False)
        prices = prices.fillna(method='bfill', inplace=False)

        cols = ['Date','Symbol','Order','Shares']
        bps_df = pd.DataFrame(columns=cols)
        bps_df = bps_df.set_index('Date')
        net_position = 0
        for i in range(prices.size-1):
            # print prices.index[i]
            # print prices.ix[prices.index[i],symbol]
            # print prices.ix[prices.index[i+1],symbol]
            # print "------------"
            curr_price = prices.ix[prices.index[i],symbol]
            tomorrow_price = prices.ix[prices.index[i+1],symbol]
            if tomorrow_price > curr_price:
                # bps_df.ix[prices.index[i],'Symbol'] = symbol
                # bps_df.ix[prices.index[i], 'Order'] = 'BUY'
                # bps_df.ix[prices.index[i], 'Shares'] = 1000
                if net_position == 0:
                    bps_df.ix[prices.index[i], 'Symbol'] = symbol
                    bps_df.ix[prices.index[i], 'Order'] = 'BUY'
                    bps_df.ix[prices.index[i], 'Shares'] = 1000
                    net_position += 1000
                if net_position == -1000:
                    bps_df.ix[prices.index[i], 'Symbol'] = symbol
                    bps_df.ix[prices.index[i], 'Order'] = 'BUY'
                    bps_df.ix[prices.index[i], 'Shares'] = 2000
                    net_position += 2000
            elif tomorrow_price < curr_price:
                if net_position == 0:
                    bps_df.ix[prices.index[i], 'Symbol'] = symbol
                    bps_df.ix[prices.index[i], 'Order'] = 'SELL'
                    bps_df.ix[prices.index[i], 'Shares'] = 1000
                    net_position -= 1000
                if net_position == 1000:
                    bps_df.ix[prices.index[i], 'Symbol'] = symbol
                    bps_df.ix[prices.index[i], 'Order'] = 'SELL'
                    bps_df.ix[prices.index[i], 'Shares'] = 2000
                    net_position -= 2000

            else:
                pass

        prices.to_csv("prices.csv")
        bps_df.to_csv("bps.csv")
        # print bps_df
        return bps_df



    def testBenchMark(self, symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31), sv=100000):
        benchmark_df = pd.DataFrame({'Date': ['2008-01-02'],
                                     'Symbol': ['JPM'],
                                     'Order':['BUY'],
                                     'Shares': [1000]})
        benchmark_df.set_index('Date', inplace=True)
        # print benchmark_df
        return benchmark_df

def compute_stats(portvals,sd,ed):
    cum_ret = (portvals[-1] / portvals[0]) - 1

    dr = portvals.copy()
    dr[1:] = (portvals[1:] / portvals[:-1].values) - 1
    dr.ix[0] = 0
    dr = dr.drop(dr.index[0], inplace=False)

    avg_daily_ret = dr.mean()
    std_daily_ret = dr.std()
    sharpe_ratio = math.sqrt(252) * (avg_daily_ret - 0) / std_daily_ret
    # Compare portfolio against $SPX
    print "Date Range: {} to {}".format(sd, ed)
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Final Portfolio Value: {}".format(portvals[-1])

def plot_portvals(benchmark_portvals,bps_portvals):
    benchmark_portvals = benchmark_portvals / benchmark_portvals.ix[0]
    bps_portvals = bps_portvals / bps_portvals.ix[0]
    df_temp = pd.concat([benchmark_portvals, bps_portvals], keys=['Benchmark', 'BPS'], axis=1)
    colors = ['#0000ff','#000000']
    ax = df_temp.plot(title='Benchmark and BPS', fontsize=12, color=colors)
    ax.set_xlabel('Date')
    ax.set_ylabel('Portfolio Value')
    plt.savefig('benchmarkVSbps-insample.png')

if __name__ == "__main__":
    bps = BestPossibleStrategy()

    sv = 100000
    sd = dt.datetime(2008, 1, 1)
    ed = dt.datetime(2009, 12, 31)

    print "------------------------------"
    print "BENCHMARK"
    benchmark_df = bps.testBenchMark()
    benchmark_portvals = compute_portvals(orders_df=benchmark_df, start_val=sv, commission=0.0, impact=0.0, sd=sd,
                                          ed=ed)
    if isinstance(benchmark_portvals, pd.DataFrame):
        benchmark_portvals = benchmark_portvals[benchmark_portvals.columns[0]]  # just get the first column
    else:
        "warning, code did not return a DataFrame"

    compute_stats(benchmark_portvals, sd, ed)

    print "------------------------------"
    print "BPS"
    bps_df = bps.testPolicy(symbol="JPM",sd=sd,ed=ed,sv=sv)
    bps_portvals = compute_portvals(orders_df=bps_df, start_val=sv, commission=0.0, impact=0.0, sd=sd,
                                          ed=ed)
    if isinstance(bps_portvals, pd.DataFrame):
        bps_portvals = bps_portvals[bps_portvals.columns[0]]  # just get the first column
    else:
        "warning, code did not return a DataFrame"

    compute_stats(bps_portvals, sd, ed)

    plot_portvals(benchmark_portvals,bps_portvals)
