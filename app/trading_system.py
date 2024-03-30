from decimal import ROUND_HALF_UP, Decimal
import decimal
import helpers.my_logger as my_logger
import pandas as pd
from helpers.settings.constants import (
    ACTION_BUY,
    ACTION_SELL,
    ORDER_STATUS_FILLED,
    ORDER_STATUS_NEW,
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
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
        self.total_profit = 0
        self.max_quantity = 0
        self.max_quote_quantity = 0
        self.max_level = 0
        self.levels = []
        self.trades_count = 0
        self.last_quantity = None
        self.register_handlers()
        self.initialize_symbol_info(symbol)
        self.initialize_balance()

    def run_strategy(self, data):
        signals = self.strategy.execute(data)
        return signals, self.total_profit, self.trades_count
    
    def getTotalProfit(self):
        initial_base_balance = Decimal(self.initial_base_balance)
        initial_quote_balance = Decimal(self.initial_quote_balance)

        base_balance_change = self.final_base_balance - initial_base_balance
        quote_balance_change = self.final_quote_balance - initial_quote_balance
        
        # Calculate the profit or loss amounts
        profit_loss_base = base_balance_change * Decimal(self.last_price)
        profit_loss_quote = quote_balance_change * 1  # Adjust this based on your quote asset pricing
        total_profit = round(profit_loss_base + profit_loss_quote, 4)
        return total_profit

    def register_handlers(self):
        self.strategy.buy_command.set_handler(self.handle_buy)
        self.strategy.sell_command.set_handler(self.handle_sell)
        self.strategy.trade_closed_event.add_handler(self.handle_trade_closed)

    def handle_trade_closed(self):
        self.calculate_profit_loss()
        
    
    def calculate_profit_loss(self):
        if(self.trades_count == 0):
            my_logger.info("No Trades Happened")
            return
        
        initial_base_balance = Decimal(self.initial_base_balance)
        initial_quote_balance = Decimal(self.initial_quote_balance)

        final_base_balance = Decimal(self.trading_client.get_asset_balance(self.base_asset))
        final_quote_balance = Decimal(self.trading_client.get_asset_balance(self.quote_asset))
        
        self.final_quote_balance = final_quote_balance
        self.final_base_balance = final_base_balance

        # Calculate the changes in balances
        base_balance_change = final_base_balance - initial_base_balance
        quote_balance_change = final_quote_balance - initial_quote_balance

        my_logger.info("")
        my_logger.info(f"{self.base_asset} initial balance : {initial_base_balance}")
        my_logger.info(f"{self.base_asset} final balance: {final_base_balance}")
        my_logger.info(f"{self.base_asset} balance change: {base_balance_change}")
        my_logger.info("")
        my_logger.info(f"{self.quote_asset} initial balance : {initial_quote_balance}")
        my_logger.info(f"{self.quote_asset} final balance: {final_quote_balance}")
        my_logger.info(f"{self.quote_asset} balance change: {quote_balance_change}")
        my_logger.info("")

        my_logger.info(f"Max {self.base_asset} Quantity: {self.max_quantity}")
        my_logger.info(f"Max Quote Quantity: {self.max_quote_quantity}")
        my_logger.info(f"Max Level: {self.max_level}")
        average = sum(self.levels) / len(self.levels)
        my_logger.info(f"Levels Average:{average}")
        my_logger.info(f"Last Price: {self.last_price}")
        
        
        # Calculate the profit or loss amounts
        profit_loss_base = base_balance_change * Decimal(self.last_price)
        profit_loss_quote = quote_balance_change * 1  # Adjust this based on your quote asset pricing
        self.total_profit = round(profit_loss_base + profit_loss_quote, 4)
        
        profit_percentage = (self.total_profit / initial_quote_balance) * 100
        
        my_logger.info(f"Total Trades Count: {self.trades_count}")
        my_logger.info(f"Profit Percentage: {profit_percentage} %")
        my_logger.info(f"Total Profit: {self.total_profit} $")
        my_logger.info("****************************")



    
    def handle_buy(self, price, quantity, type):
        return self.create_order(ACTION_BUY, type, price, quantity)

    def handle_sell(self, price, quantity, type):
        return self.create_order(ACTION_SELL, type, price, quantity)

    def create_order(self, action, type, price, quantity):
        level = quantity
        quantity = self.calculate_quantity(action, price, quantity)

        my_logger.info(f"{action} {quantity} {self.base_asset} at {price}")

        order = self.trading_client.create_order(
            action, type, self.symbol, quantity, price
        )

        # Print order price
        order_price = self.extract_price_from_order(order)
        if order_price is not None:
            self.last_price = price
            self.last_action = action
            if(self.max_quantity < quantity):
                self.max_quantity = quantity
                self.max_level = level
                self.max_quote_quantity = quantity * Decimal(price)
                self.levels.append(level)
            my_logger.info(f"{action} order placed at: {order_price}")
            self.trades_count += 1
            self.calculate_profit_loss()
            return True

        return False

    def calculate_quantity(self, action, price, quantity_percentage):
        try:
            
            if (action == ACTION_SELL and self.last_quantity is not None):
                return self.last_quantity
                
                
            # Convert numbers to decimal before dividing
            price = decimal.Decimal(str(price))
            quantity_percentage = decimal.Decimal(str(quantity_percentage))

            # Avoid division by zero
            if price == 0:
                raise ValueError("Price should not be zero.")

            # Calculate quantity using decimal arithmetic
            if(self.trade_quote_size is None):
                size = Decimal(self.final_quote_balance) * Decimal(self.trade_quote_percentage)
            else:
                size = Decimal(self.trade_quote_size)
                
            quantity = (
                size * quantity_percentage / price
            )

            # Round the quantity to an appropriate number of decimal places
            round_quantity = round(quantity, 8)
            step_size = Decimal(self.symbol_info["filters"][1]["stepSize"])
            round_quantity = self.round_to_nearest_multiple(round_quantity, step_size)
            self.last_quantity = round_quantity
            return round_quantity

        except (ValueError, decimal.InvalidOperation) as e:
            # Handle exceptions, such as invalid values or division by zero
            my_logger.info(f"Error calculating quantity: {e}")
            return None

    def round_to_nearest_multiple(self, original_number, multiple):
        rounded_number = round(Decimal(original_number) / Decimal(multiple)) * Decimal(
            multiple
        )
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
        # Get the balance from the trading client
        self.initial_base_balance = self.trading_client.get_asset_balance(self.base_asset)
        self.initial_quote_balance = self.trading_client.get_asset_balance(self.quote_asset)
        
        self.final_base_balance = self.initial_base_balance
        self.final_quote_balance = self.initial_quote_balance
