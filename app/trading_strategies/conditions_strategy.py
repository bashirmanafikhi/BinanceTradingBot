import pandas_ta as ta
from helpers.enums import SignalCategory
from models.signal import Signal
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

        # Get signals for various conditions
        signals = [
            self.conditions_manager.get_extra_orders_signal(row),
            self.conditions_manager.get_take_profit_signal(row),
            self.conditions_manager.get_stop_loss_signal(row),
        ]

        # Filter out None signals
        valid_signals = [signal for signal in signals if signal is not None]

        # Process valid signals
        for signal in valid_signals:
            return self.create_and_notify_trade_signal(signal)

        # Handle Indicator signals
        if self.can_buy() and self.conditions_manager.all_indicators_equal_action(row, ACTION_BUY):
            return self.create_and_notify_trade_signal(Signal(price, ACTION_BUY, 1, SignalCategory.INDICATOR_SIGNAL))

        elif self.can_sell() and self.conditions_manager.all_indicators_equal_action(row, ACTION_SELL):
            return self.create_and_notify_trade_signal(Signal(price, ACTION_SELL, 1, SignalCategory.INDICATOR_SIGNAL))

        return None

    def create_and_notify_trade_signal(self, input_signal):
        trade_signal = self.create_trade_action(input_signal)
        if trade_signal:
            self.conditions_manager.on_order_placed_successfully(trade_signal)
        return trade_signal
