from abc import ABC, abstractmethod
import datetime
from other_services.event import Event

# an interface for the trading strategy
class TradingStrategy(ABC):

    @abstractmethod
    def execute(self, data):
        pass