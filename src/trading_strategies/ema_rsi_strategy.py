import pandas as pd
from pandas_ta import *
from datetime import datetime, timedelta
import logging
from helpers.settings.constants import ACTION_BUY, ACTION_SELL

from trading_strategies.trading_strategy import TradingStrategy

class EMARSIStrategy(TradingStrategy):
    
    def __init__(self, short_window=9, long_window=21, rsi_window=14, rsi_threshold=70):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_window = rsi_window
        self.rsi_threshold = rsi_threshold

    def on_starting(self):
        self.last_action = None

    def process(self, row):

        # Wait for at least long_window + rsi_window rows to form
        if len(self.candles) < self.long_window + self.rsi_window:
            return []

        # Calculate EMAs and RSI
        try:
            self.candles.ta.ema(length=self.short_window, append=True)
            self.candles.ta.ema(length=self.long_window, append=True)
            self.candles.ta.rsi(length=self.rsi_window, append=True)
        except TypeError as e:
            pass
            # logging.info("Error during EMA and RSI calculation:", e)

        # Extract current and previous rows
        current_row = self.candles.iloc[-1]
        previous_row = self.candles.iloc[-2]
        current_price = current_row["close"]

        # Implement EMA Crossover Strategy with RSI confirmation
        if (
            current_row["EMA_9"] > current_row["EMA_21"]
            and previous_row["EMA_9"] <= previous_row["EMA_21"]
            and current_row["RSI_14"] > self.rsi_threshold
            and (self.last_action == ACTION_SELL or self.last_action is None)
        ):
            return self.create_trade_action(ACTION_BUY, current_price)

        elif (
            current_row["EMA_9"] < current_row["EMA_21"]
            and previous_row["EMA_9"] >= previous_row["EMA_21"]
            and current_row["RSI_14"] < (100 - self.rsi_threshold)
            and (self.last_action == ACTION_BUY or self.last_action is None)
        ):
            return self.create_trade_action(ACTION_SELL, current_price)

        else:
            return []
