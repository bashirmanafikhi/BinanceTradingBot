import pandas_ta as ta
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
from trading_strategies.trading_strategy import TradingStrategy
import helpers.my_logger as my_logger

class BollingerRSIStrategy(TradingStrategy):
    
    def __init__(self, bollinger_window=20, bollinger_dev=2, rsi_window=14, rsi_overbought=70, rsi_oversold=30):
        super().__init__()
        self.bollinger_window = bollinger_window
        self.bollinger_dev = bollinger_dev
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def format_one_zero_decimal(self,num):
        formatted = "%g" % num
        if '.' not in formatted:
            formatted += '.0'
        return formatted
        
    def calculate_bollinger(self, data):
        try:
            bb_result = ta.bbands(data["close"], length=self.bollinger_window, std=self.bollinger_dev)
            
            data["BBL"] = bb_result["BBL_%d_%s" % (self.bollinger_window, self.format_one_zero_decimal(self.bollinger_dev))]
            data["BBU"] = bb_result["BBU_%d_%s" % (self.bollinger_window, self.format_one_zero_decimal(self.bollinger_dev))]
            
        except TypeError as e:
            my_logger.error(f"Error during Bollinger Bands calculation: {e}")
            
        return data

    def calculate_rsi(self, data):
        try:
            rsi_result = ta.rsi(data["close"], length=self.rsi_window)
            data["RSI"] = rsi_result
            
        except TypeError as e:
            my_logger.error(f"Error during RSI calculation: {e}")
            
        return data

    def process_all(self, data):

        # Calculate Bollinger Bands and RSI
        if len(data) >= self.bollinger_window:
            data = self.calculate_bollinger(data)

        if len(data) >= self.rsi_window:
            data = self.calculate_rsi(data)
        
        return data

    def process_row(self, row):
        if 'BBL' not in row.index or 'RSI' not in row.index:
            return
            
        price = row["close"]

        if (
            price < row["BBL"]
            and row["RSI"] < self.rsi_oversold
            and (self.last_action == ACTION_SELL or self.last_action is None)
        ):
                return self.create_trade_action(ACTION_BUY, price)
        elif (
            price > row["BBU"]
            and row["RSI"] > self.rsi_overbought
            and (self.last_action == ACTION_BUY or self.last_action is None)
        ):
                return self.create_trade_action(ACTION_SELL, price)
            
        return None
