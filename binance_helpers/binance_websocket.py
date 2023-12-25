import time
import pandas as pd
from binance import ThreadedWebsocketManager

# Binance API credentials
api_key = 'NeDpxoFbgMoyHXgaroOrdRr0uYT5w95thwPnaHMzI7LsQb7skKGpKwDa8MKGaVss'
api_secret = 'IZBHsoI1WqGV6zZ7NiOFlqkBAmamLYmiX4mcPXvki10cQC3yvCxf1pe6ZincRpNM'
symbol = 'BTCUSDT'
testnet=True
def handle_socket_message(msg):
    print(f"Message type: {msg['e']}")
    dataframe = pd.DataFrame(msg)
    print(dataframe)

def main():
    #symbol = 'bnbbtc'

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)

    # Start the ThreadedWebsocketManager
    twm.start()

    # Start Kline (candlestick) socket
    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # Start Depth (order book) socket
    twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # Or start a multiplex socket with multiple streams
    # Streams: ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
    streams = [f'{symbol}@miniTicker', f'{symbol}@bookTicker']
    twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    # Keep the program running
    twm.join()

if __name__ == "__main__":
    main()