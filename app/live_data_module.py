# live_data_module.py
from trading_clients.trading_client_factory import TradingClientFactory
from trading_strategies.bollinger_rsi_strategy import BollingerRSIStrategy
from trading_strategies.trading_strategy import TradingStrategy
from trading_system import TradingSystem

def live_data_example():
    base_asset = "BTC"
    quote_asset = "USDT"
    trading_client_factory = TradingClientFactory()
    fake_client = trading_client_factory.create_fake_trading_client()
    binance_client = trading_client_factory.create_binance_trading_client()

    strategy = BollingerRSIStrategy(500,2,14,70,30)

    trading_system = TradingSystem(base_asset, quote_asset, strategy, binance_client)
    binance_client.start_kline_socket(symbol=f'{base_asset}{quote_asset}', callback=lambda data: trading_system.process(data))
