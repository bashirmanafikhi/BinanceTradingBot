import pandas as pd
from pandas_ta import *
from datetime import datetime, timedelta
import logging
from helpers.settings.constants import ACTION_BUY, ACTION_SELL

from trading_strategies.trading_strategy import TradingStrategy

class EMACrossoverStrategy(TradingStrategy):
    
    def __init__(self, short_window=9, long_window=21):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window

    def on_starting(self):
        self.last_action = None

    def process_row(self, row):

        # Wait for at least long_window rows to form
        if len(self.candles) < self.long_window:
            return []

        # Calculate EMAs
        try:
            self.candles.ta.ema(length=self.short_window, append=True)
            self.candles.ta.ema(length=self.long_window, append=True)
        except TypeError as e:
            pass
            # logging.info("Error during EMA calculation:", e)

        # Extract current and previous rows
        current_row = self.candles.iloc[-1]
        previous_row = self.candles.iloc[-2]
        current_price = current_row["close"]

        # Implement EMA Crossover Strategy
        if (
            current_row["EMA_9"] > current_row["EMA_21"]
            and previous_row["EMA_9"] <= previous_row["EMA_21"]
            and (self.last_action == ACTION_SELL or self.last_action is None)
        ):
            return self.create_trade_action(ACTION_BUY, current_price)

        elif (
            current_row["EMA_9"] < current_row["EMA_21"]
            and previous_row["EMA_9"] >= previous_row["EMA_21"]
            and (self.last_action == ACTION_BUY or self.last_action is None)
        ):
            return self.create_trade_action(ACTION_SELL, current_price)

        else:
            return []
