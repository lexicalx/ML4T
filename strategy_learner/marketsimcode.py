"""
Vinay Srinath - vsrinath6
"""

import pandas as pd
import numpy as np
import datetime as dt
import os
from util import get_data, plot_data
import math


def author():
    return 'vsrinath6'  # replace tb34 with your Georgia Tech username.

def compute_portvals(orders_df, start_val = 1000000, commission=9.95, impact=0.005, sd=dt.datetime(2010, 1, 1), ed=dt.datetime(2011, 12, 31)):
    # orders_df = pd.read_csv(orders_file, index_col='Date', parse_dates=True, na_values=['nan'])
    orders_df.sort_index(inplace=True)
    # order_dates = list(orders_df.index.unique())
    # print "No of orders:{}".format(len(orders_df))
    unique_symbols = list(orders_df['Symbol'].unique())
    # print "Unique symbols:{}".format(unique_symbols)

    dates = pd.date_range(sd, ed)
    prices_all = get_data(unique_symbols, dates)  # automatically adds SPY
    prices_all = prices_all[unique_symbols]
    prices_all.fillna(method='ffill', inplace=True)
    prices_all.fillna(method='bfill', inplace=True)
    prices_all = prices_all.assign(CASH=pd.Series(np.ones(len(prices_all))).values)
    # print prices_all

    trades = pd.DataFrame(0.00, index = prices_all.index, columns = unique_symbols)
    trades = trades.assign(CASH=pd.Series(np.zeros(len(trades))).values)

    for i,row in orders_df.iterrows():
        if  i in prices_all.index:
            symbol = row['Symbol']
            if row['Order'] == 'BUY':
                trades.ix[i, symbol] += row['Shares']
                trades.ix[i, 'CASH'] -= (prices_all.ix[i, symbol] * row['Shares'])
            elif row['Order'] == 'SELL':
                trades.ix[i, symbol] -= row['Shares']
                trades.ix[i, 'CASH'] += (prices_all.ix[i, symbol] * row['Shares'])
            trades.ix[i, 'CASH'] -= impact * prices_all.ix[i, symbol] * row['Shares']
            trades.ix[i, 'CASH'] -= commission
        else:
            print "Ignoring order with date:{} because it falls on a non-trading day".format(i)
    # print trades

    holdings = trades.copy()
    if len(holdings.index) > 0:
        holdings['CASH'][0] += start_val
        for x in range(1, len(holdings.index)):
            for symbol in unique_symbols:
                holdings[symbol][x] += holdings[symbol][x - 1]
            holdings['CASH'][x] += holdings['CASH'][x - 1]
    # print holdings

    value = prices_all * holdings
    portvals = value.sum(axis=1)
    # print portvals
    if len(portvals) == 0:
        portvals = [0]
    return portvals

def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters

    of = "./benchmark.csv"
    sv = 100000

    # Process orders
    portvals = compute_portvals(orders_file = of, start_val = sv, commission=0.0, impact=0.0, sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31))
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]] # just get the first column
    else:
        "warning, code did not return a DataFrame"

    print portvals
    # Get portfolio stats
    # Here we just fake the data. you should use your code from previous assignments.
    start_date = dt.datetime(2008, 1, 1)
    end_date = dt.datetime(2009, 12, 31)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2,0.01,0.02,1.5]
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]

    cum_ret = (portvals[-1] / portvals[0]) - 1

    dr = portvals.copy()
    dr[1:] = (portvals[1:] / portvals[:-1].values) - 1
    dr.ix[0] = 0
    dr = dr.drop(dr.index[0], inplace=False)

    avg_daily_ret = dr.mean()
    std_daily_ret = dr.std()
    sharpe_ratio = math.sqrt(252) * (avg_daily_ret - 0) / std_daily_ret
    # Compare portfolio against $SPX
    print "Date Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of SPY : {}".format(sharpe_ratio_SPY)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of SPY : {}".format(cum_ret_SPY)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of SPY : {}".format(std_daily_ret_SPY)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of SPY : {}".format(avg_daily_ret_SPY)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

if __name__ == "__main__":
    test_code()
