import alpaca_trade_api as tradeapi
from alpaca_trade_api import StreamConn
import pandas as pd
import websocket
import json
import time

API_KEY_ID = "PKSAWVRI13BK1YFG5JT9"
SECRET_KEY = "EUGoVcLwnE1n5Ro7l1Z9MNASbPuLFiOBX6XJKOy4"
END_POINT = "https://paper-api.alpaca.markets"
END_POINT_STREAM = "wss://data/alpaca.markets/stream"

# live_API_KEY_ID = 'AKNXZ32P07Y9FO1WVV5J'
# live_SECRET_KEY = '8IwLroeFEhIcgW3K3YiWubkKz9Pa0Ohosr1iY1k2'
# live_END_POINT = 'https://api.alpaca.markets'
def hello():
    ap = tradeapi.REST(
        "PKSAWVRI13BK1YFG5JT9",
        "EUGoVcLwnE1n5Ro7l1Z9MNASbPuLFiOBX6XJKOy4",
        'https://paper-api.alpaca.markets'
    )

    # Get account info
    account = ap.get_account()

    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity)
    return str(balance_change)

def lastEquity():
    ap = tradeapi.REST(
        "PKSAWVRI13BK1YFG5JT9",
        "EUGoVcLwnE1n5Ro7l1Z9MNASbPuLFiOBX6XJKOy4",
        'https://paper-api.alpaca.markets'
    )

    # Get account info
    account = ap.get_account()

    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    return str(balance_change)

class Ticker:
    allTickers = []
    def __init__(self, symbol, trade_list=[]):
        print("4")
        self.symbol = symbol
        self.trade_list = trade_list
        Ticker.allTickers.append(symbol)
class Alpaca:  
    def __init__(self, api_key_id, secret_key, end_point):
        
        self.api_key_id = api_key_id
        self.secret_key = secret_key
        self.end_point = end_point
        self.alpaca = tradeapi.REST(self.api_key_id, self.secret_key, base_url=self.end_point)
        self.AAPL = Ticker("AAPL")
        self.MSFT = Ticker("MSFT")
        self.TSLA = Ticker("TSLA")
        self.GOOGL = Ticker("GOOGL")
        self.CRM = Ticker("CRM")
        
        self.FB = Ticker("FB")
        self.NVDA = Ticker("NVDA")
        self.HPQ = Ticker("HPQ")
        self.IBM = Ticker("IBM")
        self.SNAP = Ticker("SNAP")
    def reset(self):
        """
        Cancel all orders
        """
        self.alpaca.cancel_all_orders()
        print("Canceled all orders")
    def close_positions(self,symbol):
        positions = self.alpaca.list_positions()
        for position in positions:
            if position.symbol == symbol:
                if(position.side == 'long'):
                    orderSide = 'sell'
                else:
                    orderSide = 'buy'
                qty = abs(int(float(position.qty)))
                self.submit_order(symbol = position.symbol,order_side = orderSide, qty = qty)
    def submit_order(self, symbol, order_side, qty=1, order_type="market", limit_price=0, stop_price=0, time_in_force="gtc"):
        """
        Submit an order with specific constrains
            :param symbol: A string of ticker name
            :param order_side: A string of buy or sell
            :param qty: An integer representing the number of shares to submit
            :param order_type: An string of order type, market, limit, stop or stop_loss
            :param limit_price: A number of limit price
            :param stop_price:  A number of stop price
            :param time_in_force: A string represents time-in-force desinations
        """
        try:
            if not self.alpaca.get_asset(symbol).tradable:
                print("Alpaca cannot trade " + symbol)
                return
        except tradeapi.rest.APIError:
            print("Alpaca cannot trade " + symbol)
            return
        if order_type == "limit":
            self.alpaca.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price
            )
        elif order_type == "stop":
            self.alpaca.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=order_type,
                time_in_force=time_in_force,
                stop_price=stop_price
            )
        elif order_type == "stop_limit":
            self.alpaca.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price
            )
        else:
            self.alpaca.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=order_type,
                time_in_force=time_in_force
            )
        print(order_type + " order has been submitted")
    def check_performance(self):
        """
        Check the return of the portfolio
        :return:
        """
        return
    def get_data(self, symbol, _from, to, timespan, multiplier):
        """
        Download data from alpaca
            :param symbol: A string of ticker name
            :param _from: A string of start time
            :param to: A string of end time
            :param timespan: A string representing the time interval of data, minute, hour, day, week, month, quarter, or year
            :param multiplier: An integer representing the size of the timespan multiplier
            :return: A pandas Dataframe of data
            :rtype: DataFame
        """
        data = self.alpaca.get_aggs(symbol=symbol, timespan=timespan, multiplier=multiplier, _from=_from, to=to)
        return data.df
    def check_market_open(self):
        print("10")
        """
        Check whether the market is open
        :return: True or False the market is open
        :rtype: Boolean
        """

        clock = self.alpaca.get_clock()
        print("The market is {}".format("open." if clock.is_open else "closed."))
        return clock.is_open
    def run(self):
        print("6")
        async def on_minute(conn, channel, bars):
            symbol = bars.symbol
            print(symbol)
            market_open_datetime = str(pd.to_datetime('today').normalize().date())
            #TODO fix variable name
            market_close_datetime = str((pd.to_datetime('today').normalize() + pd.Timedelta(1,"d")).date())
            minute_data = self.get_data(symbol, market_open_datetime, market_close_datetime, "day", 1)
            close_data = [i for i in minute_data.loc[:,'close']]
            portfolio = [i.symbol for i in self.alpaca.list_positions()]
            if self.check_market_open:
                #? Purge old data? Use just last 20
                if len(close_data) >= 9:
                    roll_max = max(close_data[-9:])
                    roll_min = min(close_data[-9:])
                    rolling_avg = sum(close_data[-9:])/9
                    if close_data[-1] >= roll_max:
                        self.submit_order(symbol, "buy", qty = 2)
                        print(symbol + " buy order")
                    elif close_data[-1] <= roll_min and symbol in portfolio:
                    #? What happens if you are already shorting the equity in question?
                        #self.submit_order(symbol, "sell", qty = 2)
                        self.close_positions(symbol)
                        print(symbol + " sell order")
        print("7")
        conn = StreamConn(base_url=END_POINT_STREAM, key_id=API_KEY_ID, secret_key=SECRET_KEY, data_stream='polygon')
        print("run on minute data")
        on_minute = conn.on(r'AM$')(on_minute)
        conn.run(["AM." + i for i in Ticker.allTickers])
    @staticmethod
    def on_open(ws):
        print("opened")
        auth_data = {"action": "authenticate",
                     "data": {"key_id": live_API_KEY_ID, "secret_key": live_SECRET_KEY}}
        ws.send(json.dumps(auth_data))
        listen_message = {"action": "listen",
                          "data": {"stream": ["AM.AAPL", "MSFT"]}}
        ws.send(json.dumps(listen_message))
    @staticmethod
    def on_message(ws, message):
        print("received a message")
        print(message)
    @staticmethod
    def on_close(ws):
        print("closed connection")
if __name__ == "__main__":
    api = Alpaca(API_KEY_ID, SECRET_KEY, END_POINT)
    while True:
        try:
            api.run()
        except:
            pass
# # #api.alpaca.list_positions()
# #api.submit_order("AAPL", "buy",qty=10)
# #print(api.alpaca.list_orders())
# #print(api.alpaca.__dir__())
# #print(api.get_data(symbol="AAPL", _from="2020-07-01", to="2020-08-30"))
# #print(api.alpaca.get_aggs(symbol="AAPL", timespan="minute", multiplier=1, _from="2020-07-30", to="2020-08-01")[0])
# #print(api.alpaca.list_positions())
# print("start")
# #api.check_market_open()
# api.run()
# #socket = "wss://data.alpaca.markets/stream"
# #ws = websocket.WebSocketApp(socket, on_open=api.on_open, on_message=api.on_message, on_close=api.on_close)
# #ws.stop()