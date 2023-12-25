import binance_helpers.binance_trading_client as binance_trading_client
from sequences.fibonacci_sequence import FibonacciSequence
from sequences.duplicated_numbers_sequence import DuplicatedNumbersSequence
from trading_strategies.martingale_strategy import MartingaleStrategy


def main():

    symbol = "BTCUSDT"
    baseCapital = 1000
    strategy = MartingaleStrategy(baseCapital, symbol)

    
    

if __name__ == "__main__":
    main()




