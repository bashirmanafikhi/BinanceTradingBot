import logging
import matplotlib.pyplot as plt
import mplfinance as mpf
from binance.client import Client
from datetime import datetime
import pandas as pd
import logging

class RealTimeCandlestickChart:
    def __init__(self):
        self.kline_data = []

    def handle_depth_message(self, msg):
        # وقت تشتري طلع على هاد
        # Ask Price: The lowest price a seller is willing to accept for a security. If you want to buy an asset immediately, you could place a market buy order at the ask price.
        ask_price = float(msg['a'][0][0])  # Lowest ask price
        logging.info(f"Ask Price: {ask_price}")

        # وقت بدك تبيع طلع على هاد
        # Bid Price: The highest price a buyer is willing to pay for a security. If you want to sell an asset immediately, you could place a market sell order at the bid price.
        bid_price = float(msg['b'][0][0])  # Highest bid price
        logging.info(f"Bid Price: {bid_price}")

    def print_price_from_kline_message(self, msg):
        logging.info(f"Symbol: {msg['s']}, Price: {msg['c']}")

    def custom_handle_kline_message(self, msg):
        kline = msg['k']

        # Extract relevant information from the Binance Kline WebSocket response
        timestamp = kline['t']
        open_price = float(kline['o'])
        high_price = float(kline['h'])
        low_price = float(kline['l'])
        close_price = float(kline['c'])
        volume = float(kline['v']) 
        kline_time = datetime.utcfromtimestamp(timestamp / 1000.0)

        # Append the new candlestick data to the list
        self.kline_data.append([kline_time, open_price, high_price, low_price, close_price, volume])

        # Update the candlestick chart
        self.update_chart()

    def update_chart(self):
        # Create a DataFrame from the kline_data list
        df = self.create_dataframe()

        # Plot the candlestick chart using mplfinance
        mpf.plot(df, type='candle', style='charles',
                 title=f'Candlestick Chart',
                 ylabel='Price ($)',
                 volume=True,
                 mav=(3, 6, 9))

        # Display the updated chart
        plt.show()

    def create_dataframe(self):
        # Create a DataFrame from the kline_data list
        df = pd.DataFrame(self.kline_data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        return df