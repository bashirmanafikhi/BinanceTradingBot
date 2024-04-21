import pandas_ta as ta
from trading_conditions.conditions_manager import ConditionsManager
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
from trading_strategies.trading_strategy import TradingStrategy
import helpers.my_logger as my_logger

class ConditionsStrategy(TradingStrategy):
    
    def __init__(self, trading_conditions: None):
        super().__init__()
        self.conditions_manager = ConditionsManager(trading_conditions)
      
    def process_all(self, data):
        data = self.conditions_manager.calculate(data)
        return data
    
    def process_row(self, row):
        price = row["close"]
        
        extra_orders_condition = self.conditions_manager.get_extra_orders_condition()
        if(extra_orders_condition):
            signal = extra_orders_condition.get_signal(row)
            if(signal and signal.action == ACTION_BUY):
                signal_to_return = self.create_trade_action(signal.action, price, signal.scale)
                if(signal_to_return):
                    self.conditions_manager.on_order_placed_successfully(signal_to_return)
                return signal_to_return
                
                
        
        if ((self.last_action is None or self.last_action == ACTION_SELL) and self.conditions_manager.should_buy(row)):
            signal_to_return = self.create_trade_action(ACTION_BUY, price)
            self.conditions_manager.on_order_placed_successfully(signal_to_return)
            return signal_to_return
            
        elif((self.last_action is None or self.last_action == ACTION_BUY) and self.conditions_manager.should_sell(row)):
            signal_to_return = self.create_trade_action(ACTION_SELL, price)
            self.conditions_manager.on_order_placed_successfully(signal_to_return)
            return signal_to_return

        return None
