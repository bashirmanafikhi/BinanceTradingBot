from binance.client import Client
import pandas as pd
import os

from settings.settings import Settings

def get_binance_trading_client():
    settings = Settings()

    api_key = settings.binance.api_key
    api_secret = settings.binance.api_secret
    api_testnet = settings.binance.api_testnet

    return BinanceTradingClient(api_key, api_secret, api_testnet)
    

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

    def place_market_buy_order(self, symbol, quantity, quantity_type='quote'):
        return self.place_market_order("BUY", symbol, quantity, quantity_type)

    def place_market_sell_order(self, symbol, quantity, quantity_type='quote'):
        return self.place_market_order("SELL", symbol, quantity, quantity_type)

    def place_market_order(self, side, symbol, quantity, quantity_type='quote'):
        try:
            if quantity_type == 'quote':
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quoteOrderQty=quantity
                )
            else:
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
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore",
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
                self.print_order_details(order)

        except Exception as e:
            print(f"An error occurred: {e}")

    def query_quote_asset_list(self, quote_asset_symbol):
        symbol_dictionary = self.client.get_exchange_info()
        symbol_dataframe = pd.DataFrame(symbol_dictionary["symbols"])
        quote_symbol_dataframe = symbol_dataframe.loc[
            (symbol_dataframe["quoteAsset"] == quote_asset_symbol) &
            (symbol_dataframe["status"] == "TRADING")
        ]
        return quote_symbol_dataframe

    def print_order_details(self, order):
        print(f"Symbol: {order['symbol']}")
        print(f"Order ID: {order['orderId']}")
        print(f"Side: {order['side']}")
        print(f"Type: {order['type']}")
        print(f"Price: {order['price']}")
        print(f"Quantity: {order['origQty']}")
        print(f"Time: {order['time']}")
        print("\n---\n")

    def get_symbol_info(self, symbol):
        return self.client.get_symbol_info(symbol)

    def get_trade_fee(self, symbol=None):
        if symbol:
            return self.client.get_trade_fee(symbol=symbol)
        else:
            return self.client.get_trade_fee()

    def get_order_book(self, symbol, limit=5):
        return self.client.get_order_book(symbol=symbol, limit=limit)

    def get_recent_trades(self, symbol, limit=5):
        return self.client.get_recent_trades(symbol=symbol, limit=limit)
    
    def get_symbol_ticker(self, symbol):
        return self.client.get_symbol_ticker(symbol=symbol)

    def get_all_tickers(self):
        return self.client.get_all_tickers()

    def get_open_positions(self):
        return self.client.get_margin_account()["userAssets"]

    def get_order_status(self, symbol, order_id):
        return self.client.get_order(symbol=symbol, orderId=order_id)

    def cancel_order(self, symbol, order_id):
        return self.client.cancel_order(symbol=symbol, orderId=order_id)

    def cancel_all_open_orders(self, symbol=None):
        if symbol:
            open_orders = self.client.get_open_orders(symbol=symbol)
        else:
            open_orders = self.client.get_open_orders()

        for order in open_orders:
            self.client.cancel_order(symbol=order['symbol'], orderId=order['orderId'])

    def place_limit_order(self, side, symbol, quantity, price):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=price
            )
            return order
        except Exception as e:
            print(f"Error placing limit order: {e}")
            return None

    def place_stop_loss_order(self, symbol, quantity, stop_price, activation_price):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side='SELL',
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_price,
                activationPrice=activation_price
            )
            return order
        except Exception as e:
            print(f"Error placing stop-loss order: {e}")
            return None
