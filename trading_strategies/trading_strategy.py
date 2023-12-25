from abc import ABC, abstractmethod
from typing import Type

# Abstract base class for TradingStrategy
class TradingStrategy(ABC):
    def __init__(self):
        self.binance_client

    @abstractmethod
    def execute_trade(self):
        pass
