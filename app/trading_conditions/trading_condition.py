from abc import ABC, abstractmethod


class TradingCondition(ABC):
    def __init__(self, use_to_open = True, use_to_close = False):
        self.use_to_open = use_to_open
        self.use_to_close = use_to_close
  
    @abstractmethod
    def calculate(self, data):
        pass

    @abstractmethod
    def is_calculated(self, row):
        pass

    @abstractmethod
    def get_signal(self, row):
        pass