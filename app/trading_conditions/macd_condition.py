from trading_conditions.indicator_condition import IndicatorCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger


class MacdCondition(IndicatorCondition):

    def __init__(self, macd_fast=12, macd_slow=26, macd_signal=9, use_to_open=True, use_to_close=False):
        super().__init__(use_to_open=use_to_open, use_to_close=use_to_close)
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        
        self.previous_macd = None
        self.previous_macd_signal = None

    def calculate(self, data):
        if len(data) < max(self.macd_fast, self.macd_slow, self.macd_signal):
            return data

        try:
            macd_result = ta.macd(data["close"], fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)
            data[self.get_macd_key()] = macd_result[self.get_macd_key()]
            data[self.get_macd_signal_key()] = macd_result[self.get_macd_signal_key()]
            data[self.get_macd_histogram_key()] = macd_result[self.get_macd_histogram_key()]
        except Exception as e:
            my_logger.error(f"Error during MACD calculation: {e}")
        return data

    def on_order_placed_successfully(self, signal_scale):
        pass

    def get_signal(self, row):
        if self.get_macd_key() not in row.index or self.get_macd_signal_key() not in row.index:
            return None
        
        previous_macd = self.previous_macd
        previous_macd_signal = self.previous_macd_signal

        new_macd = row[self.get_macd_key()]
        new_macd_signal = row[self.get_macd_signal_key()]
        
        self.previous_macd = new_macd
        self.previous_macd_signal = new_macd_signal
        

        if (new_macd < 0 and new_macd_signal < 0 and previous_macd < previous_macd_signal and new_macd > new_macd_signal):
            return self.return_signal(row["close"], ACTION_BUY)
        if (new_macd > 0 and new_macd_signal > 0 and previous_macd > previous_macd_signal and new_macd < new_macd_signal):
            return self.return_signal(row["close"], ACTION_SELL)
        

        return None
    
    def get_macd_key(self):
        return "MACD_%d_%d_%d" % (self.macd_fast, self.macd_slow, self.macd_signal)

    def get_macd_signal_key(self):
        return "MACDs_%d_%d_%d" % (self.macd_fast, self.macd_slow, self.macd_signal)

    def get_macd_histogram_key(self):
        return "MACDh_%d_%d_%d" % (self.macd_fast, self.macd_slow, self.macd_signal)
