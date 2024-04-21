from trading_conditions.extra_orders_condition import ExtraOrdersCondition
from trading_conditions.indicator_condition import IndicatorCondition
from trading_conditions.take_profit_condition import TakeProfitCondition
from trading_conditions.stop_loss_condition import StopLossCondition
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
    
    def on_order_placed_successfully(self, signal_scale):
        for condition in self.conditions:
            condition.on_order_placed_successfully(signal_scale)
            
    def get_extra_orders_condition(self):
        return next((x for x in self.conditions if isinstance(x, ExtraOrdersCondition)), None)

    def should_buy(self, row):
        
        if (self.take_profit_equal_action(row, ACTION_BUY) 
            or self.stop_loss_equal_action(row, ACTION_BUY) 
            or self.all_indicators_equal_action(row, ACTION_BUY)):
            return True
        
        return False
        
    def should_sell(self, row):
        
        if (self.take_profit_equal_action(row, ACTION_SELL) 
            or self.stop_loss_equal_action(row, ACTION_SELL) 
            or self.all_indicators_equal_action(row, ACTION_SELL)):
            return True
        
        return False
    
    def take_profit_equal_action(self, row, action):
        # Check if there is at least one instance of TakeProfitCondition
        if any(isinstance(condition, TakeProfitCondition) for condition in self.conditions):
            return all(condition.get_signal(row) == action for condition in self.conditions if isinstance(condition, TakeProfitCondition))
        else:
            return False

    def stop_loss_equal_action(self, row, action):
        # Check if there is at least one instance of StopLossCondition
        if any(isinstance(condition, StopLossCondition) for condition in self.conditions):
            return all(condition.get_signal(row) == action for condition in self.conditions if isinstance(condition, StopLossCondition))
        else:
            return False

    
    def all_indicators_equal_action(self, row, action):
        def check_condition(condition):
            return (isinstance(condition, IndicatorCondition) 
                    and ((action == ACTION_BUY and condition.use_to_open) 
                        or (action == ACTION_SELL and condition.use_to_close)))
        
        filtered_conditions = list(filter(check_condition , self.conditions))
        if(filtered_conditions):
            return (all(condition.get_signal(row) == action for condition in filtered_conditions))
        return False