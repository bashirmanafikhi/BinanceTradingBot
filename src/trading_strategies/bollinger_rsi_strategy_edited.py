import pandas_ta as ta
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
from helpers.settings.constants import ACTION_BUY, ACTION_SELL

from trading_strategies.trading_strategy import TradingStrategy

class BollingerRSIStrategyEdited(TradingStrategy):
    
    def __init__(self, bollinger_window=20, bollinger_dev=2, rsi_window=14, rsi_overbought=70, rsi_oversold=30):
        super().__init__()
        self.bollinger_window = bollinger_window
        self.bollinger_dev = bollinger_dev
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def on_starting(self):
        self.last_action = None

        # Initialize live plotting
        plt.ion()
        self.fig, self.ax = plt.subplots()

    def live_plot(self):
        # Plotting logic goes here
        # You can customize the plot based on your needs
        self.ax.clear()

        # Plot Close Price
        self.ax.plot(self.candles.index, self.candles["close"], label="Close Price", color='black')

        # Plot Lower Bollinger Band
        self.ax.plot(self.candles.index, self.candles["BBL"], label="Lower Bollinger Band", linestyle='--', color='blue')

        # Plot Upper Bollinger Band
        self.ax.plot(self.candles.index, self.candles["BBU"], label="Upper Bollinger Band", linestyle='--', color='red')

        self.ax.legend()
        plt.draw()
        plt.pause(0.001)


    def process(self, row):
        # Wait for at least bollinger_window + rsi_window rows to form
        if len(self.candles) < self.bollinger_window + self.rsi_window:
            return []

        # Calculate Bollinger Bands and RSI
        try:
            bb_result = ta.bbands(self.candles["close"], length=self.bollinger_window, std=self.bollinger_dev)
            rsi_result = ta.rsi(self.candles["close"], length=self.rsi_window)
            self.candles["BBL"] = bb_result["BBL_%d_%d.0" % (self.bollinger_window, self.bollinger_dev)]
            self.candles["BBU"] = bb_result["BBU_%d_%d.0" % (self.bollinger_window, self.bollinger_dev)]
            self.candles["RSI"] = rsi_result
        except TypeError as e:
            pass
            # logging.info("Error during Bollinger Bands and RSI calculation:", e)

        # Call live plotting method
        self.live_plot()

        # Extract current and previous rows
        current_row = self.candles.iloc[-1]
        current_price = current_row["close"]

        # Implement Bollinger Bands and RSI Strategy
        if (
            current_price < current_row["BBL"]
            and current_row["RSI"] < self.rsi_oversold
            and (self.last_action == ACTION_SELL or self.last_action is None)
        ):
            return self.create_trade_action(ACTION_BUY, current_price, False)

        elif (
            current_price > current_row["BBU"]
            and current_row["RSI"] > self.rsi_overbought
            and (self.last_action == ACTION_BUY or self.last_action is None)
        ):
            return self.create_trade_action(ACTION_SELL, current_price, False)

        else:
            return []
