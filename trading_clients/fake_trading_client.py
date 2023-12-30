from abc import ABC, abstractmethod
from helpers.settings.constants import ACTION_BUY, ACTION_SELL, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET
from trading_clients.trading_client import TradingClient
import time

class FakeTradingClient(TradingClient):
    COMMISSION_RATE = 0.1
    def __init__(self):
        self.balances = {'USDT': 10000}
        self.orders_history = []

    def _apply_commission(self, cost):
        commission = cost * self.COMMISSION_RATE
        return cost + commission

    def _update_balances(self, symbol_info, side, quantity, price):
        cost = quantity * price
        cost_with_commission = self._apply_commission(cost)

        if symbol_info['quoteAsset'] not in self.balances:
            self.balances[symbol_info['quoteAsset']] = 0
        if symbol_info['baseAsset'] not in self.balances:
            self.balances[symbol_info['baseAsset']] = 0

        if side == ACTION_BUY:
            if cost_with_commission > self.balances[symbol_info['quoteAsset']]:
                print("Insufficient balance to place order.")
                return False

            self.balances[symbol_info['quoteAsset']] -= cost_with_commission
            self.balances[symbol_info['baseAsset']] += quantity
        elif side == ACTION_SELL:
            if quantity > self.balances[symbol_info['baseAsset']]:
                print("Insufficient balance to place order.")
                return False

            self.balances[symbol_info['baseAsset']] -= quantity
            self.balances[symbol_info['quoteAsset']] += cost_with_commission

        return True

    def _add_to_orders_history(self, order):
        order['timestamp'] = time.time()
        self.orders_history.append(order)

    def _update_order_status(self, order, status):
        order['status'] = status

    def create_market_order(self, side, symbol, quantity, price, quoteOrderQty=None):
        if side not in [ACTION_BUY, ACTION_SELL]:
            print("Invalid side for market order.")
            return

        if quoteOrderQty is not None:
            print("quoteOrderQty parameter is only applicable for limit orders.")
            return

        symbol_info = self.get_symbol_info(symbol)
        if symbol_info is None:
            print(f"Symbol not found: {symbol}")
            return

        if not self._update_balances(symbol_info, side, quantity, price):
            return

        order = {'type': ORDER_TYPE_MARKET, 'side': side, 'symbol': symbol, 'quantity': quantity, 'price': price}
        self._update_order_status(order, 'filled')
        self._add_to_orders_history(order)
        print(f"Executed market order - {order}")

    def create_limit_order(self, side, symbol, quantity, price):
        symbol_info = self.get_symbol_info(symbol)
        if symbol_info is None:
            print(f"Symbol not found: {symbol}")
            return

        if not self._update_balances(symbol_info, side, quantity, price):
            return

        order = {'type': ORDER_TYPE_LIMIT, 'side': side, 'symbol': symbol, 'quantity': quantity, 'price': price}
        self._update_order_status(order, 'filled')
        self._add_to_orders_history(order)
        print(f"Placed limit order - {order}")

    def create_order(self, side, type, symbol, quantity, price, quoteOrderQty=None):
        if type == ORDER_TYPE_MARKET:
            self.create_market_order(side, symbol, quantity, price, quoteOrderQty)
        elif type == ORDER_TYPE_LIMIT:
            self.create_limit_order(side, symbol, quantity, price)

    def get_asset_balance(self, asset):
        return self.balances.get(asset, 0)

    def get_symbol_info(self, symbol):
        symbol_info_list = [
            {"symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT", "quoteAssetPrice": 41500},
            {"symbol": "ETHBTC", "baseAsset": "ETH", "quoteAsset": "BTC", "quoteAssetPrice": 0.05},
            # Add more symbols as needed
        ]

        for info in symbol_info_list:
            if info['symbol'] == symbol:
                return info

        print(f"Symbol not found: {symbol}")
        return None
