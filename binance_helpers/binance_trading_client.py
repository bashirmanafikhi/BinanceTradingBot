from binance.client import Client
import pandas as pd
import os
import json

import_path = "settings.json"
def get_binance_trading_client(json_file_path = import_path):
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            project_settings = json.load(file)

        binance_settings = project_settings.get("Binance", {})
        api_key = binance_settings.get("API_Key")
        api_secret = binance_settings.get("API_Secret")
        api_testnet = binance_settings.get("API_Testnet", True)

        return BinanceTradingClient(api_key, api_secret, api_testnet)
    else:
        raise FileNotFoundError(f"Settings file not found at: {json_file_path}")
    
    
class BinanceTradingClient:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)

    def get_account_info(self):
        return self.client.get_account()

    def get_asset_balances(self):
        account_info = self.get_account_info()
        balances = account_info["balances"]
        return balances

    def get_asset_balance(self, asset):
        try:
            account_info = self.get_account_info()
            balances = account_info["balances"]

            for balance in balances:
                if balance["asset"] == asset:
                    return float(balance["free"])

            # If the asset is not found in the balances
            return 0.0

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def place_market_buy_order(self, symbol, quantity):
        return self.place_market_order("BUY", symbol, quantity)

    def place_market_sell_order(self, symbol, quantity):
        return self.place_market_order("SELL", symbol, quantity)

    def place_market_order(self, side, symbol, quantity):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def fetch_historical_data(self, symbol, timeframe, limit=100):
        klines = self.client.get_klines(symbol=symbol, interval=timeframe, limit=limit)
        df = pd.DataFrame(
            klines,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df

    def list_open_trades(self):
        try:
            open_orders = self.client.get_open_orders()

            if not open_orders:
                print("No open trades.")
                return

            print("Open Trades:")
            for order in open_orders:
                print(f"Symbol: {order['symbol']}")
                print(f"Order ID: {order['orderId']}")
                print(f"Side: {order['side']}")
                print(f"Type: {order['type']}")
                print(f"Price: {order['price']}")
                print(f"Quantity: {order['origQty']}")
                print(f"Time: {order['time']}")
                print("\n---\n")

        except Exception as e:
            print(f"An error occurred: {e}")

    def query_quote_asset_list(self, quote_asset_symbol):
        symbol_dictionary = self.client.get_exchange_info()
        symbol_dataframe = pd.DataFrame(symbol_dictionary["symbols"])
        quote_symbol_dataframe = symbol_dataframe.loc[
            symbol_dataframe["quoteAsset"] == quote_asset_symbol
        ]
        quote_symbol_dataframe = quote_symbol_dataframe.loc[
            quote_symbol_dataframe["status"] == "TRADING"
        ]
        return quote_symbol_dataframe


