import datetime
import decimal
from models.trade_history import TradeHistory
import helpers.my_logger as my_logger
import pandas as pd
from helpers.settings.constants import ACTION_BUY, ACTION_SELL, ORDER_STATUS_FILLED, ORDER_STATUS_NEW
from trading_clients.trading_client import TradingClient
from trading_strategies.trading_strategy import TradingStrategy


class TradingSystem:

    def __init__(
        self,
        base_asset: str,
        quote_asset: str,
        strategy: TradingStrategy,
        trading_client: TradingClient,
        # should be between 0 and 1
        trade_quote_size=None,
    ):
        self.strategy = strategy
        self.trading_client = trading_client
        self.trade_quote_size = trade_quote_size
        self.total_profit = 0
        self.total_profit_percentage = 0
        self.total_buy_quantity = 0
        self.register_handlers()
        self.initialize_symbol_info(base_asset, quote_asset)
        self.initialize_balance()
        self.signals = None
        self.initial_investment = None
        self.is_running = True
        self.orders_history: TradeHistory = []
        self.start_date = datetime.datetime.now()
        my_logger.info(f"Start Date: {self.start_date}")
        

    def stop(self):
        self.is_running = False

    def process(self, data):
        if not self.is_running:
            raise SystemError("Trading system is not running")

        self.signals = self.strategy.execute(data)
        return self.signals

    def register_handlers(self):
        self.strategy.buy_command.set_handler(self.handle_buy)
        self.strategy.sell_command.set_handler(self.handle_sell)

    def log_trading_informations(self):
        if not self.orders_history:
            my_logger.info("No Trades Happened")
            return

        my_logger.info("")

        my_logger.info(f"Total Trades Count: {len(self.orders_history)}")
        my_logger.info(f"last profit: {self.get_last_profit()} $")
        my_logger.info(f"last profit percentage: {self.get_last_profit_percentage()} $")
        my_logger.info(f"total profit: {self.total_profit} $")
        my_logger.info(f"total profit percentage: {self.total_profit_percentage} $")
        my_logger.info("****************************\n\n\n")

    def handle_buy(self, price, quantity, type):
        return self.create_order(ACTION_BUY, type, price, quantity)

    def handle_sell(self, price, quantity, type):
        return self.create_order(ACTION_SELL, type, price, quantity)

    def create_order(self, action, type, price, quantity):
        quantity = self.calculate_quantity(action, price, quantity)
        if quantity == 0:
            my_logger.error("Quantity should not be zero.")

        my_logger.info(f"{action} {quantity} {self.base_asset} at {price}")

        order = self.trading_client.create_order(action, type, self.symbol, quantity, price)

        # Print order price
        order_price = self.extract_price_from_order(order)
        if order_price is not None:

            if action == ACTION_BUY:
                self.total_buy_quantity += quantity
            elif action == ACTION_SELL:
                self.total_buy_quantity = 0


            last_sell_profit = self.calculate_total_profit(action, order_price)
            self.orders_history.append(TradeHistory(action, order_price, quantity, last_sell_profit))
            my_logger.info(f"{action} order placed at: {order_price}")
            self.log_trading_informations()
            self.initialize_balance()
            return True

        return False
    
    def get_last_profit(self):
        return 0
    
    def get_last_profit_percentage(self):
        return 0
    
    def calculate_total_profit(self, action, price):

        if action == ACTION_BUY or not self.orders_history:
            return None
        
        last_buy_orders = self.get_last_buy_orders()
        last_sell_profit = 0
        for order in last_buy_orders:
            profit = order.calculate_order_profit(price)
            last_sell_profit +=  profit
        
        self.total_profit += last_sell_profit
            
        self.total_profit_percentage = (self.total_profit / self.initial_investment) * 100
        return last_sell_profit


       
    def get_last_buy_orders(self):
        buy_orders = []

        for order in reversed(self.orders_history):
            if order.action == ACTION_BUY:
                buy_orders.insert(0, order)  # Insert at the beginning to maintain order
            else:
                break 

        return buy_orders

    def calculate_quantity(self, action, price, quantity_percentage):
        try:
            if action == ACTION_SELL and self.total_buy_quantity > 0:
                return self.round_quantity(self.total_buy_quantity)

            # Avoid division by zero
            if price == 0:
                raise ValueError("Price should not be zero.")

            size = self.trade_quote_size + self.total_profit

            quantity = size * quantity_percentage / price

            if self.initial_investment is None:
                self.initial_investment = size

            return self.round_quantity(quantity)

        except (ValueError, decimal.InvalidOperation) as e:
            # Handle exceptions, such as invalid values or division by zero
            my_logger.info(f"Error calculating quantity: {e}")
            return None

    def round_quantity(self, quantity):
        step_size = float(self.symbol_info["filters"][1]["stepSize"])
        round_quantity = self.round_to_nearest_multiple(quantity, step_size)
        # Round the quantity to an appropriate number of decimal places
        round_quantity = round(round_quantity, 8)
        return round_quantity
        
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
            # my_logger.info(f"Error extracting price from order: {e}")
            return None

    def initialize_symbol_info(self, base_asset, quote_asset):
        symbol = f"{base_asset}{quote_asset}"
        # Extract quote and base asset names
        self.symbol_info = self.trading_client.get_symbol_info(symbol)
        self.symbol = symbol
        self.base_asset = self.symbol_info["baseAsset"]
        self.quote_asset = self.symbol_info["quoteAsset"]

    def initialize_balance(self):
        self.base_balance = self.trading_client.get_asset_balance(self.base_asset)
        self.quote_balance = self.trading_client.get_asset_balance(self.quote_asset)

        if self.base_balance is None or self.quote_balance is None:
            raise ValueError("Couldn't initialize balance")
