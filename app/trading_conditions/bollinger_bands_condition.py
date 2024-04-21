from trading_conditions.indicator_condition import IndicatorCondition
from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger

class BollingerBandsCondition(IndicatorCondition):
    def __init__(self, bollinger_window=20, bollinger_dev=2, use_to_open = True, use_to_close = False):
        super().__init__(use_to_open = use_to_open, use_to_close = use_to_close)
        self.bollinger_window = bollinger_window
        self.bollinger_dev = bollinger_dev

    def on_order_placed_successfully(self, signal_scale):
        pass
    
    def calculate(self, data):
        if len(data) >= self.bollinger_window:
            data = self.calculate_bollinger_band(data)
        return data

    def get_signal(self, row):
        price = row["close"]

        if (self.get_lower_band_key() in row.index and price < row[self.get_lower_band_key()]):
            return ACTION_BUY
        elif (self.get_upper_band_key() in row.index and price > row[self.get_upper_band_key()]):
            return ACTION_SELL
        
        return None
    

    def calculate_bollinger_band(self, data):
        try:
            bb_result = ta.bbands(data["close"], length=self.bollinger_window, std=self.bollinger_dev)
            
            data[self.get_lower_band_key()] = bb_result[self.get_lower_band_key()]
            data[self.get_upper_band_key()] = bb_result[self.get_upper_band_key()]
            
        except TypeError as e:
            my_logger.error(f"Error during Bollinger Bands calculation: {e}")
            
        return data
    
    
    def format_one_zero_decimal(self,num):
        formatted = "%g" % num
        if '.' not in formatted:
            formatted += '.0'
        return formatted
    
    def get_lower_band_key(self):
        return "BBL_%d_%s" % (self.bollinger_window, self.format_one_zero_decimal(self.bollinger_dev))
    
    def get_upper_band_key(self):
        return "BBU_%d_%s" % (self.bollinger_window, self.format_one_zero_decimal(self.bollinger_dev))