from abc import ABC, abstractmethod
import logging

import pandas as pd
from helpers.ddd.buy_command import BuyCommand
from helpers.ddd.event import Event
from helpers.ddd.sell_command import SellCommand
from helpers.settings.constants import ACTION_BUY, ACTION_SELL, ORDER_TYPE_LIMIT


# an interface for the trading strategy
class TradingStrategy(ABC):
    QUANTITY = 1
    
    def __init__(self, keep_running = True, stop_lose_range = 20, take_profit_range = 40):
        
        self.keep_running = keep_running
        self.stop_lose_range = stop_lose_range
        self.take_profit_range = take_profit_range
        self.high_close_limit = None
        self.low_close_limit = None
        
        self.buy_command = BuyCommand()
        self.sell_command = SellCommand()
        self.strategy_disabled_event = Event()
        self.strategy_enabled_event = Event()
        
        self.enable_strategy()
        self.set_processing(False)

    @abstractmethod
    def on_starting(self, row):
        pass
    
    @abstractmethod
    def process(self, row):
        pass
    
    def execute(self, data):
        signals = pd.DataFrame(data)
        signals["trades"] = signals.apply(self.try_process, axis=1)
        return signals
    
    def try_process(self, candle):
        if((self.is_enabled == False) and self.keep_running):
            self.enable_strategy()
            
        if not self.is_enabled or self.is_processing:
            return []
        try:
            self.enable_processing()
                
            if not hasattr(self, 'candles') or self.candles is None:
                # Create a DataFrame from the Series with the Series name as the column name
                self.candles = pd.DataFrame(candle).transpose()
            else:
                # Append the current row to the DataFrame
                self.candles.loc[len(self.candles)] = candle

            return self.process(candle)

        finally:
            self.disable_processing()
            
            

    def create_order(self, action, price, quantity, type=ORDER_TYPE_LIMIT):
        if(action == ACTION_BUY):
            return self.buy_command(price, quantity, type)
        elif(action == ACTION_SELL):
            return self.sell_command(price, quantity, type)

    def enable_strategy(self):
        self.on_starting()
        self.is_enabled = True
        self.strategy_enabled_event()
        print("Strategy Enabled")

    def disable_strategy(self):
        self.is_enabled = False
        self.strategy_disabled_event()
        print("Strategy Disabled")

    def set_processing(self, is_processing):
        self.is_processing = is_processing

    def enable_processing(self):
        self.set_processing(True)

    def disable_processing(self):
        self.set_processing(False)
    
    def close_trade(self, price):
        result = []    
        
        if(self.last_action == ACTION_BUY):
            result = self.create_trade_action(ACTION_SELL, price, set_stop_limits = False)
        elif(self.last_action == ACTION_SELL):
            result = self.create_trade_action(ACTION_BUY, price, set_stop_limits = False)
        
        if(len(result) != 0):
            self.disable_strategy()
            self.high_close_limit = None
            self.low_close_limit = None
            
        return result
    
    

    def create_trade_action(self, action, price, set_stop_limits = True):
        # Create an order with a fixed quantity
        is_succeed = self.create_order(action, price, self.QUANTITY)

        if is_succeed:
            #print(f"Trade: {action} - Quantity: {self.QUANTITY} - Price: {price}")
            if(set_stop_limits):
                self.set_profit_lose_limits(action, price)
            self.last_action = action
            return [{"action": action, "quantity": self.QUANTITY}]
        else:
            return []

    def set_profit_lose_limits(self, action,  price):
        if(action == ACTION_BUY):
            self.high_close_limit = price + self.take_profit_range
            self.low_close_limit = price -  self.stop_lose_range
        elif(action == ACTION_SELL):
            self.high_close_limit = price + self.stop_lose_range
            self.low_close_limit = price -  self.take_profit_range
            