
import pandas as pd
from other_services.event import Event
from trading_strategies.trading_strategy import TradingStrategy


class SimpleMovingAverage(TradingStrategy):
    def __init__(self, window_size):
        self.window_size = window_size
        self.previous_data = pd.DataFrame()

    def execute(self, data):
        # Concatenate the current data with the previous data
        data = pd.concat([self.previous_data, data])

        # Update the previous_data for the next iteration
        self.previous_data = data.tail(1)

        # Implement your strategy logic here, e.g., calculate moving average
        data['SMA'] = data['close'].rolling(window=self.window_size).mean()

        # Generate signals
        signals = pd.DataFrame({'buy': data['close'] > data['SMA'], 'sell': data['close'] < data['SMA']})

        return signals