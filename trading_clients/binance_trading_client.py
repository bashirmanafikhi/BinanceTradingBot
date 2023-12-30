from binance.client import Client
import pandas as pd
from helpers.binance_websocket import get_binance_websocket_service

from helpers.settings.settings import Settings
from trading_clients.trading_client import TradingClient


class BinanceTradingClient(TradingClient):
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
            balances = self.get_asset_balances()

            for balance in balances:
                if balance["asset"] == asset:
                    return float(balance["free"])

            # If the asset is not found in the balances
            return 0.0

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def start_kline_socket(self, symbol, callback):
        # Create an instance of BinanceWebSocketService
        binanceWebSocket = get_binance_websocket_service()
        # Start the WebSocket service
        binanceWebSocket.start()
        # Start Kline (candlestick) socket with custom message handling
        binanceWebSocket.start_kline_socket(symbol=symbol, callback=callback)
        # Keep the program running
        binanceWebSocket.join()

    def fetch_historical_data(self, symbol, timeframe, limit=1000):
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
        df["close"] = pd.to_numeric(df["close"])
        df["high"] = pd.to_numeric(df["high"])
        df["low"] = pd.to_numeric(df["low"])
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
            (symbol_dataframe["quoteAsset"] == quote_asset_symbol)
            & (symbol_dataframe["status"] == "TRADING")
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

    def print_symbol_info(self, symbol):
        # Print symbol information
        symbol_info = self.get_symbol_info(symbol)  # Extract quote and base asset names
        quote_asset = symbol_info["quoteAsset"]
        base_asset = symbol_info["baseAsset"]
        if symbol_info:
            print(f"Symbol Information for {symbol}:")
            print(symbol_info)
        else:
            print(f"Symbol {symbol} not found.")

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
            self.client.cancel_order(symbol=order["symbol"], orderId=order["orderId"])

    def create_market_order(self, side, symbol, quantity, price, quoteOrderQty=None):
        return self.create_order(
            side, self.client.ORDER_TYPE_MARKET, symbol, quantity, price, quoteOrderQty= quoteOrderQty
        )

    def create_limit_order(self, side, symbol, quantity, price):
        return self.create_order(side, self.client.ORDER_TYPE_LIMIT, symbol, quantity, price)

    def create_order(
        self, side, type, symbol, quantity, price, quoteOrderQty=None
    ):
        try:
            timeInForce = self.client.TIME_IN_FORCE_FOK
            if type == self.client.ORDER_TYPE_MARKET:
                timeInForce = None
                price = None

            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=type,
                quantity=quantity,
                price=price,
                quoteOrderQty=quoteOrderQty,
                timeInForce=timeInForce,
            )

            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def extract_price_from_order(self, order):
        if "fills" in order and order["fills"]:
            # Assuming there can be multiple fills, extracting the price from the first fill
            first_fill = order["fills"][0]
            buy_price = float(first_fill["price"])
            return buy_price
        else:
            print("No fills information found in the order.")
            return None
