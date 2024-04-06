from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger

class BollingerBandsCondition(TradingCondition):
    UPPER_BAND_KEY = "BBU"
    LOWER_BAND_KEY = "BBL"

    def __init__(self, bollinger_window=20, bollinger_dev=2):
        super().__init__()
        self.bollinger_window = bollinger_window
        self.bollinger_dev = bollinger_dev


    def calculate(self, data):
        if len(data) >= self.bollinger_window:
            data = self.calculate_bollinger_band(data)
        
        return data


    def is_calculated(self, row):
        return self.LOWER_BAND_KEY in row.index and self.UPPER_BAND_KEY in row.index 


    def get_signal(self, row):

        if(not self.is_calculated(row)):
            return None
        
        price = row["close"]

        if (price < row[self.LOWER_BAND_KEY]):
            return ACTION_BUY
        elif (price > row[self.UPPER_BAND_KEY]):
            return ACTION_SELL
        
        return None
    

    def calculate_bollinger_band(self, data):
        try:
            bb_result = ta.bbands(data["close"], length=self.bollinger_window, std=self.bollinger_dev)
            
            data[self.LOWER_BAND_KEY] = bb_result["BBL_%d_%s" % (self.bollinger_window, self.format_one_zero_decimal(self.bollinger_dev))]
            data[self.UPPER_BAND_KEY] = bb_result["BBU_%d_%s" % (self.bollinger_window, self.format_one_zero_decimal(self.bollinger_dev))]
            
        except TypeError as e:
            my_logger.error(f"Error during Bollinger Bands calculation: {e}")
            
        return data
    
    
    def format_one_zero_decimal(self,num):
        formatted = "%g" % num
        if '.' not in formatted:
            formatted += '.0'
        return formatted