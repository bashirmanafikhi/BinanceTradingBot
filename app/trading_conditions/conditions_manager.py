from models.signal import Signal
from trading_conditions.extra_orders_condition import ExtraOrdersCondition
from trading_conditions.indicator_condition import IndicatorCondition
from trading_conditions.take_profit_condition import TakeProfitCondition
from trading_conditions.stop_loss_condition import StopLossCondition
from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
from typing import List
from typing import List, Type, Union

class ConditionsManager:

    def __init__(self, trading_conditions: List['TradingCondition'] = None):
        self.conditions = trading_conditions or []

    def calculate(self, data):
        for condition in self.conditions:
            data = condition.calculate(data)
        return data
    
    def on_order_placed_successfully(self, signal: 'Signal') -> None:
        for condition in self.conditions:
            condition.on_order_placed_successfully(signal)
    
    def on_conditions_changed(self, new_conditions) -> None:
            new_extra_order_condition = self.get_extra_orders_condition(new_conditions)
            old_extra_order_condition = self.get_extra_orders_condition()
            old_extra_order_condition.on_condition_changed(new_extra_order_condition)
            
            new_take_profit_condition = self.get_take_profit_condition(new_conditions)
            old_take_profit_condition = self.get_take_profit_condition()
            old_take_profit_condition.on_condition_changed(new_take_profit_condition)
            
            new_stop_loss_condition = self.get_stop_loss_condition(new_conditions)
            old_stop_loss_condition = self.get_stop_loss_condition()
            old_stop_loss_condition.on_condition_changed(new_stop_loss_condition)
            
            old_conditions_without_indicators = [condition for condition in self.conditions if not isinstance(condition, IndicatorCondition)]
            new_indicators = [condition for condition in new_conditions if isinstance(condition, IndicatorCondition)]
            self.conditions.clear()
            self.conditions.extend(old_conditions_without_indicators)
            self.conditions.extend(new_indicators)
    
    def get_extra_orders_signal(self, row):
        return self.get_first_signal_of_type(ExtraOrdersCondition, row)
            
    def get_take_profit_signal(self, row):
        return self.get_first_signal_of_type(TakeProfitCondition, row)
            
    def get_stop_loss_signal(self, row):
        return self.get_first_signal_of_type(StopLossCondition, row)
    
        
    def get_first_signal_of_type(self, condition_type, row):
        condition = self.get_first_condition_of_type(condition_type)
        if(condition):
            signal = condition.get_signal(row)
            return signal
        return None

    
     
    def get_extra_orders_condition(self, conditions = None) -> Union['ExtraOrdersCondition', None]:
        return self.get_first_condition_of_type(ExtraOrdersCondition, conditions)
            
    def get_take_profit_condition(self, conditions = None) -> Union['TakeProfitCondition', None]:
        return self.get_first_condition_of_type(TakeProfitCondition, conditions)
            
    def get_stop_loss_condition(self, conditions = None) -> Union['StopLossCondition', None]:
        return self.get_first_condition_of_type(StopLossCondition, conditions)
    
    def get_first_condition_of_type(self, condition_type: Type['TradingCondition'], conditions = None) -> Union['TradingCondition', None]:
        if(not conditions):
            conditions = self.conditions
        for condition in conditions:
            if isinstance(condition, condition_type):
                return condition
        return None
    
    
    
    def get_all_conditions_of_type(self, condition_type: Type['TradingCondition']) -> List['TradingCondition']:
        return [condition for condition in self.conditions if isinstance(condition, condition_type)]

    def all_indicators_equal_action(self, row, action) -> bool:
        indicator_conditions = self.get_all_conditions_of_type(IndicatorCondition)
        if (action == ACTION_SELL):
            indicator_conditions = [indicator for indicator in indicator_conditions if indicator.use_to_close]
            
        if not indicator_conditions:
            False
            
        for condition in indicator_conditions:
            signal = condition.get_signal(row)
            if signal is None or signal.action != action:
                return False
        return True

