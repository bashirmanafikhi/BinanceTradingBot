from abc import ABC, abstractmethod


class TradingCondition(ABC):
    def __init__(self):
        pass
  
    @abstractmethod
    def calculate(self, data):
        pass

    @abstractmethod
    def is_calculated(self, row):
        pass

    @abstractmethod
    def get_signal(self, row):
        pass