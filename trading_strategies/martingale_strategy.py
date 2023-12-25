from binance_helpers.binance_trading_client import get_binance_trading_client
from binance_helpers.binance_websocket import BinanceWebSocketService, get_binance_websocket_service
from sequences.duplicated_numbers_sequence import DuplicatedNumbersSequence
from typing import Type
from sequences.sequence_strategy import SequenceStrategy
import time
import pandas as pd
from binance import ThreadedWebsocketManager

class MartingaleStrategy():
    def __init__(self, baseCapital, symbol):
        self.sequence_strategy = DuplicatedNumbersSequence()
        self.binanceClient = get_binance_trading_client()
        self.baseCapital = baseCapital
        self.symbol = symbol
        self.startTradingPercentage = 0.01
        self.startTradingCapital = self.baseCapital * self.startTradingPercentage
        self.initWebSocket()

    def custom_handle_message(self, msg):
        print(f"Message type: {msg['e']}")
        dataframe = pd.DataFrame(msg)
        print(dataframe)
        
        if(False):
            self.buy()

    def buy(self):
        sequence = self.sequence_strategy.next()
        buy_quantity = self.startTradingCapital * sequence
        print("\nMarket Buy Order..")
        order = self.binanceClient.place_market_buy_order(self.symbol, buy_quantity)
        print(pd.DataFrame(order))

    def set_sequence_strategy(self, sequence_strategy: Type[SequenceStrategy]):
        self.sequence_strategy = sequence_strategy

    def initWebSocket(self):
        # Create an instance of BinanceWebSocketService
        binanceWebSocket = get_binance_websocket_service()

        # Start the WebSocket service
        binanceWebSocket.start()

        # Start Kline (candlestick) socket with custom message handling
        binanceWebSocket.start_kline_socket(symbol=self.symbol, callback=self.custom_handle_message)

        # Keep the program running
        binanceWebSocket.join()
