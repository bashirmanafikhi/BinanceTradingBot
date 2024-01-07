from datetime import datetime, timedelta
import pandas as pd
import logging
import sys
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
from helpers.trading_data_service import TradingDataService
from trading_clients.trading_client import TradingClient
from trading_clients.trading_client_factory import TradingClientFactory
from trading_strategies.bollinger_rsi_strategy import BollingerRSIStrategy
from trading_strategies.bollinger_rsi_strategy_stop_limit import BollingerRSIStrategyStopLimit
from trading_strategies.ema_crossover_strategy import EMACrossoverStrategy
from trading_strategies.ema_rsi_strategy import EMARSIStrategy
from trading_strategies.macd_strategy import MACDStrategy
from trading_strategies.martingale_strategy import MartingaleStrategy
from trading_strategies.moving_average_crossover_strategy import plot_signals
from trading_strategies.trading_strategy import TradingStrategy
from trading_system import TradingSystem

def configure_logging():
    # Configure logging to write to the console
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def get_trading_system():
    trading_client_factory = TradingClientFactory()
    fake_client: TradingClient = trading_client_factory.create_fake_trading_client()
    strategy: TradingStrategy = BollingerRSIStrategy(30,2,13,70,30)
    
    symbol = "BTCUSDT"
    trading_system = TradingSystem(symbol, strategy, fake_client)
    return trading_client_factory, symbol, trading_system

def get_historical_data():
    # Create an instance of the TradingDataService
    trading_data_service = TradingDataService()
    success = trading_data_service.load_data()
    data = pd.DataFrame()
    if success:
        start_date = datetime(2017, 1, 3, 1, 0, 0)  # (year, month, day, hour, minute, second)
        # end_date = datetime(2017, 1,4, 1, 0, 0)  # (year, month, day, hour, minute, second)
        end_date = start_date + timedelta(days=14)
        data = trading_data_service.query_data(start_date, end_date)
    else:
        print("Data didn't load.")
    return data

def historical_data_example():
    # Load historical data
    data = get_historical_data()

    # Run the strategy on the data
    signals = trading_system.run_strategy(data)
    print(f"Total Commission: {trading_system.trading_client.total_paid_commission}")
    trading_system.calculate_profit_loss()

    plot_signals(signals)
    
def live_data_example():
    binance_client: TradingClient = trading_client_factory.create_binance_trading_client()
    binance_client.start_kline_socket(symbol=symbol, callback=handle_live_kline_message)

def handle_live_kline_message(data):
    # Run the strategy on the data
    result_data = trading_system.run_strategy(data)

if __name__ == "__main__":
    #configure_logging()
    trading_client_factory, symbol, trading_system = get_trading_system()

    # Uncomment one of the following lines based on the scenario you want to run
    # live_data_example()
    historical_data_example()
