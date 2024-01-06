import pandas as pd
import pandas_ta as ta
import numpy as np
from trading_strategies.trading_strategy import TradingStrategy
from helpers.settings.constants import ACTION_BUY, ACTION_SELL

class MACDStrategy(TradingStrategy):
    MIN_MACD_DIFF = 0.025

    def on_enabling(self):
        self.last_action = None

    def process(self, row):

        # Wait for at least 15 rows to form
        if len(self.candles) < 15:
            return []

        # Calculate MACD
        try:
            self.candles.ta.macd(append=True)
        except TypeError as e:
            pass
            #print("Error during MACD calculation:", e)
        
        
        if 'MACD_12_26_9' not in self.candles.columns:
            return []
        
        # Calculate EMA(100)
        self.candles.ta.ema(100, append=True)
        
        # Extract current and previous rows
        current_row = self.candles.iloc[-1]
        previous_row = self.candles.iloc[-2]
        current_price = current_row["close"]

        # Additional filters
        macd_diff = current_row["MACD_12_26_9"] - current_row["MACDs_12_26_9"]
        
        # Implement MACD Strategy
        if (
            abs(macd_diff) > self.MIN_MACD_DIFF
            and current_row["MACD_12_26_9"] > current_row["MACDs_12_26_9"]
            and previous_row["MACD_12_26_9"] <= previous_row["MACDs_12_26_9"]
            and (self.last_action == ACTION_SELL or self.last_action == None)
            #and (('EMA_100' in self.candles.columns) and current_price < current_row['EMA_100'])
        ):
            return self.create_trade_action(ACTION_BUY, current_price)

        elif (
            abs(macd_diff) > self.MIN_MACD_DIFF
            and current_row["MACD_12_26_9"] < current_row["MACDs_12_26_9"]
            and previous_row["MACD_12_26_9"] >= previous_row["MACDs_12_26_9"]
            and (self.last_action == ACTION_BUY)
            #and (('EMA_100' in self.candles.columns) and current_price > current_row['EMA_100'])
        ):
            return self.create_trade_action(ACTION_SELL, current_price)

        else:
            return []
