from ibapisetup import *

app = IBApi('127.0.0.1', 7497, 0)

print("program started")

# assign server clock method output to variable
requested_time = app.server_clock()

# printing server output
print("Current server time:" + str(requested_time))

# input contract details

# symbol = input("Symbol: ")
# secType = input("Security Type: ")
# currency = input("Currency: ")
# exchange = input("Exchange: ")

contract1 = Contract()
# contract1.symbol = 'AAPL'
# contract1.secType = 'STK'
# contract1.currency = 'USD'
# contract1.exchange = 'NYSE'
# contract1.primaryExchange = 'NYSE'

# contract1.symbol = 'EUR'
# contract1.secType = 'CASH'
# contract1.exchange = 'IDEALPRO'
# contract1.currency = 'USD'

contract1.symbol = 'XS1963850612'
contract1.secType = 'BOND'
contract1.exchange = 'SMART'
contract1.currency = 'USD'

# request historical data from contract
reqId = 1
# queryTime = (datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%Y%m%d %H:%M:%S")
duration = "3 M"
barSize = "1 day"
dataType = "BID"
useRTH = 1
formatDate = 1
app.reqHistoricalData(reqId=reqId, contract=contract1, endDateTime='', durationStr=duration,
                                barSizeSetting=barSize, whatToShow=dataType,
                                useRTH=useRTH, formatDate=formatDate, keepUpToDate=False, chartOptions=[])

# app.reqHistoricalData(1, eurusd_contract, '', '2 D', '1 hour', 'BID', 0, 2, False, [])

print("Historical data requested.")
time.sleep(5)
print(app.historical_data)
time.sleep(5)
print(app.historical_data)
time.sleep(5)
print(app.historical_data)

# receive historical data
# historical_data = app.historicalData(reqId, BarData) # returns a common.BarData object with price candlestick data
# print(historical_data[1].__str__)
# print("Historical data received.")

# app.disconnect()