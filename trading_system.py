from decimal import Decimal
import logging
import pandas as pd
from trading_clients.trading_client import TradingClient
from trading_strategies.trading_strategy import TradingStrategy


class TradingSystem:

    def __init__(self, symbol: str, strategy: TradingStrategy, trading_client: TradingClient):
        self.strategy = strategy
        self.trading_client = trading_client

        self.initialize_symbol_info(symbol)

    def initialize_symbol_info(self, symbol):
        self.symbol = symbol
        symbol_info = self.trading_client.get_symbol_info(symbol)# Extract quote and base asset names

        self.base_asset = symbol_info['baseAsset']
        self.quote_asset = symbol_info['quoteAsset']
        


    def run_strategy(self, data, act_on_signals=False):
        signals = self.strategy.execute(data)

        if act_on_signals:
            self.act_on_signals(signals)

        return signals
    
    


    def act_on_signals(self, signals):            
        # Implement logic to act on the live signals, such as placing orders, managing positions, etc.
        # This method should be tailored to your specific trading infrastructure.

        for index, signal in signals.iterrows():
            for trade_signal in signal["trades"]:
                if(trade_signal['action'] == 'buy'):
                    self.handle_buy(signal['close'], trade_signal['quantity'])
                elif(trade_signal['action'] == 'sell'):
                    self.handle_sell(signal['close'], trade_signal['quantity'])









    def handle_buy(self, price, quantity_percentage: float):
        # Execute buy order using the trading client
        quantity = self.calculate_quantity(price, quantity_percentage)
        logging.info(f"quantity_percentage  {quantity_percentage}")
        logging.info(f"Buying {self.base_asset} for {quantity} {self.quote_asset}$ at {price}")

        # Update balance
        order = self.trading_client.buy(self.symbol, None, price, quoteOrderQty=quantity)
        logging.info(f"order bought at: {self.extract_price_from_order(order)}")

    def handle_sell(self, price, quantity_percentage: float):
        # Execute sell order using the trading client
        quantity = self.calculate_quantity(price, quantity_percentage)
        logging.info(f"quantity_percentage  {quantity_percentage}")
        logging.info(f"Selling {self.base_asset} for {quantity} {self.quote_asset}$ at {price}")

        # Update balance
        order = self.trading_client.sell(self.symbol, None, price, quoteOrderQty=quantity)
        logging.info(f"order selled at: {self.extract_price_from_order(order)}")

    def extract_price_from_order(self, order):
        if "fills" in order and order["fills"]:
            # Assuming there can be multiple fills, extracting the price from the first fill
            first_fill = order["fills"][0]
            buy_price = float(first_fill["price"])
            return buy_price
        else:
            print("No fills information found in the order.")
            return None

    def calculate_quantity(self, price, quantity_percentage):
        balance = 10
        percentage_of_balance = 0.5  # Replace this with your desired percentage
        return (percentage_of_balance * balance * quantity_percentage)

        # Get the balance from the trading client
        #balance = self.trading_client.get_balance(self.symbol)
        # Check if the balance is not None before performing multiplication
        if balance is not None:
            quantity = Decimal(percentage_of_balance * balance * quantity_percentage) / Decimal(price)
            rounded_quantity = round(quantity, 8)
            
            return rounded_quantity
        else:
            logging.info("Warning: Unable to retrieve balance. Using default quantity.")
            return 0.0  