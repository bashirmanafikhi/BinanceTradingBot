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
        
        def check_condition(condition):
            return ((action == ACTION_BUY and condition.use_to_open) or 
                    (action == ACTION_SELL and condition.use_to_close))
        
        filtered_conditions = list(filter(check_condition , self.conditions))
        if(len(filtered_conditions) == 0):
            return False
        
        return (all(condition.get_signal(row) == action for condition in filtered_conditions))
    
    def any_signal_equals_action(self, row, action):
        return (any(condition.get_signal(row) == action for condition in self.conditions))