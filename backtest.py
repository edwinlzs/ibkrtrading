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
    print('<--- Developing Heikin Ashi Candlesticks --->')
    ix = pd.bdate_range(start = start_date, end = end_date, freq = 'B')
    HA = pd.DataFrame(index=ix)
    HA[cols] = df[cols]
    HA = HA.dropna()
    print('calculating Open... ', end='')
    HA['HA_Open'] = (
        (HA['Open'].shift(1) + HA['Close'].shift(1))/2).dropna()
    print('done\ncalculating Close... ', end='')
    HA['HA_Close'] = (
        (HA['Open'] + HA['Close'] + HA['High'] + HA['Close'])/4).dropna()
    print('done\ncalculating High... ', end='')

    # Creating HA High & Low
    high_cols = ['High', 'HA_Open', 'HA_Close']
    HA['HA_High'] = HA[high_cols].max(axis=1)
    print('done\ncalculating Low... ', end='')
    low_cols = ['Low', 'HA_Open', 'HA_Close']
    HA['HA_Low'] = HA[low_cols].min(axis=1)
    print('done\n\nHeikin Ashi OHLC complete\n')

    ################ ICHIMOKU CLOUD ################
    print('<--- Developing Ichimoku Cloud --->')
    print('calculating Conversion Line... ', end='')
    HA['Conversion_Line'] = (HA['HA_High'].rolling(9).max() + HA['HA_Low'].rolling(9).min())/2
    print('done\ncalculating Base Line... ', end='')
    HA['Base_Line'] = (HA['HA_High'].rolling(26).max() + HA['HA_Low'].rolling(26).min())/2
    print('done\ncalculating Leading Span A... ', end='')
    HA['Leading_Span_A'] = (HA['Conversion_Line'] + HA['Base_Line'])/2
    print('done\ncalculating Leading Span B... ', end='')
    HA['Leading_Span_B'] = (HA['HA_High'].rolling(52).max() + HA['HA_Low'].rolling(52).min())/2
    print('done\ncalculating Lagging Span... ', end='')
    HA['Lagging_Span'] = HA['HA_Close'].shift(26)
    print('done\n\nIchimoku Cloud indicators complete\n')

    ################ VISUALIZATION ################
    # fig, ax = plt.subplots(figsize= (16,10))
    # HA_elements = ['HA_Open','HA_High','HA_Low','HA_Close']
    # HA_plot_data = np.column_stack((date2num(HA.index),HA[HA_elements].values))
    # candlestick_ohlc(ax, HA_plot_data, width=0.6, colorup='green', colordown='red', alpha=0.8)

    # ax.plot(HA['Conversion_Line'], label = 'Conversion Line', color = 'blue')
    # ax.plot(HA['Base_Line'], label = 'Base Line', color = 'red')
    # ax.plot(HA['Leading_Span_A'], label = 'Leading Span A', color = 'green')
    # ax.plot(HA['Leading_Span_B'], label = 'Leading Span B', color = 'red', alpha = 0.5)
    # ax.plot(HA['Lagging_Span'], label = 'Lagging Span', color = 'green')
    # ax.fill_between(HA.index.values, HA['Leading_Span_A'], HA['Leading_Span_B'],
    #                 where = (HA['Leading_Span_A'] > HA['Leading_Span_B']),
    #                 interpolate = True, color = 'green', alpha = 0.25)
    # ax.fill_between(HA.index.values, HA['Leading_Span_A'], HA['Leading_Span_B'],
    #             where = (HA['Leading_Span_A'] < HA['Leading_Span_B']),
    #             interpolate = True, color = 'red', alpha = 0.25)
    # ax.legend()
        
    # plt.show()

    ################ BACKTEST ################
    # Generating Signals
    print('<--- Backtesting Strategy --->')
    trading_data = HA[HA['Leading_Span_B'].notnull()] # can only trade when all ichimoku indicators are available, leading_span_b is the last indicator to come online
    position = 0
    returns = []
    entry_price = 0
    exit_price = 0
    HA['Activity'] = np.nan
    HA['Returns'] = np.nan

    for row in trading_data.iterrows():
        date = row[0]
        values = row[1]
        
        # for comparing non-trading returns
        if date == trading_data.index[0]:
            start_price = values['Open']
        elif date == trading_data.index[-1]:
            end_price = values['Open']
        
        # trading signals
        # condition: candle above leading span A, Close above Conversion Line
        if (values['HA_Low'] > values['Leading_Span_A']) & (values['HA_Close'] > values['Conversion_Line']) & (position == 0):
            position = 1
            entry_price = values['Open']
            HA.loc[date, 'Activity'] = 'entered'
            
        # condition: Close below Conversion Line, Close below Leading Span A
        elif (values['HA_Close'] < values['Conversion_Line']) & (values['HA_Close'] < values['Leading_Span_A']) & (position == 1):
            position = 0
            exit_price = values['Open']
            change = (exit_price-entry_price)/entry_price
            
            HA.loc[date, 'Activity'] = 'exited'
            HA.loc[date, 'Returns'] = change
            returns.append(change)
        
    value = 1
    values = [1]
    for change in returns:
        value = value * (1+change)
        values.append(value)
        
    # plt.plot(values)
    # plt.show()

    print('trading return: ' + str(round((value-1)*100,2)) + '%')
    print('benchmark return: ' + str(round((end_price/start_price - 1)*100,2)) + '%')

    strat_mean = np.mean(returns)
    strat_std = np.std(returns)
    strat_sharpe = strat_mean/strat_std
    print('\nStrategy Statistics:')
    print('mean: ' + str(round(strat_mean*100,2)) + '%')
    print('stdev: ' + str(round(strat_std*100,2)) + '%')
    print('sharpe: ' + str(round(strat_sharpe,2)))

    HA['Daily Returns'] = HA['Close']/HA['Close'].shift(1) - 1
    bench_mean = np.mean(HA['Daily Returns'])
    bench_std = np.std(HA['Daily Returns'])
    bench_sharpe = bench_mean/bench_std
    print('\nBenchmark Statistics:')
    print('mean: ' + str(round(bench_mean*100,2)) + '%')
    print('stdev: ' + str(round(bench_std*100,2)) + '%')
    print('sharpe: ' + str(round(bench_sharpe,2)) + '\n')

RunStrategy('AMZN', dt.date(2008,1,1), dt.date(2019,3,22))