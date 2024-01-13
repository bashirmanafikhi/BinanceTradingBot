from abc import ABC, abstractmethod
import logging
import pandas as pd
from helpers.ddd.buy_command import BuyCommand
from helpers.ddd.event import Event
from helpers.ddd.sell_command import SellCommand
from helpers.settings.constants import ACTION_BUY, ACTION_SELL, ORDER_TYPE_LIMIT
import matplotlib.pyplot as plt

# an interface for the trading strategy
class TradingStrategy(ABC):
    QUANTITY = 1
    PLOT_WINDOW = 50
    
    def __init__(self, stop_lose_range = 20, take_profit_range = 40):
        self.stop_lose_range = stop_lose_range
        self.take_profit_range = take_profit_range
        self.high_close_limit = None
        self.low_close_limit = None
        self.last_action = None
                
        self.buy_command = BuyCommand()
        self.sell_command = SellCommand()
        self.trade_closed_event = Event()
        
        self.set_processing(False)
        
    
    @abstractmethod
    def process_row(self, row):
        pass
    
    @abstractmethod
    def process_all(self, data):
        pass
    
        
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
        
        self.live_plot(signals)

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
      
    
                
    def live_plot(self, all_signals):
        if not hasattr(self, 'fig'):
            #plt.ion()
            self.fig, self.ax = plt.subplots()
            self.lines, = self.ax.plot([], [], label='Close Price')
            self.bbu_line, = self.ax.plot([], [], label='Upper Band', linestyle='--')
            self.bbl_line, = self.ax.plot([], [], label='Lower Band', linestyle='--')
            self.ax.legend()
        
        signals = all_signals.tail(self.PLOT_WINDOW)
        
        x_data = signals.index
        y_data_close = signals['close'] 
        
        self.lines.set_xdata(x_data)
        self.lines.set_ydata(y_data_close)
        
        if 'BBL' in signals.columns:
            y_data_bbl = signals['BBL']
            self.bbl_line.set_xdata(x_data)
            self.bbl_line.set_ydata(y_data_bbl)
            
        if 'BBU' in signals.columns:
            y_data_bbu = signals['BBU']
            self.bbu_line.set_xdata(x_data)
            self.bbu_line.set_ydata(y_data_bbu)
        
        # Iterate through signals and annotate buy/sell points
        for index, signal_row in signals.iterrows():
            if signal_row.signal is not None:
                action = signal_row.signal.get("action", "")
                try:
                    if action == ACTION_BUY:
                        self.ax.scatter(index, signal_row.close, marker='o', color='green', s=20, zorder=5)
                    elif action == ACTION_SELL:
                        self.ax.scatter(index, signal_row.close, marker='o', color='red', s=20, zorder=5)    
                except:
                    print("error while drawing action scatter")
                
                    
        self.ax.relim()
        self.ax.autoscale_view()
        plt.pause(2)
            
            
            
            
            
    def create_order(self, action, price, quantity, type=ORDER_TYPE_LIMIT):
        if(action == ACTION_BUY):
            return self.buy_command(price, quantity, type)
        elif(action == ACTION_SELL):
            return self.sell_command(price, quantity, type)

    def close_order(self, price):
        result = None    
        
        if(self.last_action == ACTION_BUY):
            result = self.create_trade_action(ACTION_SELL, price, set_stop_limits = False)
        elif(self.last_action == ACTION_SELL):
            result = self.create_trade_action(ACTION_BUY, price, set_stop_limits = False)
        
        if(len(result) != 0):
            self.trade_closed_event()
            self.high_close_limit = None
            self.low_close_limit = None
            
        return result
    
    

    def create_trade_action(self, action, price, set_stop_limits = True):
        # Create an order with a fixed quantity
        is_succeed = self.create_order(action, price, self.QUANTITY)

        if is_succeed:
            logging.info(f"Trade: {action} - Quantity: {self.QUANTITY} - Price: {price}")
            if(set_stop_limits):
                self.set_profit_lose_limits(action, price)
            self.last_action = action
            return {"action": action, "quantity": self.QUANTITY}
        else:
            return None

    def set_profit_lose_limits(self, action,  price):
        if(action == ACTION_BUY):
            self.high_close_limit = price + self.take_profit_range
            self.low_close_limit = price -  self.stop_lose_range
        elif(action == ACTION_SELL):
            self.high_close_limit = price + self.stop_lose_range
            self.low_close_limit = price -  self.take_profit_range
        
    def enable_processing(self):
        self.set_processing(True)

    def disable_processing(self):
        self.set_processing(False)

    def set_processing(self, is_processing):
        self.is_processing = is_processing
