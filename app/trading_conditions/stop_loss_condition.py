from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger

class StopLossCondition(TradingCondition):

    def __init__(self, stop_loss_percentage = 1.0, trailing_stop_loss = True, timeout = None):
        if(stop_loss_percentage <= 0 or stop_loss_percentage >= 100):
            raise ValueError("stop_loss_percentage should be between 0 and 100")
        
        self.stop_loss_percentage = stop_loss_percentage
        self.trailing_stop_loss = trailing_stop_loss
        self.timeout = timeout
        
        self.stop_loss = None

    def on_order_placed_successfully(self, price, action):
        if(action == ACTION_SELL):
            self.stop_loss = None
        if(action == ACTION_BUY):
            self.set_stop_loss(price)

    def set_stop_loss(self, price):
        new_stop_loss = self.calculate_stop_loss(price)
        if(self.stop_loss is None or (self.trailing_stop_loss and new_stop_loss > self.stop_loss)):
            self.stop_loss = new_stop_loss

    def calculate_stop_loss(self, price):
        amount = price * self.stop_loss_percentage / 100
        return price - amount
        
    def calculate(self, data):
        return data

    def get_signal(self, row):
        
        if(self.stop_loss is None):
            return None
        
        price = row["close"]
        
        # update trailing stop loss
        self.set_stop_loss(price)
            
        
        
        if (price < self.stop_loss):
            return ACTION_SELL
        
        return None