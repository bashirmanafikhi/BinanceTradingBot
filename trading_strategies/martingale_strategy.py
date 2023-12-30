from helpers.sequences.duplicated_numbers_sequence import DuplicatedNumbersSequence
from helpers.sequences.sequence_strategy import SequenceStrategy
from trading_strategies.trading_strategy import TradingStrategy
import pandas as pd
import logging
from helpers.settings.constants import ACTION_BUY, ACTION_SELL, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET

class MartingaleStrategy(TradingStrategy):
    DEFAULT_TRADING_RANGE = 6

    def __init__(self, sequence_strategy = DuplicatedNumbersSequence()):
        super().__init__()
        self.sequence_strategy = sequence_strategy
        self.initialize_variables()
    
    def initialize_variables(self):
        self.total_buy_quantity = 0
        self.total_sell_quantity = 0
        self.last_action = None
        self.trading_range = None
        self.buy_limit = None
        self.sell_limit = None
        self.high_close_limit = None
        self.low_close_limit = None

    def execute(self, data):
        signals = pd.DataFrame(data[["timestamp", "close"]])
        signals["trades"] = signals.apply(self.process, axis=1)
        return signals

    def process(self, row):
        if not self.is_enabled or self.is_processing:
            return []
        
        try:
            self.enable_processing()

            price = row.close

            # First Trade
            if self.last_action is None:
                trade = self.create_trade_action(ACTION_BUY, price)
                if trade is not None:
                    self.initialize_trading_limits(price)
                return [trade]
            
            # Buy Limit
            elif self.last_action == ACTION_SELL and price > self.buy_limit:
                return [self.create_trade_action(ACTION_BUY, price)]
            
            # Sell Limit
            elif self.last_action == ACTION_BUY and price < self.sell_limit:
                return [self.create_trade_action(ACTION_SELL, price)]
            
            # Close High
            elif (self.last_action == ACTION_BUY and price > self.high_close_limit):
                return self.close_trades(ACTION_SELL, price)
            
            # Close Low
            elif (self.last_action == ACTION_SELL and price < self.low_close_limit):
                return self.close_trades(ACTION_BUY, price)


            else:
                print(f"Price: {price}")
                return []

        finally:
            self.disable_processing()
        
    def close_trades(self, first_action, price):
        trades = []
        first_quantity = self.get_closing_quantity(first_action)
        
        if first_quantity == 0:
            return trades
        
        is_succeed = self.create_order(first_action, price, first_quantity, ORDER_TYPE_LIMIT)

        if is_succeed:
            self.disable_strategy()

            trades.append({"action": first_action, "quantity": first_quantity})

            second_action = ACTION_BUY if first_action == ACTION_SELL else ACTION_SELL
            second_quantity = self.get_closing_quantity(second_action)
            if second_quantity == 0:
                return trades
            
            is_succeed = self.create_order(second_action, price, second_quantity, ORDER_TYPE_MARKET)
            if is_succeed:
                trades.append({"action": second_action, "quantity": first_quantity})

            return trades
        else:
            return trades
        
    
    def get_closing_quantity(self, action):
        return self.total_sell_quantity if action == ACTION_BUY else self.total_buy_quantity

    def create_trade_action(self, action, price):
        quantity = self.sequence_strategy.next()
        
        is_succeed = self.create_order(action, price, quantity)

        if is_succeed:
            print(f"Level: {quantity} placed")
            self.last_action = action

            if action == ACTION_BUY:
                self.total_buy_quantity += quantity
            elif action == ACTION_SELL:
                self.total_sell_quantity += quantity

            return {"action": action, "quantity": quantity}
        else:
            self.sequence_strategy.previous()
            return None


    def calculate_trading_range(self):
        return self.DEFAULT_TRADING_RANGE

    def set_sequence_strategy(self, sequence_strategy: SequenceStrategy):
        self.sequence_strategy = sequence_strategy

    def initialize_trading_limits(self, price):
        self.trading_range = self.calculate_trading_range()
        self.buy_limit = price
        self.sell_limit = price - self.trading_range
        self.high_close_limit = price + (self.trading_range * 2)
        self.low_close_limit =  price - (self.trading_range * 3)
        self.describe()

    def describe(self):
        print("====================")
        print(f"Trading Range: {self.trading_range}")
        print(f"Buy limit: {self.buy_limit}")
        print(f"Sell limit: {self.sell_limit}")
        print(f"High close limit: {self.high_close_limit}")
        print(f"Low close limit: {self.low_close_limit}")
        print("====================")
