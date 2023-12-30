from abc import ABC, abstractmethod
import logging

import pandas as pd
from helpers.ddd.buy_command import BuyCommand
from helpers.ddd.event import Event
from helpers.ddd.sell_command import SellCommand
from helpers.settings.constants import ACTION_BUY, ACTION_SELL, ORDER_TYPE_LIMIT


# an interface for the trading strategy
class TradingStrategy(ABC):
    def __init__(self):
        self.enable_strategy()
        self.set_processing(False)
        
        self.buy_command = BuyCommand()
        self.sell_command = SellCommand()
        self.strategy_disabled_event = Event()

    @abstractmethod
    def process(self, row):
        pass
    
    def execute(self, data):
        signals = pd.DataFrame(data[["close"]])
        signals["trades"] = signals.apply(self.process, axis=1)
        return signals

    def create_order(self, action, price, quantity, type=ORDER_TYPE_LIMIT):
        if(action == ACTION_BUY):
            return self.buy_command(price, quantity, type)
        elif(action == ACTION_SELL):
            return self.sell_command(price, quantity, type)

    def enable_strategy(self):
        self.is_enabled = True
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
