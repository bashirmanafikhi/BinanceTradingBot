

# I am not sure of this condition, it is from chatGPT 


# from trading_conditions.trading_condition import TradingCondition
# from helpers.settings.constants import ACTION_BUY, ACTION_SELL
# import pandas_ta as ta
# import helpers.my_logger as my_logger

# class MACDCondition(TradingCondition):
#     MACD_KEY = "MACD"
#     SIGNAL_KEY = "MACD_Signal"

#     def __init__(self, macd_fast=12, macd_slow=26, signal_period=9):
#         super().__init__()
#         self.macd_fast = macd_fast
#         self.macd_slow = macd_slow
#         self.signal_period = signal_period

#     def calculate(self, data):
#         if len(data) >= self.macd_slow:
#             data = self.calculate_macd(data, self.macd_fast, self.macd_slow, self.signal_period)
#         return data

#     def is_calculated(self, row):
#         return self.MACD_KEY in row.index and self.SIGNAL_KEY in row.index

#     def get_signal(self, row):
#         if not self.is_calculated(row):
#             return None
        
#         macd = row[self.MACD_KEY]
#         signal = row[self.SIGNAL_KEY]

#         if macd > signal:
#             return ACTION_BUY
#         elif macd < signal:
#             return ACTION_SELL
#         else:
#             return None

#     def calculate_macd(self, data, fast_period, slow_period, signal_period):
#         try:
#             macd_result = ta.macd(data["close"], fast_period=fast_period, slow_period=slow_period, signal_period=signal_period)
#             data[self.MACD_KEY] = macd_result["MACD"]
#             data[self.SIGNAL_KEY] = macd_result["MACD_Signal"]
#         except TypeError as e:
#             my_logger.error(f"Error during MACD calculation: {e}")
#         return data
