# data source
import yfinance as yf

# data analysis
import pandas as pd
import numpy as np

# datetime management
import datetime as dt
from pandas.tseries.offsets import BDay

# visualization
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.dates import date2num

def RunStrategy(ticker, start_date, end_date):

    cols = ['Open', 'High', 'Low', 'Close']

    df = yf.download(ticker, start_date, end_date)

    ################ HEIKIN ASHI CANDLESTICKS ################
    # Creating HA Open & Close
    ix = pd.bdate_range(start = start_date, end = end_date, freq = 'B')
    HA = pd.DataFrame(index=ix)
    HA[cols] = df[cols]
    HA = HA.dropna()
    HA['HA_Open'] = (
        (HA['Open'].shift(1) + HA['Close'].shift(1))/2).dropna()
    HA['HA_Close'] = (
        (HA['Open'] + HA['Close'] + HA['High'] + HA['Close'])/4).dropna()

    # Creating HA High & Low
    high_cols = ['High', 'HA_Open', 'HA_Close']
    HA['HA_High'] = HA[high_cols].max(axis=1)
    low_cols = ['Low', 'HA_Open', 'HA_Close']
    HA['HA_Low'] = HA[low_cols].min(axis=1)

    ################ ICHIMOKU CLOUD ################
    HA['Conversion_Line'] = (HA['HA_High'].rolling(9).max() + HA['HA_Low'].rolling(9).min())/2
    HA['Base_Line'] = (HA['HA_High'].rolling(26).max() + HA['HA_Low'].rolling(26).min())/2
    HA['Leading_Span_A'] = (HA['Conversion_Line'] + HA['Base_Line'])/2
    HA['Leading_Span_B'] = (HA['HA_High'].rolling(52).max() + HA['HA_Low'].rolling(52).min())/2
    HA['Lagging_Span'] = HA['HA_Close'].shift(26)

    # Visualization
    fig, ax = plt.subplots(figsize= (16,10))
    HA_elements = ['HA_Open','HA_High','HA_Low','HA_Close']
    HA_plot_data = np.column_stack((date2num(HA.index),HA[HA_elements].values))
    candlestick_ohlc(ax, HA_plot_data, width=0.6, colorup='green', colordown='red', alpha=0.8)

    ax.plot(HA['Conversion_Line'], label = 'Conversion Line', color = 'blue')
    ax.plot(HA['Base_Line'], label = 'Base Line', color = 'red')
    ax.plot(HA['Leading_Span_A'], label = 'Leading Span A', color = 'green')
    ax.plot(HA['Leading_Span_B'], label = 'Leading Span B', color = 'red', alpha = 0.5)
    ax.plot(HA['Lagging_Span'], label = 'Lagging Span', color = 'green')
    ax.fill_between(HA.index.values, HA['Leading_Span_A'], HA['Leading_Span_B'],
                    where = (HA['Leading_Span_A'] > HA['Leading_Span_B']),
                    interpolate = True, color = 'green', alpha = 0.25)
    ax.fill_between(HA.index.values, HA['Leading_Span_A'], HA['Leading_Span_B'],
                where = (HA['Leading_Span_A'] < HA['Leading_Span_B']),
                interpolate = True, color = 'red', alpha = 0.25)
    ax.legend()
        
    plt.show()

RunStrategy('MMM', dt.date(2008,1,1), dt.date(2019,3,22))