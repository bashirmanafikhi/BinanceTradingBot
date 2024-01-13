# live_data_module.py
from trading_clients.trading_client_factory import TradingClientFactory
from trading_strategies.bollinger_rsi_strategy import BollingerRSIStrategyEdited
from trading_strategies.trading_strategy import TradingStrategy
from trading_system import TradingSystem

def live_data_example():
    symbol = "BTCUSDT"
    trading_client_factory = TradingClientFactory()
    fake_client = trading_client_factory.create_fake_trading_client()
    binance_client = trading_client_factory.create_binance_trading_client()

    strategy = BollingerRSIStrategyEdited(10, 1, 10, 50, 50)

    trading_system = TradingSystem(symbol, strategy, binance_client)
    binance_client.start_kline_socket(symbol=symbol, callback=lambda data: trading_system.run_strategy(data))
