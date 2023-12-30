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
        self.last_price = 1

        self.register_handlers()
        self.initialize_symbol_info(symbol)
        self.initialize_balance()

    def run_strategy(self, data):
        signals = self.strategy.execute(data)
        return signals

    def register_handlers(self):
        self.strategy.buy_command.set_handler(self.handle_buy)
        self.strategy.sell_command.set_handler(self.handle_sell)
        self.strategy.strategy_disabled_event.add_handler(self.handle_strategy_disabled)

    def handle_strategy_disabled(self):
        self.calculate_profit_loss()
        
    
    def calculate_profit_loss(self):
        initial_base_balance = Decimal(self.initial_base_balance)
        initial_quote_balance = Decimal(self.initial_quote_balance)

        final_base_balance = Decimal(self.trading_client.get_asset_balance(self.base_asset))
        final_quote_balance = Decimal(self.trading_client.get_asset_balance(self.quote_asset))

        # Calculate the changes in balances
        base_balance_change = final_base_balance - initial_base_balance
        quote_balance_change = final_quote_balance - initial_quote_balance

        # Calculate percentage changes
        base_percentage_change = (base_balance_change / initial_base_balance) * 100
        quote_percentage_change = (quote_balance_change / initial_quote_balance) * 100

        print("-------------------------------------")
        print(f"{self.base_asset} initial balance : {initial_base_balance}")
        print(f"{self.base_asset} final balance: {final_base_balance}")
        print(f"{self.base_asset} balance change: {base_balance_change}")
        print(f"{self.base_asset} percentage change: {base_percentage_change:.2f}%")
        print("-------------------------------------")
        print(f"{self.quote_asset} initial balance : {initial_quote_balance}")
        print(f"{self.quote_asset} final balance: {final_quote_balance}")
        print(f"{self.quote_asset} balance change: {quote_balance_change}")
        print(f"{self.quote_asset} percentage change: {quote_percentage_change:.2f}%")
        print("-------------------------------------")

        # Calculate the profit or loss amounts
        profit_loss_base = base_balance_change * Decimal(self.last_price)
        profit_loss_quote = quote_balance_change * 1  # Adjust this based on your quote asset pricing
        total_profit = round(profit_loss_base + profit_loss_quote, 4)
        print(f"Total Profit: {total_profit} $")



    
    def handle_buy(self, price, quantity, type):
        return self.create_order(ACTION_BUY, type, price, quantity)

    def handle_sell(self, price, quantity, type):
        return self.create_order(ACTION_SELL, type, price, quantity)

    def create_order(self, action, type, price, quantity):
        self.last_price = price

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
        self.initial_base_balance = self.trading_client.get_asset_balance(self.base_asset)
        self.initial_quote_balance = self.trading_client.get_asset_balance(self.quote_asset)
