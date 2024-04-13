import decimal
import helpers.my_logger as my_logger
import pandas as pd
from helpers.settings.constants import (
    ACTION_BUY,
    ACTION_SELL,
    ORDER_STATUS_FILLED,
    ORDER_STATUS_NEW
)
from trading_clients.trading_client import TradingClient
from trading_strategies.trading_strategy import TradingStrategy


class TradingSystem:

    def __init__(
        self,
        symbol: str,
        strategy: TradingStrategy,
        trading_client: TradingClient,
        # should be between 0 and 1
        trade_quote_percentage= 0.9,
        trade_quote_size = None
    ):
        self.strategy = strategy
        self.trading_client = trading_client
        self.trade_quote_percentage = trade_quote_percentage
        self.trade_quote_size = trade_quote_size
        self.last_action = None
        self.last_price = 0
        self.last_profit = 0
        self.last_profit_percentage = 0
        self.total_profit = 0
        self.total_profit_percentage = 0
        self.trades_count = 0
        self.last_quantity = None
        self.register_handlers()
        self.initialize_symbol_info(symbol)
        self.initialize_balance()
        self.signals = None
        self.initial_investment = None
        self.is_running = True


    def stop(self):
        self.is_running = False
        
    def process(self, data):
        if(not self.is_running):
            raise SystemError("Trading system is not running")
        
        self.signals = self.strategy.execute(data)
        return self.signals

    def register_handlers(self):
        self.strategy.buy_command.set_handler(self.handle_buy)
        self.strategy.sell_command.set_handler(self.handle_sell)
        self.strategy.trade_closed_event.add_handler(self.handle_trade_closed)

    def handle_trade_closed(self):
        self.log_trading_informations()
        
    
    def log_trading_informations(self):
        if(self.trades_count == 0):
            my_logger.info("No Trades Happened")
            return
        
        my_logger.info("")
        my_logger.info(f"Last Price: {self.last_price}")
        
        my_logger.info(f"Total Trades Count: {self.trades_count}")
        my_logger.info(f"last profit: {self.last_profit} $")
        my_logger.info(f"last profit percentage: {self.last_profit_percentage} $")
        my_logger.info(f"total profit: {self.total_profit} $")
        my_logger.info(f"total profit percentage: {self.total_profit_percentage} $")
        my_logger.info("****************************\n\n\n")

    def handle_buy(self, price, quantity, type):
        return self.create_order(ACTION_BUY, type, price, quantity)

    def handle_sell(self, price, quantity, type):
        return self.create_order(ACTION_SELL, type, price, quantity)

    def create_order(self, action, type, price, quantity):
        quantity = self.calculate_quantity(action, price, quantity)
        if(quantity == 0):
            my_logger.error("Quantity should not be zero.")

        my_logger.info(f"{action} {quantity} {self.base_asset} at {price}")

        order = self.trading_client.create_order(
            action, type, self.symbol, quantity, price
        )

        # Print order price
        order_price = self.extract_price_from_order(order)
        if order_price is not None:
            self.calculate_total_profit(action,price,quantity)
            my_logger.info(f"{action} order placed at: {order_price}")
            self.trades_count += 1
            self.log_trading_informations()
            self.initialize_balance()
            return True

        return False
    
    def calculate_total_profit(self, action, price, current_quantity):
        previous_price = self.last_price
        previous_action = self.last_action

        self.last_price = price
        self.last_action = action

        if previous_action is None or action == ACTION_BUY:
            return 0

        # Calculate costs
        previous_cost = previous_price * current_quantity
        current_cost = price * current_quantity

        # Calculate profit for last action
        self.last_profit = current_cost - previous_cost

        # Update last_profit and total_profit
        self.total_profit += self.last_profit
        
        # Calculate profit percentages
        self.last_profit_percentage = (self.last_profit / previous_cost) * 100
        self.total_profit_percentage = (self.total_profit / self.initial_investment) * 100

        
        
        
        
        
    def calculate_quantity(self, action, price, quantity_percentage):
        try:
            if (action == ACTION_SELL and self.last_quantity is not None):
                return self.last_quantity
            
            # Avoid division by zero
            if price == 0:
                raise ValueError("Price should not be zero.")
            
            # Calculate quantity using decimal arithmetic
            if(self.trade_quote_size is None):
                size = self.quote_balance * self.trade_quote_percentage
            else:
                size = self.trade_quote_size
                
            quantity = (
                size * quantity_percentage / price
            )
            
            if(self.initial_investment is None):
                self.initial_investment = size

            step_size = float(self.symbol_info["filters"][1]["stepSize"])
            round_quantity = self.round_to_nearest_multiple(quantity, step_size)
            # Round the quantity to an appropriate number of decimal places
            round_quantity = round(round_quantity, 8)
            self.last_quantity = round_quantity
            return round_quantity

        except (ValueError, decimal.InvalidOperation) as e:
            # Handle exceptions, such as invalid values or division by zero
            my_logger.info(f"Error calculating quantity: {e}")
            return None

    def round_to_nearest_multiple(self, original_number, multiple):
        # Ensure original_number is positive
        original_number = abs(original_number)
        
        # Calculate the rounded number
        rounded_number = (original_number) // multiple * multiple
        return rounded_number

    def extract_price_from_order(self, order):
        try:
            if order["status"] == ORDER_STATUS_FILLED:
                return float(order["fills"][0]["price"])
            elif order["status"] == ORDER_STATUS_NEW:
                return ORDER_STATUS_NEW
            else:
                my_logger.info(f"Order status not filled.. it's {order['status']}")
                return None
        except (KeyError, IndexError, ValueError, Exception) as e:
            #my_logger.info(f"Error extracting price from order: {e}")
            return None
        
    def initialize_symbol_info(self, symbol):
        # Extract quote and base asset names
        self.symbol_info = self.trading_client.get_symbol_info(symbol)
        self.symbol = symbol
        self.base_asset = self.symbol_info["baseAsset"]
        self.quote_asset = self.symbol_info["quoteAsset"]

    def initialize_balance(self):
        self.base_balance = self.trading_client.get_asset_balance(self.base_asset)
        self.quote_balance = self.trading_client.get_asset_balance(self.quote_asset)

        if(self.base_balance is None or self.quote_balance is None):
            raise ValueError("Couldn't initialize balance")
