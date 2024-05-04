from helpers.enums import SignalCategory
from models.signal import Signal
from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger


class StopLossCondition(TradingCondition):

    def __init__(
        self, stop_loss_percentage=1.0, include_extra_orders_positions=False, trailing_stop_loss=True, timeout=None
    ):
        if stop_loss_percentage <= 0 or stop_loss_percentage >= 100:
            raise ValueError("stop_loss_percentage should be between 0 and 100")

        self.stop_loss_percentage = stop_loss_percentage
        self.include_extra_orders_positions = include_extra_orders_positions
        self.trailing_stop_loss = trailing_stop_loss
        self.timeout = timeout

        self.stop_loss = None
        self.buy_signals = []

    def on_condition_changed(self, new_condition):
        if not new_condition:
            return

        self.stop_loss_percentage = new_condition.stop_loss_percentage
        self.trailing_stop_loss = new_condition.trailing_stop_loss
        self.timeout = new_condition.timeout

        self.set_stop_loss()

    def on_order_placed_successfully(self, signal):
        if signal.action == ACTION_SELL:
            self.stop_loss = None
            self.buy_signals.clear()
        if signal.action == ACTION_BUY:
            self.buy_signals.append(signal)
            self.set_stop_loss()

    def set_stop_loss(self):
        if not self.buy_signals:
            return  # No buy signals yet, cannot set stop loss

        # Calculate weighted stop loss based on all buy signals
        total_price = sum(signal.price * signal.scale for signal in self.buy_signals)
        total_scale = sum(signal.scale for signal in self.buy_signals)
        average_price = total_price / total_scale

        if(self.include_extra_orders_positions):
            self.stop_loss = self.calculate_stop_loss(average_price, self.stop_loss_percentage)
        else:
            stop_loss_percentage = self.stop_loss_percentage / total_scale
            self.stop_loss = self.calculate_stop_loss(average_price, stop_loss_percentage)

    def calculate_stop_loss(self, price, stop_loss_percentage):
        amount = price * stop_loss_percentage / 100
        return price - amount
            

    def update_trailing_stop_loss(self, new_stop_loss):
        if self.trailing_stop_loss and self.stop_loss is not None and new_stop_loss > self.stop_loss:
            self.stop_loss = new_stop_loss

    def calculate(self, data):
        return data

    def get_signal(self, row):

        if self.stop_loss is None:
            return None

        price = row["close"]

        # update trailing stop loss
        # needs to be fixed after calculating the wighted average stop loss
        # self.set_stop_loss()

        if price < self.stop_loss:
            return Signal(price, ACTION_SELL, None, SignalCategory.STOP_LOSS)

        return None
