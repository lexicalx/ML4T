"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import datetime as dt
import os
from util import get_data, plot_data


def author():
    return 'vsrinath6'  # replace tb34 with your Georgia Tech username.

def compute_portvals(orders_file = "./orders/orders.csv", start_val = 1000000, commission=9.95, impact=0.005):
    orders_df = pd.read_csv(orders_file, index_col='Date', parse_dates=True, na_values=['nan'])
    orders_df.sort_index(inplace=True)
    order_dates = list(orders_df.index.unique())
    # print "No of orders:{}".format(len(orders_df))
    unique_symbols = list(orders_df['Symbol'].unique())
    # print "Unique symbols:{}".format(unique_symbols)

    dates = pd.date_range(order_dates[0], order_dates[-1])
    prices_all = get_data(unique_symbols, dates)  # automatically adds SPY
    prices_all = prices_all[unique_symbols]
    prices_all.fillna(method='ffill', inplace=True)
    prices_all.fillna(method='bfill', inplace=True)
    prices_all = prices_all.assign(CASH=pd.Series(np.ones(len(prices_all))).values)
    # print prices_all

    trades = pd.DataFrame(0.00, index = prices_all.index, columns = unique_symbols)
    trades = trades.assign(CASH=pd.Series(np.zeros(len(trades))).values)

    for i,row in orders_df.iterrows():
        symbol = row['Symbol']
        if row['Order'] == 'BUY':
            trades.ix[i, symbol] += row['Shares']
            trades.ix[i, 'CASH'] -= (prices_all.ix[i, symbol] * row['Shares'])
        elif row['Order'] == 'SELL':
            trades.ix[i, symbol] -= row['Shares']
            trades.ix[i, 'CASH'] += (prices_all.ix[i, symbol] * row['Shares'])
        trades.ix[i, 'CASH'] -= impact * prices_all.ix[i, symbol] * row['Shares']
        trades.ix[i, 'CASH'] -= commission
    # print trades

    holdings = trades.copy()
    holdings['CASH'][0] += start_val
    for x in range(1, len(holdings.index)):
        for symbol in unique_symbols:
            holdings[symbol][x] += holdings[symbol][x - 1]
        holdings['CASH'][x] += holdings['CASH'][x - 1]
    # print holdings

    value = prices_all * holdings
    portvals = value.sum(axis=1)
    # print portvals
    return portvals

def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters

    of = "./orders/orders-short.csv"
    sv = 1000000

    # Process orders
    portvals = compute_portvals(orders_file = of, start_val = sv)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]] # just get the first column
    else:
        "warning, code did not return a DataFrame"
    
    # Get portfolio stats
    # Here we just fake the data. you should use your code from previous assignments.
    start_date = dt.datetime(2008,1,1)
    end_date = dt.datetime(2008,6,1)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2,0.01,0.02,1.5]
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]

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

