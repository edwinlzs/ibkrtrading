# order documentation:
# http://interactivebrokers.github.io/tws-api/basic_orders.html
# http://interactivebrokers.github.io/tws-api/order_submission.html

from ibapisetup import *

app = IBApi('127.0.0.1', 7497, 0)
print("--program started--")
requested_time = app.server_clock()
print("Current server time:" + str(requested_time))
app.nextOrderId = app.reqIds(-1)

# def run_loop():
#     print('running app loop')
#     app.run()

action = "BUY"
quantity = 10
price = 670.00
# discretionaryAmt = 5

contract = Contract()
contract.symbol = 'TTD'
contract.secType = 'STK'
contract.currency = 'USD'
contract.exchange = 'SMART'
# contract.primaryExchange = 'ISLAND'

order = Order()
order.action = action
order.orderType = "LMT"
order.totalQuantity = quantity
order.lmtPrice = price
# order.discretionaryAmt = discretionaryAmt # amount over and above Bid we are willing to pay
print("order prepared\n")

# print('preparing thread')
# api_thread = Thread(target=run_loop, daemon=True)
# api_thread.start()
# print('thread started')

print("-- checking for connection")
while True:
    if isinstance(app.nextOrderId, int):
        print('-- connected\n')
        break
    else:
        print('waiting for connection')
        time.sleep(2)

print("-- transmitting order\n")
app.simplePlaceOid = app.nextOrderId
print("order id: " + str(app.simplePlaceOid))
app.placeOrder(app.simplePlaceOid, contract, order)
app.nextOrderId += 1
print("-- order placed\n")

print("-- exiting")
app.disconnect()
