from abc import ABC, abstractmethod

from trading_clients.trading_client import TradingClient

class FakeTradingClient(TradingClient):
    def __init__(self, initial_balance=10000.0):
        self.balances = {'USDT': initial_balance}
        self.orders = []

    def create_market_order(self, side, symbol, quantity, quoteOrderQty=None):
        if side == 'BUY':
            cost = quantity * quoteOrderQty if quoteOrderQty else quantity
            if cost > self.balances['USDT']:
                raise ValueError("Insufficient balance to place the order.")
            self.balances['USDT'] -= cost
        elif side == 'SELL':
            # Assuming no short selling for simplicity
            raise ValueError("Cannot place a sell market order in this simulator.")
        else:
            raise ValueError("Invalid order side. Use 'BUY' or 'SELL'.")
        self.orders.append({'side': side, 'symbol': symbol, 'quantity': quantity, 'type': 'MARKET'})
        print(f"Placed market {side} order for {quantity} {symbol}.")

    def create_limit_order(self, side, symbol, quantity, price, quoteOrderQty=None):
        if side == 'BUY':
            cost = quantity * price
            if cost > self.balances['USDT']:
                raise ValueError("Insufficient balance to place the order.")
            self.balances['USDT'] -= cost
        elif side == 'SELL':
            # Assuming no short selling for simplicity
            raise ValueError("Cannot place a sell limit order in this simulator.")
        else:
            raise ValueError("Invalid order side. Use 'BUY' or 'SELL'.")
        self.orders.append({'side': side, 'symbol': symbol, 'quantity': quantity, 'price': price, 'type': 'LIMIT'})
        print(f"Placed limit {side} order for {quantity} {symbol} at {price}.")

    def get_asset_balance(self, asset):
        if asset not in self.balances:
            raise ValueError(f"Unknown asset symbol: {asset}")
        return self.balances[asset]

    def get_symbol_info(self, symbol):
        # Simulating symbol information, you may customize this based on your needs
        return {'symbol': symbol, 'baseAsset': symbol[:-4], 'quoteAsset': 'USDT', 'status': 'TRADING'}