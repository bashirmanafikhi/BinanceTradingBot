from helpers.enums import SignalCategory
from models.signal import Signal
from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger


class TakeProfitCondition(TradingCondition):

    def __init__(
        self,
        take_profit_percentage=2.0,
        include_extra_orders_positions=False,
        trailing_take_profit=False,
        trailing_take_profit_deviation_percentage=0.4,
    ):
        if take_profit_percentage <= 0 or take_profit_percentage >= 100:
            raise ValueError("take_profit_percentage should be between 0 and 100")

        if trailing_take_profit_deviation_percentage <= 0 or trailing_take_profit_deviation_percentage >= 100:
            raise ValueError("trailing_take_profit_deviation_percentage should be between 0 and 100")

        super().__init__()

        self.take_profit_percentage = take_profit_percentage
        self.include_extra_orders_positions = include_extra_orders_positions
        self.trailing_take_profit = trailing_take_profit
        self.trailing_take_profit_deviation_percentage = trailing_take_profit_deviation_percentage

        self.take_profit = None
        self.buy_signals = []

    def on_condition_changed(self, new_condition):
        if not new_condition:
            return

        self.take_profit_percentage = new_condition.take_profit_percentage
        self.trailing_take_profit = new_condition.trailing_take_profit
        self.trailing_take_profit_deviation_percentage = new_condition.trailing_take_profit_deviation_percentage

        self.set_take_profit()

    def on_order_placed_successfully(self, signal):
        if signal.action == ACTION_SELL:
            self.take_profit = None
            self.buy_signals.clear()
        if signal.action == ACTION_BUY:
            self.buy_signals.append(signal)
            self.set_take_profit()

    def set_take_profit(self):
        if not self.buy_signals:
            return  # No buy signals yet, cannot set take-profit

        # Calculate weighted average price based on all buy signals
        total_price = sum(signal.price * signal.scale for signal in self.buy_signals)
        total_scale = sum(signal.scale for signal in self.buy_signals)
        average_price = total_price / total_scale

        if(self.include_extra_orders_positions):
            self.take_profit = self.calculate_take_profit(average_price, self.take_profit_percentage)
        else:
            take_profit_percentage = self.take_profit_percentage / total_scale
            self.take_profit = self.calculate_take_profit(average_price, take_profit_percentage)

    def calculate_take_profit(self, price, take_profit_percentage):
        amount = price * take_profit_percentage / 100
        return price + amount

    def calculate(self, data):
        return data

    def get_signal(self, row):

        if self.take_profit is None:
            return None

        price = row["close"]

        if price > self.take_profit:
            return Signal(price, ACTION_SELL, None, SignalCategory.TAKE_PROFIT)

        return None
