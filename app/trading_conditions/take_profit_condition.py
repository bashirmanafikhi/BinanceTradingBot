from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger

class TakeProfitCondition(TradingCondition):

    def __init__(self,take_profit_percentage = 2.0, trailing_take_profit = False, trailing_take_profit_deviation_percentage = 0.4):
        if(take_profit_percentage <= 0 or take_profit_percentage >= 100):
            raise ValueError("take_profit_percentage should be between 0 and 100")
        
        if(trailing_take_profit_deviation_percentage <= 0 or trailing_take_profit_deviation_percentage >= 100):
            raise ValueError("trailing_take_profit_deviation_percentage should be between 0 and 100")
        
        super().__init__()
        
        self.take_profit_percentage = take_profit_percentage
        self.trailing_take_profit = trailing_take_profit
        self.trailing_take_profit_deviation_percentage = trailing_take_profit_deviation_percentage
        
        self.take_profit = None

    def on_order_placed_successfully(self, price, action):
        if(action == ACTION_SELL):
            self.take_profit = None
        if(action == ACTION_BUY):
            self.set_take_profit(price)

    def set_take_profit(self, price):
        self.take_profit = self.calculate_take_profit(price)

    def calculate_take_profit(self, price):
        amount = price * self.take_profit_percentage / 100
        return price + amount
        
    def calculate(self, data):
        return data

    def get_signal(self, row):
        
        if(self.take_profit is None):
            return None
        
        price = row["close"]
        
        if (price > self.take_profit):
            return ACTION_SELL
        
        return None