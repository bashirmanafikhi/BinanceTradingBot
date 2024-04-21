from abc import ABC, abstractmethod

class TradingCondition(ABC):
      
    @abstractmethod
    def calculate(self, data):
        pass
    
    @abstractmethod
    def get_signal(self, row):
        pass
    
    @abstractmethod
    def on_order_placed_successfully(self, signal_scale):
        pass