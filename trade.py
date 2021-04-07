from strategy import run_indicators
from ibapitrade import execute_trade
from ibapiportfolio import retrieve_positions
from yahoo_fin import stock_info as si

positions_df = retrieve_positions()
symbols = positions_df['Symbol'].to_list()

actions = {} # store the actions for each symbol

for symbol in symbols:

    print('running signals for ' + symbol)
    live_price = si.get_live_price(symbol) # live stock price
    indicators = run_indicators(symbol) # retrieve indicators and signal
    signal = indicators['Signal']
    previous_close = indicators['Close']
    position = positions_df[positions_df['Symbol'] == symbol]

    # checking for any sharp moves in current trading day
    if signal == "NEUTRAL":
        actions[symbol] = {"Signal": signal, "Action": None, "Price": None, "Quantity": None, "OrderType": None}

    elif signal == "BUY":
        if position.empty: # no position yet
        
            if live_price < previous_close * 0.98: # live price is at least 2% below ytd's close
                print('Significant movement detected in ' + symbol + ':')
                print('Live Price: ' + str(round(live_price,2)))
                print('Previous Close: ' + str(round(previous_close,2)))
                print('Change: ' + str(round(live_price/previous_close-1,2)*100) + '%\n')
                proceed = input('proceed with ' + signal + ' market order? [y/n]: ')

                if proceed == 'y': # use Market Order
                    orderType = "MKT"
                    reference_price = live_price

                else: # use Limit Order
                    orderType = "LMT"
                    lmtPrice = float(input('enter limit price for order: '))
                    reference_price = lmtPrice

                # execute_trade(symbol=symbol, exchange="SMART", secType="STK", currency="USD", action=signal, orderType=orderType, quantity=quantity)
            else:
                orderType = "MKT"
                reference_price = live_price

            investment_amount = float(input('how much to invest (USD)?: '))
            quantity = int(investment_amount/live_price)
            actions[symbol] = {"Signal": signal, "Action": signal, "Price": round(reference_price,2),
                        "Quantity": int(quantity), "OrderType": orderType}

        else: # already have position
            actions[symbol] = {"Signal": signal, "Action": 'HOLD', "Price": None, "Quantity": None, "OrderType": None}

    elif signal == "SELL":
        if not position.empty: # have a position

            if live_price > previous_close * 1.02: # live price is at least 2% above ytd's close
                print('Significant movement detected in ' + symbol + ':')
                print('Live Price: ' + str(round(live_price,2)))
                print('Previous Close: ' + str(round(previous_close,2)))
                print('Change: ' + str(round(live_price/previous_close-1,2)*100) + '%\n')
                proceed = input('proceed with ' + signal + ' market order? [y/n]: ')

                if proceed == 'y': # use Market Order
                    orderType = "MKT"
                    reference_price = live_price

                else: # use Limit Order
                    orderType = "LMT"
                    lmtPrice = float(input('enter limit price for order: '))
                    reference_price = lmtPrice

                # execute_trade(symbol=symbol, exchange="SMART", secType="STK", currency="USD", action=signal, orderType=orderType, quantity=quantity)
            else:
                orderType = "MKT"
                reference_price = live_price
                
            quantity = position['Quantity'].values[0]
            actions[symbol] = {"Signal": signal, "Action": signal, "Price": round(reference_price,2),
                        "Quantity": int(quantity), "OrderType": orderType}

        else: # no position
            actions[symbol] = {"Signal": signal, "Action": 'HOLD', "Price": None, "Quantity": None, "OrderType": None}

    else:
        print("Signal error, please debug.")
    
print('\n\n Review Trade Execution:')
print('SYMBOL\tSIGNAL\tACTION\tPRICE\tQTY\tORDERTYPE')
for symbol,data in actions.items():
    signal = data['Signal']
    action = data['Action']
    price = data['Price']
    quantity = data['Quantity']
    orderType = data['OrderType']
    print(symbol + '\t' + signal + '\t' + str(action) + '\t' + str(price) + '\t' + str(quantity) +
        '\t' + str(orderType))

proceed = input('\nProceed with Trades? [y/n]: ')
if proceed == 'y':
    for symbol,data in actions.items():
        signal = data['Signal']
        action = data['Action']
        price = data['Price']
        quantity = data['Quantity']
        orderType = data['OrderType']
        if action in ['BUY', 'SELL']:
            execute_trade(symbol=symbol, exchange="SMART", secType="STK", currency="USD", action=signal, orderType=orderType, quantity=quantity, price=price)
