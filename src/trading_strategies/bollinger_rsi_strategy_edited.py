import pandas_ta as ta
from datetime import datetime, timedelta
import logging
from helpers.settings.constants import ACTION_BUY, ACTION_SELL

from trading_strategies.trading_strategy import TradingStrategy

class BollingerRSIStrategyEdited(TradingStrategy):
    
    def __init__(self, bollinger_window=20, bollinger_dev=2, rsi_window=14, rsi_overbought=70, rsi_oversold=30):
        super().__init__()
        self.bollinger_window = bollinger_window
        self.bollinger_dev = bollinger_dev
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def on_starting(self):
        self.last_action = None

    def process(self, row):
        # Wait for at least bollinger_window + rsi_window rows to form
        if len(self.candles) < self.bollinger_window + self.rsi_window:
            return []

        # Calculate Bollinger Bands and RSI
        try:
            bb_result = ta.bbands(self.candles["close"], length=self.bollinger_window, std=self.bollinger_dev)
            rsi_result = ta.rsi(self.candles["close"], length=self.rsi_window)
            self.candles["BBL"] = bb_result["BBL_%d_%d.0" % (self.bollinger_window, self.bollinger_dev)]
            self.candles["BBU"] = bb_result["BBU_%d_%d.0" % (self.bollinger_window, self.bollinger_dev)]
            self.candles["RSI"] = rsi_result
        except TypeError as e:
            pass
            # logging.info("Error during Bollinger Bands and RSI calculation:", e)

        # Extract current and previous rows
        current_row = self.candles.iloc[-1]
        current_price = current_row["close"]

        # Implement Bollinger Bands and RSI Strategy
        if (
            current_price < current_row["BBL"]
            and current_row["RSI"] < self.rsi_oversold
            and (self.last_action == ACTION_SELL or self.last_action is None)
        ):
            return self.create_trade_action(ACTION_BUY, current_price, False)

        elif (
            current_price > current_row["BBU"]
            and current_row["RSI"] > self.rsi_overbought
            and (self.last_action == ACTION_BUY or self.last_action is None)
        ):
            return self.create_trade_action(ACTION_SELL, current_price, False)

        else:
            return []
