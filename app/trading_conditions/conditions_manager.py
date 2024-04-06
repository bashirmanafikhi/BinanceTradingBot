from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
from typing import List

class ConditionsManager():

    def __init__(self, trading_conditions: List[TradingCondition] = None):
        if trading_conditions is None:
            trading_conditions = []
        self.conditions = trading_conditions

    def calculate(self, data):
        for condition in self.conditions:
            data = condition.calculate(data)
        return data

    def is_calculated(self, row):
        return all(condition.is_calculated(row) for condition in self.conditions)

    def get_signal(self, row):
        
        if(not self.is_calculated(row)):
            return None
        
        if (self.all_signals_equals_action(row, ACTION_BUY)):
            return ACTION_BUY
        if (self.all_signals_equals_action(row, ACTION_SELL)):
            return ACTION_SELL
        
        return None
    
    def all_signals_equals_action(self, row, action):
        return (all(condition.get_signal(row) == action for condition in self.conditions))
    
    def any_signal_equals_action(self, row, action):
        return (any(condition.get_signal(row) == action for condition in self.conditions))