from abc import ABC, abstractmethod

# Define an interface for the trading client
class TradingClient(ABC):
    @abstractmethod
    def create_market_order(self, side, symbol, quantity, quoteOrderQty=None):
        pass

    @abstractmethod
    def create_limit_order(self, side, symbol, quantity, price):
        pass

    @abstractmethod
    def create_order(self, side, type, symbol, quantity, price, quoteOrderQty=None):
        pass

    @abstractmethod
    def get_asset_balance(self, asset):
        pass

    @abstractmethod
    def get_symbol_info(self, symbol):
        pass