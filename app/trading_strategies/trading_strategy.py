from abc import ABC, abstractmethod
from models.signal import Signal
import helpers.my_logger as my_logger
import pandas as pd
from helpers.ddd.buy_command import BuyCommand
from helpers.ddd.event import Event
from helpers.ddd.sell_command import SellCommand
from helpers.settings.constants import ACTION_BUY, ACTION_SELL, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET
import matplotlib.pyplot as plt

# an interface for the trading strategy
class TradingStrategy(ABC):
    PLOT_WINDOW = 100
    
    def __init__(self):
        self.last_action = ACTION_SELL
            
        self.buy_command = BuyCommand()
        self.sell_command = SellCommand()
        
        self.create_order_tries_limit = 3
        self.create_order_tries_counter = 0
        self.set_processing(False)
        
    
    @abstractmethod
    def process_row(self, row):
        pass
    
    @abstractmethod
    def process_all(self, data):
        pass
    
    
    def can_sell(self):
        return (self.last_action is None or self.last_action == ACTION_BUY)
    
    def can_buy(self):
        return (self.last_action is None or self.last_action == ACTION_SELL)
    
    def execute(self, data):
        # Check if data is empty or None
        if data is None or data.empty:
            return None

        # Live data case
        if len(data) == 1:
            # If 'self.data' doesn't exist, initialize it with the provided data
            if not hasattr(self, 'data'):
                self.data = data
            else:
                # Append the new data to the existing DataFrame
                self.data = self.data = pd.concat([self.data, data], ignore_index=True)

            # Process all data and get signals
            signals = self.process_all(self.data)

            # Select the last row using iloc
            last_signal = signals.iloc[-1]
            
            # Now, you can safely update the "signal" column using at
            signals.at[signals.index[-1], "signal"] = self.execute_candle(last_signal)


        # Backtest data case
        else:
            # Process all data and calculate signals
            signals = self.process_all(data)

            # Apply execute_candle to each row and update the "signal" column
            signals["signal"] = signals.apply(self.execute_candle, axis=1)
        
        #self.live_plot(signals)

        # Return the resulting DataFrame with signals
        return signals

    
    def execute_candle(self, candle):
            
        if self.is_processing:
            return None
        
        try:
            self.enable_processing()
            return self.process_row(candle)

        finally:
            self.disable_processing()
    
    def create_trade_action(self, signal):
        if(self.create_order_tries_counter == self.create_order_tries_limit):
            my_logger.warning(f"create order failed {self.create_order_tries_counter} times, strategy is disabled.")
            return None
                
        self.create_order_tries_counter += 1
        # Create an order with a fixed scale
        is_succeed = self.create_order(signal.action, signal.price, signal.scale)

        if is_succeed:
            self.last_action = signal.action
            self.create_order_tries_counter = 0
            return signal
        else:
            if(self.create_order_tries_counter == self.create_order_tries_limit):
                my_logger.error(f"create order failed {self.create_order_tries_counter} times, strategy is disabled.")
                # todo send telegram notification
            return None
        
    def create_order(self, action, price, scale, type=ORDER_TYPE_MARKET):
        if(action == ACTION_BUY):
            return self.buy_command(price, scale, type)
        elif(action == ACTION_SELL):
            return self.sell_command(price, scale, type)
        
    def enable_processing(self):
        self.set_processing(True)

    def disable_processing(self):
        self.set_processing(False)

    def set_processing(self, is_processing):
        self.is_processing = is_processing

      
    
                
    # def live_plot(self, all_signals):
    #     if not hasattr(self, 'fig'):
    #         #plt.ion()
    #         self.fig, (self.ax, self.ax_rsi) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
    #         self.lines, = self.ax.plot([], [], label='Close Price')
    #         self.bbu_line, = self.ax.plot([], [], label='Upper Band', linestyle='--')
    #         self.bbl_line, = self.ax.plot([], [], label='Lower Band', linestyle='--')
    #         self.ax.legend()

    #         self.ax_rsi.plot([], [], label='RSI', color='purple')
    #         self.ax_rsi.axhline(70, linestyle='--', color='orange')  # Overbought threshold
    #         self.ax_rsi.axhline(30, linestyle='--', color='blue')    # Oversold threshold
    #         self.ax_rsi.set_ylabel('RSI')
    #         self.ax_rsi.legend()
        
    #     signals = all_signals.tail(self.PLOT_WINDOW)
        
    #     x_data = signals.index
    #     y_data_close = signals['close'] 
        
    #     self.lines.set_xdata(x_data)
    #     self.lines.set_ydata(y_data_close)
        
    #     if 'BBL' in signals.columns:
    #         y_data_bbl = signals['BBL']
    #         self.bbl_line.set_xdata(x_data)
    #         self.bbl_line.set_ydata(y_data_bbl)
            
    #     if 'BBU' in signals.columns:
    #         y_data_bbu = signals['BBU']
    #         self.bbu_line.set_xdata(x_data)
    #         self.bbu_line.set_ydata(y_data_bbu)
        
    #     # Plot RSI
    #     if 'RSI' in signals.columns:
    #         x_data_rsi = signals.index
    #         y_data_rsi = signals['RSI']
    #         self.ax_rsi.lines[0].set_xdata(x_data_rsi)
    #         self.ax_rsi.lines[0].set_ydata(y_data_rsi)
        
    #     # Iterate through signals and annotate buy/sell points
    #     for index, signal_row in signals.iterrows():
    #         if signal_row.signal is not None:
    #             action = signal_row.signal.get("action", "")
    #             try:
    #                 if action == ACTION_BUY:
    #                     self.ax.scatter(index, signal_row.close, marker='o', color='green', s=20, zorder=5)
    #                 elif action == ACTION_SELL:
    #                     self.ax.scatter(index, signal_row.close, marker='o', color='red', s=20, zorder=5)    
    #             except:
    #                 print("error while drawing action scatter")
                
    #     self.ax.relim()
    #     self.ax.autoscale_view()

    #     self.ax_rsi.relim()
    #     self.ax_rsi.autoscale_view()

    #     plt.pause(2)
            
            
        