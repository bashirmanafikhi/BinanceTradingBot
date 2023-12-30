import time
import pandas as pd
from binance import ThreadedWebsocketManager

from helpers.settings.settings import Settings

def get_binance_websocket_service():
    settings = Settings()

    api_key = settings.binance.api_key
    api_secret = settings.binance.api_secret
    api_testnet = settings.binance.api_testnet

    return BinanceWebSocketService(api_key, api_secret, api_testnet)


class BinanceWebSocketService:

    def __init__(self, api_key, api_secret, api_testnet):
        self.api_key = api_key
        self.api_secret = api_secret
        self.twm = ThreadedWebsocketManager(api_key=api_key,
                                            api_secret=api_secret,
                                            testnet=api_testnet)

    def start_kline_socket(self, symbol, callback):

        def convert_kline_to_dataframe(kline_data):
            kline = kline_data['k']

            # Extracting data from the kline dictionary
            data = {
                "timestamp": pd.to_datetime(kline['t'], unit="ms"),
                "open": float(kline['o']),
                "high": float(kline['h']),
                "low": float(kline['l']),
                "close": float(kline['c']),
                "volume": float(kline['v']),
                "close_time": kline['T'],
                "quote_asset_volume": float(kline['q']),
                "number_of_trades": kline['n'],
                "taker_buy_base_asset_volume": float(kline['V']),
                "taker_buy_quote_asset_volume": float(kline['Q']),
                "ignore": kline['B']
            }

            # Create a DataFrame
            df = pd.DataFrame([data])

            # Convert relevant columns to numeric
            df['close'] = pd.to_numeric(df['close'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])

            callback(df)

        self.twm.start_kline_socket(callback=convert_kline_to_dataframe,
                                    symbol=symbol)

    def start_depth_socket(self, symbol, callback):
        self.twm.start_depth_socket(callback=callback, symbol=symbol)

    def start_multiplex_socket(self, streams, callback):
        self.twm.start_multiplex_socket(callback=callback, streams=streams)

    def start(self):
        self.twm.start()

    def join(self):
        self.twm.join()





    # def handle_depth_message_example(self, msg):
    #     # وقت بدك تبيع طلع على هاد
    #     # Bid Price: The highest price a buyer is willing to pay for a security. If you want to sell an asset immediately, you could place a market sell order at the bid price.
    #     if "b" in msg and len(msg["b"]) > 0:
    #         self.bid_price = float(msg["b"][0][0])  # Highest bid price
    #     else:
    #         return

    #     # وقت تشتري طلع على هاد
    #     # Ask Price: The lowest price a seller is willing to accept for a security. If you want to buy an asset immediately, you could place a market buy order at the ask price.
    #     if "a" in msg and len(msg["a"]) > 0:
    #         self.ask_price = float(msg["a"][0][0])  # Lowest ask price
    #     else:
    #         return
