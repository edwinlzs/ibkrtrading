from ibapisetup import *

def retrieve_positions():

    app = IBApi('127.0.0.1', 7497, 0)
    # print("--program started--")
    # requested_time = app.server_clock()
    # print("Current server time:" + str(requested_time))

    app.reqPositions() # send request

    time.sleep(3)
    positions_df = app.all_positions

    app.disconnect()

    return positions_df

# positions_df = retrieve_positions()
# print(positions_df[positions_df['Symbol'] == 'LMT'].empty)
