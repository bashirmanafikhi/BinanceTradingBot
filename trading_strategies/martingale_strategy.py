from other_services.sequences.duplicated_numbers_sequence import DuplicatedNumbersSequence
from other_services.sequences.sequence_strategy import SequenceStrategy
from trading_strategies.trading_strategy import TradingStrategy
import pandas as pd
import logging
from settings.constants import BUY_ACTION, SELL_ACTION

class MartingaleStrategy(TradingStrategy):
    DEFAULT_TRADING_RANGE = 10

    def __init__(self):
        super().__init__()
        self.initialize_variables()
    
    def initialize_variables(self):
        self.is_enabled = True
        self.sequence_strategy = DuplicatedNumbersSequence()
        self.total_buy_quantity_percentage = 0
        self.total_sell_quantity_percentage = 0
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
        if not self.is_enabled:
            return []
        
        price = row.close

        # First Trade
        if self.last_action is None:
            self.initialize_trading_limits(price)
            return [self.create_trade_action(BUY_ACTION)]
        
        # Buy Limit
        elif self.last_action == SELL_ACTION and price > self.buy_limit:
            return [self.create_trade_action(BUY_ACTION)]
        
        # Sell Limit
        elif self.last_action == BUY_ACTION and price < self.sell_limit:
            return [self.create_trade_action(SELL_ACTION)]
        
        # Close
        elif (self.last_action == BUY_ACTION and price > self.high_close_limit) or \
             (self.last_action == SELL_ACTION and price < self.low_close_limit):
            self.is_enabled = False
            logging.info("Cloooooooosed")
            return [
                self.create_trade_action(BUY_ACTION, self.total_sell_quantity_percentage),
                self.create_trade_action(SELL_ACTION, self.total_buy_quantity_percentage),
            ]
        
        else:
            logging.info(f"Price: {price}")
            return []

    def create_trade_action(self, action, quantity_percentage = None):
        if(quantity_percentage is None):
            quantity_percentage = self.sequence_strategy.next()
            
            if action == BUY_ACTION:
                self.total_buy_quantity_percentage += quantity_percentage

            elif action == SELL_ACTION:
                self.total_sell_quantity_percentage += quantity_percentage
            
        self.last_action = action

        return {"action": action, "quantity": quantity_percentage}

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
        logging.info("====================")
        logging.info(f"Trading Range: {self.trading_range}")
        logging.info(f"Buy limit: {self.buy_limit}")
        logging.info(f"Sell limit: {self.sell_limit}")
        logging.info(f"High close limit: {self.high_close_limit}")
        logging.info(f"Low close limit: {self.low_close_limit}")
        logging.info("====================")
