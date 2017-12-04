import pandas as pd
from pandas import np
import numpy as np
from util import get_data, plot_data
import pandas as pd
import datetime as dt
import math
from marketsimcode import compute_portvals
import matplotlib.pyplot as plt

def sma(prices, window=14, min_periods=14):
    sma = prices.rolling(window=window, min_periods=min_periods,
                         center=False).mean()
    # sma.rename(columns={'JPM': 'SMA'}, inplace=True)
    return sma

def ema(prices, window=50, min_periods=0):
    ema = prices.ewm(span=window, min_periods=min_periods, adjust=False).mean()
    return ema


def macd(prices, fast_window=12, slow_window=26, signal_window=9):
    macd = ema(prices, window=fast_window) - ema(prices, window=slow_window)
    macd.rename(columns={'JPM': 'MACD'}, inplace=True)
    signal = ema(macd, window=signal_window)
    hist = macd - signal
    signal.rename(columns={'MACD': 'MACD_SIGNAL'}, inplace=True)
    hist.rename(columns={'MACD': 'MACD_HIST'}, inplace=True)
    return pd.concat([macd,signal,hist],axis=1)


def bbp(prices, window=14, min_periods=14):
    medium = sma(prices, window=window, min_periods=min_periods)
    rolling_std = prices.rolling(window=window,
                                 min_periods=min_periods).std()
    rolling_std.iloc[0] = 0.0  # We define the std of one element to be 0
    top_band = medium + (2 * rolling_std)
    bottom_band = medium - (2 * rolling_std)

    bband = prices.copy()
    # bband['Upper Band'] = top_band
    # bband['Lower Band'] = bottom_band

    bbp = (prices - bottom_band) / (top_band - bottom_band)
    # bbp['Upper band'] = 1.0
    # bbp['Lower band'] = 0.0
    # bbp.rename(columns={symbol: 'BBP'}, inplace=True)
    return bbp


def rsi(prices, window=14, min_periods=0):
    change = prices.diff()
    change.iloc[0] = 0.0  # Set gain/loss of first day to zero
    # Using arithmetic mean, not exponential smoothing here
    avg_up = (change.where(lambda x: x > 0, other=0.0)
                    .rolling(window=window, min_periods=min_periods)
                    .mean())
    avg_down = (change.where(lambda x: x < 0, other=0.0)
                      .abs()
                      .rolling(window=window, min_periods=min_periods)
                      .mean())
    rsiVal = avg_up / (avg_up + avg_down) * 100
    # If avg_up+avg_down = 0 the rsi should be around 50... I think
    rsiVal.replace(to_replace=[np.inf, np.NaN], value=50, inplace=True)
    if min_periods > 0:
        rsiVal[:min_periods-1] = np.NaN
    # rsi.rename(index='RSI', inplace=True)
        rsiVal.rename(columns={symbol, 'RSI'}, inplace=True)
    return rsiVal

def atr(df, col_labels=('Low', 'High', 'Close'), window=14):
    low = df[col_labels[0]]
    high = df[col_labels[1]]
    close = df[col_labels[2]]

    tr_1 = high - low
    tr_2 = (high - close.shift()).abs()  # High - Previous Close
    tr_3 = (low - close.shift()).abs()

    max_tr = pd.concat([tr_1, tr_2, tr_3], axis=1).max(axis=1)

    atr = pd.prices(0.0, index=max_tr.index, name='ATR')
    atr[:window-1] = np.NaN
    atr[window-1] = max_tr[:window].mean()

    for i in range(window, len(atr)):
        atr[i] = (atr[i - 1] * (window - 1) + max_tr[i]) / window

    return atr

def priceOverSMA(prices):
    sma_JPM = sma(prices)
    sma_JPM = sma_JPM.dropna()
    prices = prices.dropna()
    priceOverSma = prices / sma_JPM
    # priceOverSma['Upper Threshold'] = 1.05
    # priceOverSma['Lower Threshold'] = 0.95
    # priceOverSma.rename(columns={symbol: 'Price/SMA'}, inplace=True)

    # sma_JPM.rename(columns={symbol: 'SMA'}, inplace=True)
    # sma_JPM[symbol] = prices[symbol]
    # plot_fig(sma_JPM, symbol+' - SMA', (12, 6), 'Date', 'SMA', 'SMA-in-sample')

    return priceOverSma

def priceOverEMA(prices,window,type):
    ema_JPM = ema(prices,window=window)
    ema_JPM = ema_JPM.dropna()
    prices = prices.dropna()
    priceOverEma = prices / ema_JPM
    priceOverEma.rename(columns={'JPM': 'Price/EMA '+type}, inplace=True)

    ema_JPM.rename(columns={'JPM': 'EMA '+type}, inplace=True)
    ema_JPM['JPM'] = prices['JPM']
    # plot_fig(ema_JPM, 'JPM - EMA', (12, 6), 'Date', 'EMA '+type, 'priceOverEMA'+type+'-in-sample')

    return priceOverEma

def priceOverEMAClubbed(prices):
    priceOverEMAFast = priceOverEMA(prices, window=12, type='Fast')
    priceOverEMASlow = priceOverEMA(prices, window=26, type='Slow')
    priceOverEMAClubbed = pd.concat([priceOverEMAFast, priceOverEMASlow], axis=1)
    priceOverEMAClubbed['Upper Threshold'] = 1.1
    priceOverEMAClubbed['Lower Threshold'] = 0.8
    return priceOverEMAClubbed

def plot_fig(df,title,figsize,x_label,y_label, filename):
    ax = df.plot(title=title, fontsize=12, figsize=figsize)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.grid()
    plt.savefig(filename+'.png')

def plot_fig_macd(df, title, figsize, x_label, y_label, filename):
    # ax = df.plot(title=title, fontsize=12, figsize=figsize)
    ax = df['MACD_HIST'].plot(secondary_y=True)
    df[['MACD', 'MACD_SIGNAL']].plot(kind='bar', ax=ax)


    # ax2 = ax.twinx()
    # ax2.plot(ax.get_xticks(), df[['MACD', 'MACD_SIGNAL']].values)

    plt.grid()
    plt.savefig(filename + '.png')

if __name__ == "__main__":

    syms = ['JPM']
    sd = dt.datetime(2008, 1, 1)
    ed = dt.datetime(2009, 12, 31)
    dates = pd.date_range(sd, ed + dt.timedelta(days=1))
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices = prices.fillna(method='ffill', inplace=False)
    prices = prices.fillna(method='bfill', inplace=False)

    priceOverSMAValues = priceOverSMA(prices)
    priceOverEMAClubbed = priceOverEMAClubbed(prices)
    bband, bbp = bbands(prices)
    macdVal = macd(prices)
    ema_fast = ema(prices, window=12)
    ema_fast.rename(columns={'JPM': 'EMA Fast (12)'}, inplace=True)
    ema_slow = ema(prices, window=26)
    ema_slow.rename(columns={'JPM': 'EMA Slow(26)'}, inplace=True)
    ema = pd.concat([prices,ema_fast,ema_slow],axis=1)
    rsiV = rsi(prices)

    plot_fig(rsiV, 'JPM - RSI', (12, 6), 'Date', '', 'RSI-in-sample')
    plot_fig(macdVal, 'JPM - MACD', (12, 6), 'Date', '', 'MACD-in-sample')
    plot_fig(ema, 'JPM - EMA', (12, 6), 'Date', '', 'EMA-in-sample')
    plot_fig(priceOverEMAClubbed, 'JPM - Price over EMA', (12, 6), 'Date', 'Price over EMA', 'priceOverEma-in-sample')
    plot_fig(priceOverSMAValues,'JPM - Price over SMA',(12,6),'Date','Price over SMA','priceOverSma-in-sample')
    plot_fig(bbp, 'JPM - Bollinger Band Percentage', (12, 6), 'Date', 'BBP', 'BBP-in-sample')
    plot_fig(bband, 'JPM - Bollinger Bands', (12, 6), 'Date','','BBand-in-sample')
