from flask import copy_current_request_context
import pandas as pd
import asyncio
import threading
import asyncio
from binance import AsyncClient, BinanceSocketManager


class MyBinanceSocketManager:

    def __init__(self, api_key, api_secret, api_testnet):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_testnet = api_testnet
        self.thread = None
        self.client = None
        self.stop_event = threading.Event()

    async def start_binance_socket_manager_async(self, symbol, callback):
        try:
            self.client = await AsyncClient.create(api_key=self.api_key, api_secret=self.api_secret, testnet=self.api_testnet)
            bm = BinanceSocketManager(self.client)
            ts = bm.kline_socket(symbol)
            async with ts as tscm:
                while not self.stop_event.is_set():
                    res = await tscm.recv()
                    df = self.convert_kline_to_dataframe(res)
                    callback(df)
        except Exception as e:
            # Log the error or handle it according to your application's requirements
            print(f"An error occurred while starting Binance socket: {e}")
            raise
        finally:
            await self.client.close_connection()

    def start_kline_in_new_thread(self, symbol, callback):
        
        @copy_current_request_context
        def start_kline_socket(symbol, callback):
            asyncio.run(self.start_binance_socket_manager_async(symbol, callback))
            
        self.thread = threading.Thread(target=start_kline_socket, args=(symbol, callback))
        self.thread.start()


    def stop_kline_socket(self):
        self.stop_event.set()
        if self.client:
            asyncio.run(self.client.close_connection())  # Close the client connection
        if self.thread:
            self.thread.join()  # Wait for the thread to finish


    def convert_kline_to_dataframe(self, kline_data):
        if((kline_data is None) or ('k' not in kline_data)):
            return
        
        kline = kline_data['k']

        # Extracting data from the kline dictionary
        data = {
            "timestamp": pd.to_datetime(kline['t'], unit="ms"),
            "open": float(kline['o']),
            "high": float(kline['h']),
            "low": float(kline['l']),
            "close": float(kline['c']),
            "volume": float(kline['v']),
            "close_time": kline['T'],
            "quote_asset_volume": float(kline['q']),
            "number_of_trades": kline['n'],
            "taker_buy_base_asset_volume": float(kline['V']),
            "taker_buy_quote_asset_volume": float(kline['Q']),
            "ignore": kline['B'],
            "symbol": kline_data['s']
        }

        # Create a DataFrame
        df = pd.DataFrame([data])

        # Convert relevant columns to numeric
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])

        return df
    
    