import pandas as pd
from helpers.binance_websocket import get_binance_websocket_service
from helpers.settings.constants import ACTION_BUY, ACTION_SELL, ORDER_TYPE_LIMIT
from helpers.trading_data_service import TradingDataService
from trading_clients.trading_client import TradingClient
from trading_clients.trading_client_factory import TradingClientFactory
from trading_strategies.martingale_strategy import MartingaleStrategy
from trading_strategies.moving_average_crossover_strategy import (
    moving_average_crossover_strategy,
    plot_signals,
    exponential_moving_average_crossover_strategy,
)
import matplotlib.pyplot as plt
from trading_strategies.simple_moving_average_strategy import SimpleMovingAverage
from trading_strategies.trading_strategy import TradingStrategy

from trading_system import TradingSystem
import logging
import sys

def configure_logging():
    # Configure logging to write to the console
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


symbol = "BTCUSDT"

# Choose a strategy
# strategy: TradingStrategy = SimpleMovingAverage(20)
strategy: TradingStrategy = MartingaleStrategy(keep_running=True)

# Create a BinanceTradingClient instance
trading_client_factory = TradingClientFactory()
fake_client: TradingClient = trading_client_factory.create_fake_trading_client()

# Create a trading system with the selected strategy and BinanceTradingClient
trading_system = TradingSystem(symbol, strategy, fake_client)


# Example usage:
data_dir = 'C:\\Users\\pc\\Desktop\\TradingProjects\\Bitcoin Historical Dataset'
file_name = 'BTC-2017min.csv'

# Create an instance of the TradingDataService
trading_data_service = TradingDataService(data_dir, file_name)



def historical_data_example():
        
    # Load historical data
    success = trading_data_service.load_data()
    data = pd.DataFrame()
    if success:
        data = trading_data_service.query_one_month()
        # data = trading_data_service.query_data(start_date, end_date)

        if data is not None:
            print(data.head())
    else:
        print("data didn't loaded.")
    
    ##data = binance_client.fetch_historical_data(symbol, "1m")

    # Run the strategy on the data
    result_data = trading_system.run_strategy(data)

    # Print the result
    # print(result_data)


def live_data_example():

    binance_client: TradingClient = trading_client_factory.create_binance_trading_client()
    binance_client.start_kline_socket(symbol=symbol, callback=handle_live_kline_message)

def handle_live_kline_message(data):
    # Run the strategy on the data
    result_data = trading_system.run_strategy(data)


def movingAverageExample():
    # Fetch historical data
    symbol = "BTCUSDT"
    interval = "5m"
    trading_client_factory = TradingClientFactory()
    client = trading_client_factory.create_binance_trading_client()

    historical_data = client.fetch_historical_data(symbol, interval, limit=250)

    # Define moving average window periods
    short_window = 50
    long_window = 200

    # Generate signals
    signals = exponential_moving_average_crossover_strategy(
        historical_data, short_window, long_window
    )

    # Print the generated signals
    plot_signals(historical_data, signals)


if __name__ == "__main__":
    configure_logging()
    # live_data_example()
    historical_data_example()
    # movingAverageExample()
