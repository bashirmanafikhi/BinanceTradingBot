import json
import os
import pandas
import binance_helpers.binance_trading_client as binance_trading_client
from sequences.fibonacci_sequence import FibonacciSequence
from sequences.duplicated_numbers_sequence import DuplicatedNumbersSequence
from trading_strategies.martingale_strategy import MartingaleStrategy


def main():

    strategy = MartingaleStrategy()
    strategy.execute_trade()

    trading_client = binance_trading_client.get_binance_trading_client()
    
    coin = "BTC"
    pairing = "USDT"
    symbol = coin + pairing
    
    # Example usage of the methods
    print(f"{coin} : {trading_client.get_asset_balance(coin)}")
    # print(f"{pairing} : {trading_client.get_asset_balance(pairing)}")

    # buy_quantity = 0.001
    # order = trading_client.place_market_buy_order(symbol, buy_quantity)
    # print("\nMarket Buy Order..")
    # # print(pandas.DataFrame(order))

    # print(f"{coin} : {trading_client.get_asset_balance(coin)}")
    # print(f"{pairing} : {trading_client.get_asset_balance(pairing)}")

if __name__ == "__main__":
    main()




