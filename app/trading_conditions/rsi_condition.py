from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger

class RSICondition(TradingCondition):
    RSI_KEY = "RSI"

    def __init__(self, rsi_window = 14, rsi_overbought=70, rsi_oversold=30):
        super().__init__()
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def calculate(self, data):
        if len(data) >= self.rsi_window:
            data = self.calculate_rsi(data, self.rsi_window)
        
        return data

    def is_calculated(self, row):
        return self.RSI_KEY in row.index

    def get_signal(self, row):
        
        if(not self.is_calculated(row)):
            return None
        
        if (row[self.RSI_KEY] < self.rsi_oversold):
            return ACTION_BUY
        elif (row[self.RSI_KEY] > self.rsi_overbought):
            return ACTION_SELL
        
        return None
    
    def calculate_rsi(self, data, rsi_window):
        try:
            rsi_result = ta.rsi(data["close"], length=rsi_window)
            data[self.RSI_KEY] = rsi_result
            
        except TypeError as e:
            my_logger.error(f"Error during RSI calculation: {e}")
            
        return data