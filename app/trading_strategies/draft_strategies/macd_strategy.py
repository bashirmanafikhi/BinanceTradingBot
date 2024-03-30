import pandas as pd
import pandas_ta as ta
import numpy as np
import helpers.my_logger as my_logger
from trading_strategies.trading_strategy import TradingStrategy
from helpers.settings.constants import ACTION_BUY, ACTION_SELL

class MACDStrategy(TradingStrategy):
    def __init__(self, min_macd_diff = 0.04):
        super().__init__()
        self.min_macd_diff = min_macd_diff
        
    def on_starting(self):
        self.last_action = None
        self.high_close_limit = None
        self.low_close_limit = None

    def process_row(self, row):
        price = row.close

        # Wait for at least 15 rows to form
        if len(self.candles) < 15:
            return []

        # Calculate MACD
        try:
            self.candles.ta.macd(append=True)
        except TypeError as e:
            pass
            #my_logger.info("Error during MACD calculation:", e)
        
        
        if 'MACD_12_26_9' not in self.candles.columns:
            return []
        
        # Calculate EMA(100)
        #self.candles.ta.ema(100, append=True)
        
        # Extract current and previous rows
        current_row = self.candles.iloc[-1]
        previous_row = self.candles.iloc[-2]
        current_price = current_row["close"]

        # Additional filters
        macd_diff = current_row["MACD_12_26_9"] - current_row["MACDs_12_26_9"]
        
        # Implement MACD Strategy
        if (
            abs(macd_diff) > self.min_macd_diff
            and current_row["MACD_12_26_9"] > current_row["MACDs_12_26_9"]
            and previous_row["MACD_12_26_9"] <= previous_row["MACDs_12_26_9"]
            and (self.last_action == None)
            #and (('EMA_100' in self.candles.columns) and current_price < current_row['EMA_100'])
        ):
            return self.create_trade_action(ACTION_BUY, current_price)

        elif (
            abs(macd_diff) > self.min_macd_diff
            and current_row["MACD_12_26_9"] < current_row["MACDs_12_26_9"]
            and previous_row["MACD_12_26_9"] >= previous_row["MACDs_12_26_9"]
            and (self.last_action == None)
            #and (('EMA_100' in self.candles.columns) and current_price > current_row['EMA_100'])
        ):
            return self.create_trade_action(ACTION_SELL, current_price)

        # Close
        elif self.last_action != None and (price > self.high_close_limit or price < self.low_close_limit):
            return self.close_order(price) 
        
        else:
            return []
        
