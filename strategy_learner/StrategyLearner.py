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

        priceOverSMAValues = priceOverSMA(symbol,prices)
        bbpValues = bbp(symbol,prices)
        rsiValues = rsi(symbol,prices)

        self.prices = prices.ix[sd:]
        self.symbol = symbol

        priceOverSMAValues = priceOverSMAValues.ix[sd:]
        priceOverSMAValues[symbol] = pd.qcut(priceOverSMAValues[symbol].values, 10).codes

        bbpValues = bbpValues.ix[sd:]
        bbpValues[symbol] = pd.qcut(bbpValues[symbol].values, 10).codes

        rsiValues = rsiValues.ix[sd:]
        rsiValues[symbol] = pd.qcut(rsiValues[symbol].values, 10).codes

        states = (priceOverSMAValues * 100) + (bbpValues * 10) + rsiValues * 1

        converged = False
        count = 0
        prev_total_reward = 0
        reward_match_count = 0
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
                # if net_position == 1:
                #     reward = 0
                # elif net_position == 2:
                #     # get daily return percetage
                #     reward = (prices.ix[day, symbol] / prices.ix[day - 1, symbol] - 1) - self.impact
                # elif net_position == 0:
                #     # get daily return percetage
                #     reward = -1 * (prices.ix[day, symbol] / prices.ix[day - 1, symbol] - 1 - self.impact)
                # total_reward += reward
                reward = self.getReward(net_position,day)
                total_reward += reward
                state = states.ix[day, symbol]
                action = self.learner.query(state, reward)
            count += 1
            total_time = time.clock() - start_time
            # print total_time
            prev_total_reward = total_reward
            if total_reward == prev_total_reward:
                reward_match_count += 1
                if reward_match_count == 5:
                    converged = True

    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol="IBM", \
                   sd=dt.datetime(2009, 1, 1), \
                   ed=dt.datetime(2010, 1, 1), \
                   sv=10000):

        lookback_dates = pd.date_range(sd - dt.timedelta(days=30), ed)

        prices = ut.get_data([symbol], lookback_dates)
        prices = prices.ix[:, [symbol]]

        priceOverSMAValues = priceOverSMA(symbol,prices)
        bbpValues = bbp(symbol,prices)
        rsiValues = rsi(symbol,prices)

        self.prices = prices.ix[sd:]
        self.symbol = symbol
        priceOverSMAValues = priceOverSMAValues.ix[sd:]
        priceOverSMAValues[symbol] = pd.qcut(priceOverSMAValues[symbol].values, 10).codes

        bbpValues = bbpValues.ix[sd:]
        bbpValues[symbol] = pd.qcut(bbpValues[symbol].values, 10).codes

        rsiValues = rsiValues.ix[sd:]
        rsiValues[symbol] = pd.qcut(rsiValues[symbol].values, 10).codes

        states = (priceOverSMAValues * 100) + (bbpValues * 10) + rsiValues * 1

        df_actions = priceOverSMAValues.copy()

        state = states.ix[0, symbol]
        action = self.learner.querysetstate(state)


        total_days = states.shape[0]
        total_reward = 0
        day = 0

        # SELL = 0
        # NOTHING = 1
        # BUY = 2
        #
        SHORT = 0
        NONE = 1
        LONG = 2

        net_position = NONE
        df_actions.ix[day, symbol] = self.addNewAction(net_position,day,action)
        # add action to dataframe
        # if action == BUY:
        #     if net_position == LONG:
        #         df_actions.ix[day, symbol] = 0.0
        #     elif net_position == NONE:
        #         df_actions.ix[day, symbol] = 1000.0
        #     elif net_position == SHORT:
        #         df_actions.ix[day, symbol] = 2000.0
        # elif action == NOTHING:
        #     if net_position == LONG:
        #         df_actions.ix[day, symbol] = -1000.0
        #     elif net_position == NONE:
        #         df_actions.ix[day, symbol] = 0.0
        #     elif net_position == SHORT:
        #         df_actions.ix[day, symbol] = 1000.0
        # elif action == SELL:
        #     if net_position == LONG:
        #         df_actions.ix[day, symbol] = -2000.0
        #     elif net_position == NONE:
        #         df_actions.ix[day, symbol] = -1000.0
        #     elif net_position == SHORT:
        #         df_actions.ix[day, symbol] = 0

        for day in range(1, total_days):

            # implement action
            net_position = action

            # if net_position == NONE:
            #     reward = 0
            # elif net_position == LONG:
            #     reward = (prices.ix[day, symbol] / prices.ix[day - 1, symbol] - 1) - self.impact
            # elif net_position == SHORT:
            #     reward = -1 * (prices.ix[day, symbol] / prices.ix[day - 1, symbol] - 1 - self.impact)
            # total_reward += reward
            total_reward += self.getReward(net_position, day)
            state = states.ix[day, symbol]

            action = self.learner.querysetstate(state)
            df_actions.ix[day, symbol] = self.addNewAction(net_position,day,action)
            # if action == BUY:
            #     if net_position == LONG:
            #         df_actions.ix[day, symbol] = 0.0
            #     elif net_position == NONE:
            #         df_actions.ix[day, symbol] = 1000.0
            #     elif net_position == SHORT:
            #         df_actions.ix[day, symbol] = 2000.0
            # elif action == NOTHING:
            #     if net_position == LONG:
            #         df_actions.ix[day, symbol] = -1000.0
            #     elif net_position == NONE:
            #         df_actions.ix[day, symbol] = 0.0
            #     elif net_position == SHORT:
            #         df_actions.ix[day, symbol] = 1000.0
            # elif action == SELL:
            #     if net_position == LONG:
            #         df_actions.ix[day, symbol] = -2000.0
            #     elif net_position == NONE:
            #         df_actions.ix[day, symbol] = -1000.0
            #     elif net_position == SHORT:
            #         df_actions.ix[day, symbol] = 0

        return df_actions

    def getReward(self,net_position,day):
        SHORT = 0
        NONE = 1
        LONG = 2
        reward = 0
        if net_position == NONE:
            reward = 0
        elif net_position == LONG:
            reward = (self.prices.ix[day, self.symbol] / self.prices.ix[day - 1, self.symbol] - 1) - self.impact
        elif net_position == SHORT:
            reward = -1 * (self.prices.ix[day, self.symbol] / self.prices.ix[day - 1, self.symbol] - 1 - self.impact)
        return reward

    def addNewAction(self, net_position, day, action):
        SELL = 0
        NOTHING = 1
        BUY = 2

        SHORT = 0
        NONE = 1
        LONG = 2
        shares = 0.0
        if action == BUY:
            if net_position == LONG:
                shares = 0.0
            elif net_position == NONE:
                shares = 1000.0
            elif net_position == SHORT:
                shares = 2000.0
        elif action == NOTHING:
            if net_position == LONG:
                shares = -1000.0
            elif net_position == NONE:
                shares = 0.0
            elif net_position == SHORT:
                shares = 1000.0
        elif action == SELL:
            if net_position == LONG:
                shares = -2000.0
            elif net_position == NONE:
                shares = -1000.0
            elif net_position == SHORT:
                shares = 0
        return shares

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