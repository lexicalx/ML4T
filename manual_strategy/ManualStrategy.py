from indicators import rsi,macd,bbands, priceOverSMA, priceOverEMAClubbed
import numpy as np
from util import get_data, plot_data
import pandas as pd
import datetime as dt
import math
from marketsimcode import compute_portvals
import matplotlib.pyplot as plt

class ManualStrategy(object):
    def __init__(self, verbose=False):
        self.verbose = verbose
        np.seterr(divide='ignore', invalid='ignore')
        self.long_entry_x = []
        self.short_entry_x = []

    def author(self):
        return 'vsrinath6'  # replace tb34 with your Georgia Tech username

    def testPolicy(self, symbol="AAPL", sd=dt.datetime(2010, 1, 1), ed=dt.datetime(2011, 12, 31), sv=100000):
        syms = [symbol]
        dates = pd.date_range(sd- dt.timedelta(days=20), ed + dt.timedelta(days=1))
        prices_all = get_data(syms, dates)  # automatically adds SPY
        prices_SPY = prices_all['SPY']
        prices_SPY = prices_SPY.fillna(method='ffill', inplace=False)
        prices_SPY = prices_SPY.fillna(method='bfill', inplace=False)
        prices = prices_all[syms]  # only portfolio symbols
        prices = prices.fillna(method='ffill', inplace=False)
        prices = prices.fillna(method='bfill', inplace=False)

        cols = ['Date', 'Symbol', 'Order', 'Shares']
        ms_df = pd.DataFrame(columns=cols)
        ms_df = ms_df.set_index('Date')


        priceOverSMAValues = priceOverSMA(prices)
        # priceOverEMAClubbedValues = priceOverEMAClubbed(prices)
        bband, bbp = bbands(prices)
        rsiJPM = rsi(prices)
        rsiSPY = rsi(prices_SPY)

        prices = prices[prices.index >= sd]
        priceOverSMAValues = priceOverSMAValues[priceOverSMAValues.index >= sd]
        bbp = bbp[bbp.index >= sd]
        rsiJPM = rsiJPM[rsiJPM.index >= sd]
        rsiSPY = rsiSPY[rsiSPY.index >= sd]

        net_position = 0
        for i in range(prices.size-1):
            # print prices.index[i]
            # print prices.ix[prices.index[i],symbol]
            # print prices.ix[prices.index[i+1],symbol]
            # print "------------"
            i += 1
            priceOverSMAValue = priceOverSMAValues.ix[prices.index[i],'Price/SMA']
            priceOverSMAValuePrior = priceOverSMAValues.ix[prices.index[i-1], 'Price/SMA']
            bbpValue = bbp.ix[prices.index[i],'BBP']
            rsiJPMValue = rsiJPM.ix[prices.index[i], 'RSI']
            rsiSPYValue = rsiSPY.ix[prices.index[i], 'RSI']
            # print "index={},priceOverSMA={},bbp={},rsiJPM={},rsiSPY={}".format(prices.index[i],priceOverSMAValue,bbpValue,rsiJPMValue,rsiSPYValue)
            if priceOverSMAValue > 1.05 and bbpValue > 1 and rsiJPMValue > 60:
                self.short_entry_x.append(prices.index[i])
                if net_position == 0:
                    ms_df.ix[prices.index[i], 'Symbol'] = symbol
                    ms_df.ix[prices.index[i], 'Order'] = 'SELL'
                    ms_df.ix[prices.index[i], 'Shares'] = 1000
                    net_position -= 1000
                if net_position == 1000:
                    ms_df.ix[prices.index[i], 'Symbol'] = symbol
                    ms_df.ix[prices.index[i], 'Order'] = 'SELL'
                    ms_df.ix[prices.index[i], 'Shares'] = 2000
                    net_position -= 2000
            elif priceOverSMAValue < 0.95 and bbpValue > 0 and rsiJPMValue < 25:
                self.long_entry_x.append(prices.index[i])
                if net_position == 0:
                    ms_df.ix[prices.index[i], 'Symbol'] = symbol
                    ms_df.ix[prices.index[i], 'Order'] = 'BUY'
                    ms_df.ix[prices.index[i], 'Shares'] = 1000
                    net_position += 1000
                if net_position == -1000:
                    ms_df.ix[prices.index[i], 'Symbol'] = symbol
                    ms_df.ix[prices.index[i], 'Order'] = 'BUY'
                    ms_df.ix[prices.index[i], 'Shares'] = 2000
                    net_position += 2000
            # elif priceOverSMAValue >= 1 and priceOverSMAValuePrior < 1 and net_position>0:
            #     ms_df.ix[prices.index[i], 'Symbol'] = symbol
            #     ms_df.ix[prices.index[i], 'Order'] = 'SELL'
            #     ms_df.ix[prices.index[i], 'Shares'] = 1000
            #     net_position = 0
            # elif priceOverSMAValue <= 1 and priceOverSMAValuePrior > 1 and net_position<0:
            #     ms_df.ix[prices.index[i], 'Symbol'] = symbol
            #     ms_df.ix[prices.index[i], 'Order'] = 'BUY'
            #     ms_df.ix[prices.index[i], 'Shares'] = 1000
            #     net_position = 0
            else:
                pass

        prices.to_csv("prices.csv")
        ms_df.to_csv("ms.csv")
        # print bps_df
        return ms_df

    def testBenchMark(self, symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31), sv=100000):
        benchmark_df = pd.DataFrame({'Date': [sd],
                                     'Symbol': [symbol],
                                     'Order': ['BUY'],
                                     'Shares': [1000]})
        benchmark_df.set_index('Date', inplace=True)
        print benchmark_df
        # print benchmark_df
        return benchmark_df


def compute_stats(portvals, sd, ed):
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


def plot_portvals(self,benchmark_portvals, ms_portvals,type):
    benchmark_portvals = benchmark_portvals / benchmark_portvals.ix[0]
    ms_portvals = ms_portvals / ms_portvals.ix[0]
    df_temp = pd.concat([benchmark_portvals, ms_portvals], keys=['Benchmark', 'MS'], axis=1)
    colors = ['#0000ff', '#000000']
    ax = df_temp.plot(title='Benchmark and MS', fontsize=12, color=colors,figsize=(16,6))
    ax.set_xlabel('Date')
    ax.set_ylabel('Portfolio Value')

    for lx in self.long_entry_x:
        plt.axvline(x=lx, color = 'g')
    for sx in self.short_entry_x:
        plt.axvline(x=sx, color='r')
    plt.savefig('benchmarkVSms-'+type+'.png')


if __name__ == "__main__":
    ms = ManualStrategy()

    sv = 100000
    sd = dt.datetime(2008, 1, 1)
    ed = dt.datetime(2009, 12, 31)

    print "------------------------------"
    print "BENCHMARK"
    benchmark_df = ms.testBenchMark(symbol='JPM',sd=sd+ dt.timedelta(days=1),ed=ed,sv=sv)
    benchmark_portvals = compute_portvals(orders_df=benchmark_df, start_val=sv, commission=9.95, impact=0.005, sd=sd,
                                          ed=ed)
    if isinstance(benchmark_portvals, pd.DataFrame):
        benchmark_portvals = benchmark_portvals[benchmark_portvals.columns[0]]  # just get the first column
    else:
        "warning, code did not return a DataFrame"

    compute_stats(benchmark_portvals, sd, ed)

    print "------------------------------"
    print "MS"
    ms_df = ms.testPolicy(symbol="JPM", sd=sd, ed=ed, sv=sv)
    ms_portvals = compute_portvals(orders_df=ms_df, start_val=sv, commission=9.95, impact=0.005, sd=sd,
                                   ed=ed)
    if isinstance(ms_portvals, pd.DataFrame):
        ms_portvals = ms_portvals[ms_portvals.columns[0]]  # just get the first column
    else:
        "warning, code did not return a DataFrame"

    compute_stats(ms_portvals, sd, ed)

    plot_portvals(ms,benchmark_portvals, ms_portvals, 'insample')