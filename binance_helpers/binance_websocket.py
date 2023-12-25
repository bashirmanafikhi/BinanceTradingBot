import time
import pandas as pd
from binance import ThreadedWebsocketManager

from settings.settings import Settings

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
        self.twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret, testnet=api_testnet)

    def start_kline_socket(self, symbol, callback):
        self.twm.start_kline_socket(callback=callback, symbol=symbol)

    def start_depth_socket(self, symbol, callback):
        self.twm.start_depth_socket(callback=callback, symbol=symbol)

    def start_multiplex_socket(self, streams, callback):
        self.twm.start_multiplex_socket(callback=callback, streams=streams)

    def start(self):
        self.twm.start()

    def join(self):
        self.twm.join()
