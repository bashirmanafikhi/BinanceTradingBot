from abc import ABC, abstractmethod
from helpers.enums import SignalCategory
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
from models.signal import Signal
from trading_conditions.trading_condition import TradingCondition

class IndicatorCondition(TradingCondition):
    def __init__(self, use_to_open = True, use_to_close = False):
        self.use_to_open = use_to_open
        self.use_to_close = use_to_close
  
    @abstractmethod
    def calculate(self, data):
        pass
    
    @abstractmethod
    def get_signal(self, row):
        pass
    
    @abstractmethod
    def on_order_placed_successfully(self, signal_scale):
        pass
    
    def return_signal(self, price, action):
        if((action == ACTION_BUY and not self.use_to_open) or (action == ACTION_SELL and not self.use_to_close)):
            return None
        
        return Signal(price, action, 1, SignalCategory.INDICATOR_SIGNAL)