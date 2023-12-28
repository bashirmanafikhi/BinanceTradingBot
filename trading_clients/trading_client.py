from abc import ABC, abstractmethod

# Define an interface for the trading client
class TradingClient(ABC):
    @abstractmethod
    def buy(self, symbol, quantity, price, quoteOrderQty=None):
        pass

    @abstractmethod
    def sell(self, symbol, quantity, price, quoteOrderQty=None):
        pass

    @abstractmethod
    def get_balance(self, symbol):
        pass

    @abstractmethod
    def get_symbol_info(self, symbol):
        pass