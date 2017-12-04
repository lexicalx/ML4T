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
from indicators import rsi,bbp, priceOverSMA

class StrategyLearner(object):

    # constructor
    def __init__(self, verbose = False, impact=0.0):
        self.verbose = verbose
        self.impact = impact
        self.SELL = 0
        self.NOTHING = 1
        self.BUY = 2

        self.SHORT = 0
        self.NONE = 1
        self.LONG = 2

    # this method should create a QLearner, and train it for trading
    def addEvidence(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,1,1), \
        sv = 10000):

        self.learner = ql.QLearner(num_states=(ed-sd).days, \
                                   num_actions=3, \
                                   alpha=0.2, \
                                   gamma=0.9, \
                                   rar=0.98, \
                                   radr=0.999, \
                                   dyna=0, \
                                   verbose=False)

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
        prev_total_reward = 0
        reward_match_count = 0
        while not converged:
            state = states.ix[0, symbol]
            action = self.learner.querysetstate(state)
            net_position = self.NONE
            total_days = states.shape[0]
            total_reward = 0
            for day in range(1, total_days):
                net_position = action
                reward = self.getReward(net_position,day)
                total_reward += reward
                state = states.ix[day, symbol]
                action = self.learner.query(state, reward)
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

        df_trades = priceOverSMAValues.copy()

        state = states.ix[0, symbol]
        action = self.learner.querysetstate(state)


        total_days = states.shape[0]
        total_reward = 0
        day = 0

        net_position = self.NONE
        df_trades.ix[day, symbol] = self.addNewAction(net_position,day,action)

        for day in range(1, total_days):
            net_position = action
            total_reward += self.getReward(net_position, day)
            state = states.ix[day, symbol]
            action = self.learner.querysetstate(state)
            df_trades.ix[day, symbol] = self.addNewAction(net_position,day,action)
        # print df_trades
        return df_trades

    def getReward(self,net_position,day):
        reward = 0
        if net_position == self.NONE:
            reward = 0
        elif net_position == self.LONG:
            reward = (self.prices.ix[day, self.symbol] / self.prices.ix[day - 1, self.symbol] - 1) - self.impact
        elif net_position == self.SHORT:
            reward = -1 * (self.prices.ix[day, self.symbol] / self.prices.ix[day - 1, self.symbol] - 1 - self.impact)
        return reward

    def addNewAction(self, net_position, day, action):
        shares = 0.0
        if action == self.BUY:
            # if net_position == self.LONG:
            #     shares = 0.0
            if net_position == self.NONE:
                shares = 1000.0
            elif net_position == self.SHORT:
                shares = 2000.0
        elif action == self.NOTHING:
            if net_position == self.LONG:
                shares = -1000.0
            # elif net_position == self.NONE:
            #     shares = 0.0
            elif net_position == self.SHORT:
                shares = 1000.0
        elif action == self.SELL:
            if net_position == self.LONG:
                shares = -2000.0
            elif net_position == self.NONE:
                shares = -1000.0
            # elif net_position == self.SHORT:
            #     shares = 0
        return shares

if __name__=="__main__":
    print "One does not simply think up a strategy"