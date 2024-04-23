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

    
     
    def get_extra_orders_condition(self) -> Union['ExtraOrdersCondition', None]:
        return self.get_first_condition_of_type(ExtraOrdersCondition)
            
    def get_take_profit_condition(self) -> Union['TakeProfitCondition', None]:
        return self.get_first_condition_of_type(TakeProfitCondition)
            
    def get_stop_loss_condition(self) -> Union['StopLossCondition', None]:
        return self.get_first_condition_of_type(StopLossCondition)
    
    def get_first_condition_of_type(self, condition_type: Type['TradingCondition']) -> Union['TradingCondition', None]:
        for condition in self.conditions:
            if isinstance(condition, condition_type):
                return condition
        return None
    
    
    
    def get_all_conditions_of_type(self, condition_type: Type['TradingCondition']) -> List['TradingCondition']:
        return [condition for condition in self.conditions if isinstance(condition, condition_type)]

    def all_indicators_equal_action(self, row, action) -> bool:
        indicator_conditions = self.get_all_conditions_of_type(IndicatorCondition)
        
        if not indicator_conditions:
            False
            
        for condition in indicator_conditions:
            signal = condition.get_signal(row)
            if signal is None or signal.action != action:
                return False
        return True

