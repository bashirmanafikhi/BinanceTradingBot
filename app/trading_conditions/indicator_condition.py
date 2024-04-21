from abc import ABC, abstractmethod
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