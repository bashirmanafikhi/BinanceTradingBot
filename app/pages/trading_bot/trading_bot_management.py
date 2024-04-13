from io import BytesIO
from trading_system import TradingSystem
from trading_clients.binance_trading_client import BinanceTradingClient
from trading_clients.web_socket_services.my_binance_socket_manager import MyBinanceSocketManager
from current_app_manager import CurrentAppManager
from helpers.models import User, TradingBot



def start_bot(id, kline_callback):
    trading_bot = TradingBot.query.get_or_404(id)
    
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if(trading_system is not None):
        return "Already running!"
    
    start_kline_socket(trading_bot, kline_callback)
    
    exchange = trading_bot.exchange
    
    binance_client = BinanceTradingClient(exchange.api_key, exchange.api_secret, exchange.is_test)
    binance_client.COMMISSION_RATE = 0
    strategy = trading_bot.get_strategy()
    trading_system = TradingSystem(trading_bot.symbol, strategy, binance_client, trading_bot.trade_percentage, trading_bot.trade_size)
    
    CurrentAppManager.set_trading_system(trading_bot.id, trading_system)

    return "Started successfully.", 200


def stop_bot(id):
    trading_bot = TradingBot.query.get_or_404(id)
    
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if(trading_system is not None):
        CurrentAppManager.remove_trading_system(trading_bot.id)
        # do what you need with trading_system
        
    # Stop Kline Socket and it's thread
    binance_websocket_manager = CurrentAppManager.get_websocket_manager(trading_bot.id)
    if(binance_websocket_manager is not None):
        binance_websocket_manager.stop_kline_socket()
        CurrentAppManager.remove_websocket_manager(trading_bot.id)
    
    return "Stopped successfully.", 200


def start_kline_socket(trading_bot, kline_callback):
    try:
        binance_websocket_manager = CurrentAppManager.get_websocket_manager(trading_bot.id)
        if binance_websocket_manager is None:
            exchange = trading_bot.exchange
            binance_websocket_manager = MyBinanceSocketManager(exchange.api_key, exchange.api_secret, exchange.is_test)
            CurrentAppManager.set_websocket_manager(trading_bot.id, binance_websocket_manager)
            
            binance_websocket_manager.start_kline_in_new_thread(
                symbol=trading_bot.symbol,
                callback=lambda data: kline_callback(data, trading_bot.id))
            
    except Exception as e:
        CurrentAppManager.remove_websocket_manager(trading_bot.id)
        # Handle the exception as per your application's requirements
        print(f"An error occurred: {e}")


def get_chart_details(trading_system, signals, plot_size = 5000):
    if(signals is None):
        return
    
    if(plot_size is not None):
        signals = signals.tail(plot_size)
        
    last_signal = signals.iloc[-1]
    # Convert data to lists
    close_x_data = signals.index.tolist()
    close_y_data = signals['close'].tolist()
    
    # Prepare data dictionary
    data = {
        "last_price": trading_system.last_price,
        "last_action": trading_system.last_action,
        "last_signal": last_signal.to_json(),
        
        "last_profit": trading_system.last_profit,
        "last_profit_percentage": trading_system.last_profit_percentage,
        "total_profit": trading_system.total_profit,
        "total_profit_percentage": trading_system.total_profit_percentage,
        
        "total_trades_count": trading_system.trades_count,
        "price_x_data": close_x_data,
        "price_y_data": close_y_data
    }

    # Check if 'BBL' and 'BBU' columns exist in the DataFrame
    if 'BBL' in signals.columns and 'BBU' in signals.columns:
        # Drop rows with NaN values in 'BBL' and 'BBU' columns
        bollinger_signals = signals[['BBL', 'BBU']].dropna()

        # Extract x data
        data["bbl_bbu_x_data"] = bollinger_signals.index.tolist()

        # Extract y data for 'BBL' and 'BBU'
        data["bbl_y_data"] = bollinger_signals['BBL'].tolist()
        data["bbu_y_data"] = bollinger_signals['BBU'].tolist()

    # Check if 'RSI' column exist in the DataFrame
    if 'RSI' in signals.columns:
        # Replace rows with NaN values
        rsi_signals = signals[['RSI']].fillna(50)

        # Extract x and y data
        data["rsi_x_data"] = rsi_signals.index.tolist()
        data["rsi_y_data"] = rsi_signals['RSI'].tolist()

    # action signals
    
    if 'signal' in signals.columns:
        # Keep only 'close' and 'signal' columns and drop rows with NaN in 'signal'
        action_signals = signals[['close', 'signal']].dropna(subset=['signal'])

        # Filter buy and sell signals
        buy_signals = action_signals[action_signals['signal'].apply(lambda x: x.get('action', '').upper()) == 'BUY']
        sell_signals = action_signals[action_signals['signal'].apply(lambda x: x.get('action', '').upper()) == 'SELL']

        # Extract buy signal x and y data
        data["buy_signal_x_data"] = buy_signals.index.tolist()
        data["buy_signal_y_data"] = buy_signals['close'].tolist()

        # Extract sell signal x and y data
        data["sell_signal_x_data"] = sell_signals.index.tolist()
        data["sell_signal_y_data"] = sell_signals['close'].tolist()
    
    return data
  

def update_running_trading_system(trading_bot):
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if(trading_system is None):
        return
    
    trading_system.trade_quote_percentage = trading_bot.trade_percentage
    trading_system.trade_quote_size = trading_bot.trade_size
    strategy = trading_system.strategy
    strategy.conditions_manager.conditions = trading_bot.get_conditions()
    
def generate_csv(trading_system):
    if trading_system is None:
        return None

    signals = trading_system.signals

    # Keep only specific columns
    signals = signals.loc[:, ['timestamp','open','high','low','close']]

    # Create a BytesIO object to hold the CSV data in memory
    csv_buffer = BytesIO()

    # Write DataFrame to the BytesIO object as a CSV file
    signals.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  # Reset file pointer to beginning of the file

    return csv_buffer