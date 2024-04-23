from typing import List
from helpers.enums import SignalCategory
from models.signal import Signal
from trading_conditions.trading_condition import TradingCondition
from helpers.settings.constants import ACTION_BUY, ACTION_SELL
import pandas_ta as ta
import helpers.my_logger as my_logger


class ExtraOrdersCondition(TradingCondition):

    def __init__(
        self,
        extra_orders_count,
        extra_order_first_volume_scale=1,
        extra_order_first_deviation_percentage=1,
        extra_order_step_volume_scale=1,
        extra_order_step_deviation_scale=1,
    ):

        if extra_orders_count <= 0:
            raise ValueError("extra_orders_count must be bigger than thero")

        if extra_order_first_deviation_percentage <= 0 or extra_order_first_deviation_percentage >= 100:
            raise ValueError("extra_order_first_deviation_percentage should be between 0 and 100")

        self.extra_orders_count = extra_orders_count
        self.extra_order_first_volume_scale = extra_order_first_volume_scale
        self.extra_order_first_deviation_percentage = extra_order_first_deviation_percentage
        self.extra_order_step_volume_scale = extra_order_step_volume_scale
        self.extra_order_step_deviation_scale = extra_order_step_deviation_scale

        self.extra_orders: List[ExtraOrderDto] = []
        self.done_orders_count = 0

    def on_order_placed_successfully(self, signal):
        if signal.action == ACTION_SELL:
            self.extra_orders.clear()
            self.done_orders_count = 0
        if signal.action == ACTION_BUY:
            self.check_extra_orders(signal.price)

    def check_extra_orders(self, price):
        if self.extra_orders:
            self.done_orders_count += 1
            my_logger.info(f"Extra order triggered: {self.done_orders_count}")
        else:
            self.calculate_extra_orders(price)
            for order in self.extra_orders:
                my_logger.info(
                    f"set extra order: volume:{order.volume_scale}, deviation_percentage:{order.deviation_percentage}, deviation:{order.deviation} "
                )

    def calculate_extra_orders(self, price):
        first_order_volume_scale = self.extra_order_first_volume_scale
        first_order_deviation_percentage = self.extra_order_first_deviation_percentage
        first_order_deviation = price - (price * first_order_deviation_percentage / 100)
        first_order = ExtraOrderDto(first_order_volume_scale, first_order_deviation, first_order_deviation_percentage)
        self.extra_orders.append(first_order)

        for i in range(self.extra_orders_count - 1):
            last_order = self.extra_orders[-1]
            new_order_volume_scale = last_order.volume_scale * self.extra_order_step_volume_scale
            new_order_deviation_percentage = last_order.deviation_percentage * self.extra_order_step_deviation_scale
            new_order_deviation = last_order.deviation - (last_order.deviation * new_order_deviation_percentage / 100)
            new_order = ExtraOrderDto(new_order_volume_scale, new_order_deviation, new_order_deviation_percentage)
            self.extra_orders.append(new_order)

    def calculate(self, data):
        return data

    def get_signal(self, row):

        if not self.extra_orders:
            return None

        price = row["close"]

        if self.extra_orders_count > self.done_orders_count:
            extra_order = self.extra_orders[self.done_orders_count]
            if price < extra_order.deviation:
                return Signal(price, ACTION_BUY, extra_order.volume_scale, SignalCategory.EXTRA_ORDER)

        return None


class ExtraOrderDto:
    def __init__(self, volume_scale, deviation, deviation_percentage):
        self.volume_scale = volume_scale
        self.deviation = deviation
        self.deviation_percentage = deviation_percentage
