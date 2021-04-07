# guides:
# https://algotrading101.com/learn/interactive-brokers-python-api-native-guide/
# https://medium.com/swlh/structure-and-communicating-with-interactive-brokers-api-python-78ed9dcaccd7

from ibapi.wrapper import *
from ibapi.client import *
from ibapi.contract import *
from ibapi.order import *
from ibapi.common import *
from threading import Thread
import queue, datetime, time
import pandas as pd

class TestWrapper(EWrapper):

    # error handling methods
    # errors are pushed from the server, not invoked by the app
    def init_error(self): # stores error messages in queue
        error_queue = queue.Queue()
        self.my_errors_queue = error_queue

    def is_error(self): # check if there are errors in queue
        error_exist = not self.my_errors_queue.empty()
        return error_exist

    def get_error(self, timeout=6): # retrieve error message
        if self.is_error():
            try:
                return self.my_errors_queue.get(timeout=timeout)
            except queue.Empty:
                print("Exception raised")
                return None
        return None

    def error(self, id, errorCode, errorString): # overrides native method in ibapi for simpler error message
        errormessage = "Error ID: %d, Error Code: %d, Message: %s" % (id, errorCode, errorString)
        self.my_errors_queue.put(errormessage)

    ############
    # time handling methods
    # simplest way to prove connection established is to ask for server time
    def init_time(self):
        time_queue = queue.Queue()
        self.my_time_queue = time_queue
        return time_queue

    def currentTime(self, server_time): # overwrites native method in ibapi to allow server_time to be placed in queue
        self.my_time_queue.put(server_time)
    

############
# client class to invoke messages and requests to server
class TestClient(EClient):

    def __init__(self, wrapper):
        # implement wrapper as constructor of TestClient
        # needed to handle returned messages, __init__ helps socket be initialized to an instance of the wrapper
        EClient.__init__(self, wrapper)

    def server_clock(self):
        
        print("Asking server for unix time")

        # creates queue to store time
        time_storage = self.wrapper.init_time()

        # requests unix time from EClient
        self.reqCurrentTime()

        # declare max timeout
        # good practice to follow for any request, watches for error without feedback
        max_wait_time = 10

        try:
            requested_time = time_storage.get(timeout = max_wait_time)
        except queue.Empty:
            print("Queue empty or max time reached")
            requested_time = None

        # loop checks for errors stored from get_error method in wrapper
        # if no error, server_clock method skips loop and returns value of time to print in execution area
        while self.wrapper.is_error():
            print("Error:")
            print(self.get_error(timeout=5))

        return requested_time

class IBApi(TestWrapper, TestClient):

    def __init__(self, ipaddress, portid, clientid):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)

        # connect to server with ipaddress, portid and clientid
        self.connect(ipaddress, portid, clientid)

        # initialize threading
        thread = Thread(target=self.run)
        thread.start()
        setattr(self, "_thread", thread)

        # start listening for errors
        self.init_error()

        # variable to store historical data
        self.historical_data = []

        # variable to store positions
        self.all_positions = pd.DataFrame([], columns = ['Account','Symbol', 'Quantity', 'Average Cost', 'Sec Type'])
    
    # receiving historical data
    def historicalData(self, reqId, bar):
        self.historical_data.append([bar.date, bar.close])

    ############
    # managing orders
    def nextValidId(self, OrderId: int):
        super().nextValidId(OrderId)
        self.nextOrderId = OrderId
        print('The next valid order id is: ', self.nextOrderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

    ###########
    # checking positions
    def position(self, account, contract, pos, avgCost):
            index = str(account)+str(contract.symbol)
            # specifically for class demo acct
            if account == 'DU3307446':
                self.all_positions.loc[index]= account, contract.symbol, pos, avgCost, contract.secType

# want program to be run only when we run this specific script, not when it is imported, hence:

if __name__ == '__main__':

    print('before start')

    # specifies local host with port
    app = IBApi("127.0.0.1", 7497, 0)

    # indicates program begun
    print("Program started")

    # assign server clock method output to variable
    requested_time = app.server_clock()

    # printing server output
    print("Current server time:" + str(requested_time))

    # optional disconnect, don't disconnect if keeping open connection
    # app.disconnect()