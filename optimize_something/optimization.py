"""MC1-P2: Optimize a portfolio."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from util import get_data, plot_data
import scipy.optimize as spo
import math
from matplotlib.dates import DateFormatter

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def optimize_portfolio(sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), \
    syms=['GOOG','AAPL','GLD','XOM'], gen_plot=False):

    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # find the allocations for the optimal portfolio
    # note that the values here ARE NOT meant to be correct for a test case
  
    no_of_allocs = len(syms) 
    #print "no_of_allocs : {}".format(no_of_allocs) 
    #Borrowed from "Python for Finance" book - Chapter 11
    alloc_bounds = tuple((0, 1) for x in range(no_of_allocs))
    #Borrowed from "Python for Finance" book - Chapter 11
    alloc_constraints = ({'type': 'eq', 'fun': lambda x:  np.sum(x) - 1})

    guess = no_of_allocs * [1./no_of_allocs,]
    #print "guess : {}".format(guess)
    opts = spo.minimize(compute_portfolio_volatility, guess, args=(prices,), method='SLSQP', bounds=alloc_bounds, constraints=alloc_constraints)
    #print "Min volatility: {}".format(opts.fun)
    #print "allocs: {}".format(opts.x)
    allocs = opts.x
    cr, adr, sddr, sr, ev, port_val = compute_portfolio_stats(allocs, prices)

    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        port_val = port_val/port_val.ix[0]
        prices_SPY = prices_SPY.fillna(method='ffill',inplace=False)
        prices_SPY = prices_SPY.fillna(method='bfill',inplace=False)
        prices_SPY = prices_SPY/prices_SPY.ix[0]
        df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
        
        ax = df_temp.plot(title='Daily Portfolio Value and SPY', fontsize=12)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
        plt.savefig('plot.png')

        pass
    
    return allocs, cr, adr, sddr, sr

    
def compute_portfolio_volatility(allocs,\
    prices):
    return compute_portfolio_stats(allocs,prices)[2]


def compute_portfolio_stats(allocs,\
    prices,\
    sv=1000000,\
    rfr = 0.0, sf = 252.0):

    prices = prices.fillna(method='ffill',inplace=False)
    prices = prices.fillna(method='bfill',inplace=False)


    # Get daily portfolio value

    normed_prices = prices/prices.ix[0]
    alloced = allocs*normed_prices
    pos_vals = alloced*sv
    port_val = pos_vals.sum(axis=1)

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cr = (port_val[-1]/port_val[0])-1

    dr = port_val.copy()
    dr[1:] = (port_val[1:]/port_val[:-1].values)-1
    dr.ix[0] = 0
    dr = dr.drop(dr.index[0],inplace=False)

    adr = dr.mean()
    sddr = dr.std()

    sr = math.sqrt(sf)*(adr-rfr)/sddr

    ev = port_val[-1]

    return cr, adr, sddr, sr, ev, port_val


def test_code():
    # This function WILL NOT be called by the auto grader
    # Do not assume that any variables defined here are available to your function/code
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!

    start_date = dt.datetime(2008,6,1)
    end_date = dt.datetime(2009,6,1)
    symbols = ['IBM','X','GLD']

    # Assess the portfolio
    allocations, cr, adr, sddr, sr = optimize_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        gen_plot = True)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocations
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr

if __name__ == "__main__":
    # This code WILL NOT be called by the auto grader
    # Do not assume that it will be called
    test_code()
