from decimal import ROUND_HALF_UP, Decimal
import decimal
import logging
import pandas as pd
from helpers.settings.constants import (
    ACTION_BUY,
    ACTION_SELL,
    ORDER_STATUS_FILLED,
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
)
from trading_clients.trading_client import TradingClient
from trading_strategies.trading_strategy import TradingStrategy


class TradingSystem:
    DEFAULT_TRADE_QUOTE_SIZE = 10

    def __init__(
        self,
        symbol: str,
        strategy: TradingStrategy,
        trading_client: TradingClient,
        trade_quote_size=DEFAULT_TRADE_QUOTE_SIZE,
    ):
        self.strategy = strategy
        self.trading_client = trading_client
        self.trade_quote_size = trade_quote_size

        self.register_handlers()
        self.initialize_symbol_info(symbol)

    def run_strategy(self, data):
        signals = self.strategy.execute(data)
        return signals

    def register_handlers(self):
        self.strategy.buy_command.set_handler(self.handle_buy)
        self.strategy.sell_command.set_handler(self.handle_sell)

    def handle_buy(self, price, quantity, type):
        return self.create_order(ACTION_BUY, type, price, quantity)

    def handle_sell(self, price, quantity, type):
        return self.create_order(ACTION_SELL, type, price, quantity)

    def create_order(self, action, type, price, quantity):
        quantity = self.calculate_quantity(price, quantity)

        print(f"{action} {quantity} {self.base_asset} at {price}")

        order = self.trading_client.create_order(
            action, type, self.symbol, quantity, price
        )

        # Print order price
        order_price = self.extract_price_from_order(order)
        if order_price is not None:
            print(f"{action} order placed at: {order_price}")
            return True

        return False

    def calculate_quantity(self, price, quantity_percentage):
        try:
            # Convert numbers to decimal before dividing
            price_decimal = decimal.Decimal(str(price))
            quantity_percentage_decimal = decimal.Decimal(str(quantity_percentage))

            # Avoid division by zero
            if price_decimal == 0:
                raise ValueError("Price should not be zero.")

            # Calculate quantity using decimal arithmetic
            quantity = (
                self.trade_quote_size * quantity_percentage_decimal / price_decimal
            )

            # Round the quantity to an appropriate number of decimal places
            round_quantity = round(quantity, 8)
            step_size = Decimal(self.symbol_info["filters"][1]["stepSize"])
            round_quantity = self.round_to_nearest_multiple(round_quantity, step_size)
            return round_quantity

        except (ValueError, decimal.InvalidOperation) as e:
            # Handle exceptions, such as invalid values or division by zero
            print(f"Error calculating quantity: {e}")
            return None

    def round_to_nearest_multiple(self, original_number, multiple):
        rounded_number = round(Decimal(original_number) / Decimal(multiple)) * Decimal(
            multiple
        )
        return rounded_number

    def extract_price_from_order(self, order):
        if order["status"] == ORDER_STATUS_FILLED:
            return float(order["fills"][0]["price"])
        else:
            print(f"Order status not filled.. it's {order['status']}")
            return None

    def initialize_symbol_info(self, symbol):
        # Extract quote and base asset names
        self.symbol_info = self.trading_client.get_symbol_info(symbol)
        self.symbol = symbol
        self.base_asset = self.symbol_info["baseAsset"]
        self.quote_asset = self.symbol_info["quoteAsset"]

    def initialize_balance(self):
        # Get the balance from the trading client
        self.quote_balance = self.trading_client.get_asset_balance(self.quote_asset)
