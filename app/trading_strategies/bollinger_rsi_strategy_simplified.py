import pandas_ta as ta
from trading_conditions.bollinger_bands_condition import BollingerBandsCondition
from trading_conditions.rsi_condition import RSICondition
from trading_strategies.conditions_strategy import ConditionsStrategy
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
from trading_strategies.trading_strategy import TradingStrategy
import helpers.my_logger as my_logger

class BollingerRSIStrategySimplified(ConditionsStrategy):
    
    def __init__(self, bollinger_window=20, bollinger_dev=2, rsi_window=14, rsi_overbought=70, rsi_oversold=30):

        self.bollinger_condition = BollingerBandsCondition(bollinger_window, bollinger_dev)
        self.rsi_condition = RSICondition(rsi_window, rsi_overbought, rsi_oversold)
        conditions_list = [self.bollinger_condition, self.rsi_condition]
        super().__init__(conditions_list)

    def process_all(self, data):
        return  super().process_all(data)

    def process_row(self, row):
        return  super().process_row(row)