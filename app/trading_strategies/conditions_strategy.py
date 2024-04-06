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
        if not self.conditions_manager.is_calculated(row):
            return
            
        price = row["close"]
        signal = self.conditions_manager.get_signal(row)

        if (self.last_action is None or self.last_action == ACTION_SELL) and signal == ACTION_BUY:
            self.current_signal = signal
        elif (self.last_action is None or self.last_action == ACTION_BUY) and signal == ACTION_SELL:
            self.current_signal = signal
        elif self.current_signal and not self.conditions_manager.any_signal_equals_action(row, self.current_signal):
            return self.create_trade_action(self.current_signal, price, False)

        return None
