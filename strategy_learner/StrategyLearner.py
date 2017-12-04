"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch
"""

import datetime as dt
import pandas as pd
import util as ut
import QLearner as ql
import random
import time
import numpy as np
from indicators import sma,rsi,macd,bbp, priceOverSMA, priceOverEMAClubbed

class StrategyLearner(object):

    # constructor
    def __init__(self, verbose = False, impact=0.0):
        self.verbose = verbose
        self.impact = impact

    # this method should create a QLearner, and train it for trading
    def addEvidence(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,1,1), \
        sv = 10000):

        start_time = time.clock()

        self.learner = ql.QLearner(1000, 3, .2, .9, .98, .999)

        lookback_dates = pd.date_range(sd - dt.timedelta(days=30), ed)

        prices = ut.get_data([symbol], lookback_dates)
        prices = prices.ix[:, [symbol]]

        ## Get indicators with 14 days lookback period from sd
        priceOverSMARatio = priceOverSMA(symbol,prices)
        bbpValue = bbp(symbol,prices)
        rsiValue = rsi(symbol,prices)

        ## Get prices starting from sd
        prices = prices.ix[sd:]

        # discretize state
        priceOverSMARatio = priceOverSMARatio.ix[sd:]
        priceOverSMARatio[symbol] = pd.qcut(priceOverSMARatio[symbol].values, 10).codes

        bbpValue = bbpValue.ix[sd:]
        bbpValue[symbol] = pd.qcut(bbpValue[symbol].values, 10).codes

        rsiValue = rsiValue.ix[sd:]
        rsiValue[symbol] = pd.qcut(rsiValue[symbol].values, 10).codes

        states = (priceOverSMARatio * 100) + (bbpValue * 10) + rsiValue * 1

        converged = False
        count = 0
        while not converged:
            # setquerystate
            state = states.ix[0, symbol]
            action = self.learner.querysetstate(state)
            net_position = 1
            num_days = states.shape[0]
            total_reward = 0
            for day in range(1, num_days):
                # implement action
                net_position = action
                if net_position == 1:
                    reward = 0
                elif net_position == 2:
                    # get daily return percetage
                    reward = prices.ix[day, symbol] / prices.ix[day - 1, symbol] - 1
                elif net_position == 0:
                    # get daily return percetage
                    reward = -1 * (prices.ix[day, symbol] / prices.ix[day - 1, symbol] - 1)
                total_reward += reward
                state = states.ix[day, symbol]
                action = self.learner.query(state, reward)
            count += 1
            total_time = time.clock() - start_time
            # print total_time
            if total_time > 20:
                converged = True

    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol="IBM", \
                   sd=dt.datetime(2009, 1, 1), \
                   ed=dt.datetime(2010, 1, 1), \
                   sv=10000):

        lookback_dates = pd.date_range(sd - dt.timedelta(days=30), ed)

        price = ut.get_data([symbol], lookback_dates)
        price = price.ix[:, [symbol]]

        smaR = priceOverSMA(symbol,price)
        bbpV = bbp(symbol,price)
        rsiV = rsi(symbol,price)

        price = price.ix[sd:]

        # discretize state
        smaR = smaR.ix[sd:]
        smaR[symbol] = pd.qcut(smaR[symbol].values, 10).codes

        bbpV = bbpV.ix[sd:]
        bbpV[symbol] = pd.qcut(bbpV[symbol].values, 10).codes

        rsiV = rsiV.ix[sd:]
        rsiV[symbol] = pd.qcut(rsiV[symbol].values, 10).codes

        # state = (smaR*1000) + (bbp*100.0001) + (rsi*10) + mom*1
        states = (smaR * 100) + (bbpV * 10) + rsiV * 1

        action_df = smaR.copy()

        state = states.ix[0, symbol]
        action = self.learner.querysetstate(state)


        num_days = states.shape[0]
        total_reward = 0
        day = 0

        SELL = 0
        NOTHING = 1
        BUY = 2

        SHORT = 0
        NONE = 1
        LONG = 2

        net_position = NONE
        # add action to dataframe
        if action == BUY:
            if net_position == LONG:
                action_df.ix[day, symbol] = 0.0
            elif net_position == NONE:
                action_df.ix[day, symbol] = 1000.0
            elif net_position == SHORT:
                action_df.ix[day, symbol] = 2000.0
        elif action == NOTHING:
            if net_position == LONG:
                action_df.ix[day, symbol] = -1000.0
            elif net_position == NONE:
                action_df.ix[day, symbol] = 0.0
            elif net_position == SHORT:
                action_df.ix[day, symbol] = 1000.0
        elif action == SELL:
            if net_position == LONG:
                action_df.ix[day, symbol] = -2000.0
            elif net_position == NONE:
                action_df.ix[day, symbol] = -1000.0
            elif net_position == SHORT:
                action_df.ix[day, symbol] = 0

        for day in range(1, num_days):

            # implement action
            net_position = action

            if net_position == NONE:
                reward = 0
            elif net_position == LONG:
                # get daily return percetage
                reward = price.ix[day, symbol] / price.ix[day - 1, symbol] - 1
            elif net_position == SHORT:
                # get daily return percetage
                reward = -1 * (price.ix[day, symbol] / price.ix[day - 1, symbol] - 1)
            total_reward += reward

            state = states.ix[day, symbol]

            action = self.learner.querysetstate(state)

            # add action to dataframe
            if action == BUY:
                if net_position == LONG:
                    action_df.ix[day, symbol] = 0.0
                elif net_position == NONE:
                    action_df.ix[day, symbol] = 1000.0
                elif net_position == SHORT:
                    action_df.ix[day, symbol] = 2000.0
            elif action == NOTHING:
                if net_position == LONG:
                    action_df.ix[day, symbol] = -1000.0
                elif net_position == NONE:
                    action_df.ix[day, symbol] = 0.0
                elif net_position == SHORT:
                    action_df.ix[day, symbol] = 1000.0
            elif action == SELL:
                if net_position == LONG:
                    action_df.ix[day, symbol] = -2000.0
                elif net_position == NONE:
                    action_df.ix[day, symbol] = -1000.0
                elif net_position == SHORT:
                    action_df.ix[day, symbol] = 0

        return action_df


if __name__=="__main__":
    print "One does not simply think up a strategy"
    symbol = "IBM"
    sd = dt.datetime(2009, 1, 1)
    ed = dt.datetime(2010, 1, 1)
    lookback_dates = pd.date_range(sd - dt.timedelta(days=30), ed)

    price = ut.get_data([symbol], lookback_dates)
    price = price.ix[:, [symbol]]

    smaR = priceOverSMA(symbol, price)
    bbpV = bbp(symbol, price)
    rsiV = rsi(symbol, price)

    price = price.ix[sd:]

    # discretize state
    smaR = smaR.ix[sd:]
    smaR[symbol] = pd.qcut(smaR[symbol].values, 10).codes

    bbpV = bbpV.ix[sd:]
    bbpV[symbol] = pd.qcut(bbpV[symbol].values, 10).codes

    rsiV = rsiV.ix[sd:]
    rsiV[symbol] = pd.qcut(rsiV[symbol].values, 10).codes