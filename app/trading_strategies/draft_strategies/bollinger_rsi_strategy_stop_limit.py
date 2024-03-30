import pandas as pd
from pandas_ta import *
from datetime import datetime, timedelta
import helpers.my_logger as my_logger
from helpers.settings.constants import ACTION_BUY, ACTION_SELL

from trading_strategies.trading_strategy import TradingStrategy

class BollingerRSIStrategyStopLimit(TradingStrategy):
    
    def __init__(self, bollinger_window=20, bollinger_dev=2, rsi_window=14, rsi_overbought=70, rsi_oversold=30):
        super().__init__()
        self.bollinger_window = bollinger_window
        self.bollinger_dev = bollinger_dev
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def on_starting(self):
        self.last_action = None

    def process_row(self, row):
        # Wait for at least bollinger_window + rsi_window rows to form
        if len(self.candles) < self.bollinger_window + self.rsi_window:
            return []

        # Calculate Bollinger Bands and RSI
        try:
            self.candles.ta.bbands(length=self.bollinger_window, std=self.bollinger_dev, append=True)
            self.candles.ta.rsi(length=self.rsi_window, append=True)
        except TypeError as e:
            pass
            # my_logger.info("Error during Bollinger Bands and RSI calculation:", e)

        # Extract current and previous rows
        current_row = self.candles.iloc[-1]
        previous_row = self.candles.iloc[-2]
        current_price = current_row["close"]

        # Implement Bollinger Bands and RSI Strategy
        if (
            current_row["close"] < current_row[f"BBL_{self.bollinger_window}_{self.bollinger_dev}.0"]
            and current_row[f"RSI_{self.rsi_window}"] < self.rsi_oversold
            and (self.last_action is None)
        ):
            return self.create_trade_action(ACTION_BUY, current_price)

        elif (
            current_row["close"] > current_row[f"BBU_{self.bollinger_window}_{self.bollinger_dev}.0"]
            and current_row[f"RSI_{self.rsi_window}"] > self.rsi_overbought
            and (self.last_action is None)
        ):
            return self.create_trade_action(ACTION_SELL, current_price)

        # Close
        elif self.last_action != None and (current_price > self.high_close_limit or current_price < self.low_close_limit):
            return self.close_order(current_price) 
        
        else:
            return []
