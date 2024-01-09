from helpers.settings.settings import Settings
from trading_clients.binance_trading_client import BinanceTradingClient
from trading_clients.fake_trading_client import FakeTradingClient


class TradingClientFactory:
    def __init__(self):
        self.settings = Settings()

    def create_binance_trading_client(self):
        api_key = self.settings.binance.api_key
        api_secret = self.settings.binance.api_secret
        api_testnet = self.settings.binance.api_testnet

        return BinanceTradingClient(api_key, api_secret, api_testnet)

    def create_fake_trading_client(self):
        return FakeTradingClient()