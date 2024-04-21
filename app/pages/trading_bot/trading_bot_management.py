from io import BytesIO
from trading_system import TradingSystem
from trading_clients.binance_trading_client import BinanceTradingClient
from trading_clients.web_socket_services.my_binance_socket_manager import MyBinanceSocketManager
from current_app_manager import CurrentAppManager
from models.database_models import User, TradingBot



def start_bot(id, kline_callback):
    trading_bot = TradingBot.query.get_or_404(id)
    
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if(trading_system is not None and trading_system.is_running):
        return "Already running!"
    
    start_kline_socket(trading_bot, kline_callback)
    
    exchange = trading_bot.exchange
    
    binance_client = BinanceTradingClient(exchange.api_key, exchange.api_secret, exchange.is_test)
    strategy = trading_bot.get_strategy()
    trading_system = TradingSystem(trading_bot.base_asset, trading_bot.quote_asset, strategy, binance_client, trading_bot.trade_size)
    
    CurrentAppManager.set_trading_system(trading_bot.id, trading_system)

    return "Started successfully."


def stop_bot(id):
    trading_bot = TradingBot.query.get_or_404(id)
    
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if(trading_system is not None):
        trading_system.stop()
        
    # Stop Kline Socket and it's thread
    binance_websocket_manager = CurrentAppManager.get_websocket_manager(trading_bot.id)
    if(binance_websocket_manager is not None):
        binance_websocket_manager.stop_kline_socket()
        CurrentAppManager.remove_websocket_manager(trading_bot.id)
    
    return "Stopped successfully."


def start_kline_socket(trading_bot, kline_callback):
    try:
        binance_websocket_manager = CurrentAppManager.get_websocket_manager(trading_bot.id)
        if binance_websocket_manager is None:
            exchange = trading_bot.exchange
            binance_websocket_manager = MyBinanceSocketManager(exchange.api_key, exchange.api_secret, exchange.is_test)
            CurrentAppManager.set_websocket_manager(trading_bot.id, binance_websocket_manager)
            
            binance_websocket_manager.start_kline_in_new_thread(
                symbol=trading_bot.get_symbol(),
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
        "last_action_price": None,
        "last_action": None,
        "last_signal": last_signal.to_json(),
        
        "last_profit": trading_system.get_last_profit(),
        "last_profit_percentage": trading_system.get_last_profit_percentage(),
        "total_profit": trading_system.total_profit,
        "total_profit_percentage": trading_system.total_profit_percentage,
        
        "total_trades_count": len(trading_system.orders_history),
        "price_x_data": close_x_data,
        "price_y_data": close_y_data
    }

    # Check if any columns contain 'BBL' and 'BBU' in their names
    bbl_columns = [col for col in signals.columns if 'BBL' in col]
    bbu_columns = [col for col in signals.columns if 'BBU' in col]

    if bbl_columns and bbu_columns:
        # Take the first column found containing 'BBL' and 'BBU'
        bbl_column = bbl_columns[0]
        bbu_column = bbu_columns[0]

        # Drop rows with NaN values in 'BBL' and 'BBU' columns
        bollinger_signals = signals[[bbl_column, bbu_column]].dropna()

        # Extract x data
        data["bbl_bbu_x_data"] = bollinger_signals.index.tolist()

        # Extract y data for 'BBL' and 'BBU'
        data["bbl_y_data"] = bollinger_signals[bbl_column].tolist()
        data["bbu_y_data"] = bollinger_signals[bbu_column].tolist()

    # Check if any column contains 'rsi' in its name
    rsi_columns = [col for col in signals.columns if 'RSI' in col]

    if rsi_columns:
        # Take the first column found containing 'rsi'
        rsi_column = rsi_columns[0]

        # Replace rows with NaN values
        rsi_signals = signals[[rsi_column]].fillna(50)

        # Extract x and y data
        data["rsi_x_data"] = rsi_signals.index.tolist()
        data["rsi_y_data"] = rsi_signals[rsi_column].tolist()

    # action signals
    
    if 'signal' in signals.columns:
        # Keep only 'close' and 'signal' columns and drop rows with NaN in 'signal'
        action_signals = signals[['close', 'signal']].dropna(subset=['signal'])

        # Filter buy and sell signals
        buy_signals = action_signals[action_signals['signal'].apply(lambda x: x.action) == 'BUY']
        sell_signals = action_signals[action_signals['signal'].apply(lambda x: x.action) == 'SELL']

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
    
    trading_system.trade_quote_size = trading_bot.trade_size
    strategy = trading_system.strategy
    strategy.conditions_manager.conditions = trading_bot.get_start_conditions()
    
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