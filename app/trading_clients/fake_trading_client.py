from abc import ABC, abstractmethod
import helpers.my_logger as my_logger
from helpers.settings.constants import (
    ACTION_BUY,
    ACTION_SELL,
    ORDER_STATUS_FILLED,
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
)
from trading_clients.trading_client import TradingClient
import time


class FakeTradingClient(TradingClient):
    COMMISSION_RATE = 0.1

    def __init__(self):
        self.balances = {"USDT": 200, "BTC": 0, "SOL": 0, "ETH": 0}
        self.orders_history = []
        self.total_paid_commission = 0

    def _apply_commission(self, cost):
        commission_rate = self.COMMISSION_RATE
        commission = cost * commission_rate
        self.total_paid_commission += commission
        return cost + commission

    def _update_balances(self, symbol_info, side, quantity, price):
        cost = quantity * price
        cost_with_commission = self._apply_commission(cost)

        if symbol_info["quoteAsset"] not in self.balances:
            self.balances[symbol_info["quoteAsset"]] = 0
        if symbol_info["baseAsset"] not in self.balances:
            self.balances[symbol_info["baseAsset"]] = 0

        current_quote_balance = self.balances[symbol_info["quoteAsset"]]
        current_base_balance = self.balances[symbol_info["baseAsset"]]
        
        if side == ACTION_BUY:
            if cost_with_commission > current_quote_balance:
                my_logger.info("Insufficient balance to place order.")
                my_logger.info(f"side: {side}, price: {price}, cost_with_commission: {cost_with_commission}, current_quote_balance: {current_quote_balance}, current_base_balance: {current_base_balance}")
                return False

            self.balances[symbol_info["quoteAsset"]] -= cost_with_commission
            self.balances[symbol_info["baseAsset"]] += quantity
        elif side == ACTION_SELL:
            if quantity > current_base_balance:
                my_logger.info("Insufficient balance to place order.")
                my_logger.info(f"side: {side}, price: {price}, quantity: {quantity}, current_quote_balance: {current_quote_balance}, current_base_balance: {current_base_balance}")
                return False

            self.balances[symbol_info["baseAsset"]] -= quantity
            self.balances[symbol_info["quoteAsset"]] += cost_with_commission

        return True

    def _add_to_orders_history(self, order):
        order["timestamp"] = time.time()
        self.orders_history.append(order)

    def create_market_order(self,
                            side,
                            symbol,
                            quantity,
                            price,
                            quoteOrderQty=None):
        if side not in [ACTION_BUY, ACTION_SELL]:
            my_logger.warning("Invalid side for market order.")
            return

        if quoteOrderQty is not None:
            my_logger.warning(
                "quoteOrderQty parameter is only applicable for limit orders.")
            return

        symbol_info = self.get_symbol_info(symbol)
        if symbol_info is None:
            my_logger.warning(f"Symbol not found: {symbol}")
            return

        if not self._update_balances(symbol_info, side, quantity, price):
            return

        order = {
            "type": ORDER_TYPE_MARKET,
            "side": side,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "status": ORDER_STATUS_FILLED,
            "fills": [{
                "price": price
            }],
        }

        self._add_to_orders_history(order)
        my_logger.info(f"Executed market order - {order}")
        return order

    def create_limit_order(self, side, symbol, quantity, price):
        symbol_info = self.get_symbol_info(symbol)
        if symbol_info is None:
            my_logger.info(f"Symbol not found: {symbol}")
            return

        if not self._update_balances(symbol_info, side, quantity, price):
            return

        order = {
            "type": ORDER_TYPE_LIMIT,
            "side": side,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "status": ORDER_STATUS_FILLED,
            "fills": [{
                "price": price
            }],
        }

        self._add_to_orders_history(order)
        #my_logger.info(f"Placed limit order - {order}")
        return order

    def create_order(self,
                     side,
                     type,
                     symbol,
                     quantity,
                     price,
                     quoteOrderQty=None):
        if type == ORDER_TYPE_MARKET:
            return self.create_market_order(side, symbol, quantity, price,
                                            quoteOrderQty)
        elif type == ORDER_TYPE_LIMIT:
            return self.create_limit_order(side, symbol, quantity, price)

    def get_asset_balance(self, asset):
        return self.balances.get(asset, 0)

    def get_symbol_info(self, symbol):
        symbol_info_list = [
            {
                "symbol":
                "BTCUSDT",
                "baseAsset":
                "BTC",
                "quoteAsset":
                "USDT",
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "minPrice": "0.01",
                        "maxPrice": "100000.0",
                        "tickSize": "0.01",
                    },
                    {
                        "filterType": "LOT_SIZE",
                        "minQty": "0.001",
                        "maxQty": "10000.0",
                        "stepSize": "0.00001",
                    },
                ],
            },
            {
                "symbol":
                "ETHBTC",
                "baseAsset":
                "ETH",
                "quoteAsset":
                "BTC",
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "minPrice": "0.0001",
                        "maxPrice": "100.0",
                        "tickSize": "0.0001",
                    },
                    {
                        "filterType": "LOT_SIZE",
                        "minQty": "0.00001000",
                        "maxQty": "9000.00000000",
                        "stepSize": "0.00001000",
                    },
                ],
            },
            {
                "symbol":
                "SOLUSDT",
                "baseAsset":
                "SOL",
                "quoteAsset":
                "USDT",
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "minPrice": "0.00001",
                        "maxPrice": "10000.0",
                        "tickSize": "0.0001",
                    },
                    {
                        "filterType": "LOT_SIZE",
                        "minQty": "0.00001000",
                        "maxQty": "9000.00000000",
                        "stepSize": "0.00001000",
                    },
                ],
            },
        ]

        for info in symbol_info_list:
            if info["symbol"] == symbol:
                return info

        my_logger.info(f"Symbol not found: {symbol}")
        return None
