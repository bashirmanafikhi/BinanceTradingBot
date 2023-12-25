from sequences.duplicated_numbers_sequence import DuplicatedNumbersSequence
from .trading_strategy import TradingStrategy
from typing import Type
from sequences.sequence_strategy import SequenceStrategy

class MartingaleStrategy(TradingStrategy):
    def __init__(self):
        self.sequence_strategy = DuplicatedNumbersSequence()

    def set_sequence_strategy(self, sequence_strategy: Type[SequenceStrategy]):
        self.sequence_strategy = sequence_strategy

    def execute_trade(self):
        # Martingale-specific logic goes here
        print("Applying Martingale strategy...")
        sequence = self.sequence_strategy.generate_sequence(10)
        # Simulate trading logic using the generated sequence
        print(f"Executing trade with sequence: {sequence}")
