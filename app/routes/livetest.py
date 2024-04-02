from flask import Blueprint, render_template, current_app,request,redirect, Response
import helpers.my_logger as my_logger
from flask_app import socketio
from binance import ThreadedWebsocketManager
from helpers.binance_websocket import get_binance_websocket_service
from trading_clients.trading_client_factory import TradingClientFactory
from trading_strategies.bollinger_rsi_strategy import BollingerRSIStrategy
from trading_strategies.trading_strategy import TradingStrategy
from trading_system import TradingSystem
import math

livetest_bp = Blueprint("livetest", __name__)

@livetest_bp.route("/livetest")
def livetest():
    binance_manager_status = "Running" if is_binance_manager_alive() else "Stopped"

    return render_template(
        "livetest/livetest.html",
        binance_manager_status=binance_manager_status,
        socket_url=f"{current_app.config['SERVER_URL']}livetest",
        strategy_details= get_strategy_details()
    )

def get_strategy_details():
    trading_system = get_current_trading_system()
    if(trading_system is None):
        return {
            "symbol":"BTCUSDT",
            "trade_percentage":0.90,
            "trade_size":None,
            "bollinger_window":750,
            "bollinger_dev":2,
            "rsi_window":250,
            "rsi_overbought":70,
            "rsi_oversold":30,
        }
    else:
        return {
            "symbol": trading_system.symbol,
            "trade_percentage":trading_system.trade_quote_percentage,
            "trade_size":trading_system.trade_quote_size,
            "bollinger_window":trading_system.strategy.bollinger_window,
            "bollinger_dev":trading_system.strategy.bollinger_dev,
            "rsi_window":trading_system.strategy.rsi_window,
            "rsi_overbought":trading_system.strategy.rsi_overbought,
            "rsi_oversold":trading_system.strategy.rsi_oversold,
        }

def get_current_binance_manager():
    if "binance_manager" not in current_app.extensions:
        return get_new_binance_websocket_manager()
    return current_app.extensions["binance_manager"]

def get_new_binance_websocket_manager():
    current_app.extensions["binance_manager"] = get_binance_websocket_service()
    return current_app.extensions["binance_manager"]

def is_binance_manager_alive():
    return get_current_binance_manager().is_alive()

@socketio.on("connect", namespace="/livetest")
def handle_connect():
    print(f"handle_connect livetest")

@socketio.on("disconnect", namespace="/livetest")
def handle_disconnect():
    print(f"handle_disconnect livetest")

def get_current_trading_system():
    if "trading_system" in current_app.extensions:
        return current_app.extensions["trading_system"]
    return None

def on_kline_data_callback(trading_system, data):
    signals, total_profit, total_trades_count = trading_system.run_strategy(data)

    plot_size = 5000
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
        "initial_base_balance": float(trading_system.initial_base_balance),
        "initial_quote_balance": float(trading_system.initial_quote_balance),
        "final_base_balance": float(trading_system.final_base_balance),
        "final_quote_balance": float(trading_system.final_quote_balance),
        "total_profit": float(total_profit),
        "total_trades_count": total_trades_count,
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


    # Emit the data via socketio
    socketio.emit("update_data", data, namespace="/livetest")

@livetest_bp.route("/start-binance-websocket", methods=['POST'])
def start_binance_websocket():
    symbol = request.form.get('symbol')
    bollinger_window = float(request.form.get('bollinger_window'))
    bollinger_dev = float(request.form.get('bollinger_dev'))
    rsi_window = float(request.form.get('rsi_window'))
    rsi_overbought = float(request.form.get('rsi_overbought'))
    rsi_oversold = float(request.form.get('rsi_oversold'))
    trade_percentage = float(request.form.get('trade_percentage'))
    trade_size = request.form.get('trade_size')
    trade_size = None if trade_size == '' else trade_size

    if is_binance_manager_alive():
            return update_strategy(bollinger_window, bollinger_dev, rsi_window, rsi_overbought, rsi_oversold, trade_percentage, trade_size)
    
    return start_strategy(bollinger_window, bollinger_dev, rsi_window, rsi_overbought, rsi_oversold, symbol, trade_percentage, trade_size)
    
def update_strategy(bollinger_window, bollinger_dev, rsi_window, rsi_overbought, rsi_oversold, trade_percentage, trade_size):    
    trading_system = get_current_trading_system()
    strategy = trading_system.strategy

    trading_system.trade_quote_percentage = trade_percentage
    trading_system.trade_quote_size = trade_size

    strategy.bollinger_window = bollinger_window
    strategy.bollinger_dev = bollinger_dev
    strategy.rsi_window = rsi_window
    strategy.rsi_overbought = rsi_overbought
    strategy.rsi_oversold = rsi_oversold

    # Redirect back to the same page
    return redirect(request.referrer)

def start_strategy(bollinger_window, bollinger_dev, rsi_window, rsi_overbought, rsi_oversold, symbol, trade_percentage, trade_size):    
    try:
        binance_manager = get_new_binance_websocket_manager()

        trading_client_factory = TradingClientFactory()
        binance_client = trading_client_factory.create_binance_trading_client()
        #binance_client = trading_client_factory.create_fake_trading_client()

        strategy = BollingerRSIStrategy(bollinger_window, bollinger_dev, rsi_window, rsi_overbought, rsi_oversold)

        trading_system = TradingSystem(symbol, strategy, binance_client, trade_percentage, trade_size)

        binance_manager.start()

        binance_manager.start_kline_socket(
            symbol=trading_system.symbol,
            callback=lambda data: on_kline_data_callback(trading_system, data),
        )

        current_app.extensions["trading_system"] = trading_system
        # Return a response message
        return "WebSocket connection started successfully.", 200

    except Exception as e:
        return f"Error starting Binance WebSocket service: {str(e)}"

@livetest_bp.route("/stop-binance-websocket", methods=['POST'])
def stop_binance_websocket():
    try:
        binance_manager = get_current_binance_manager()

        if not binance_manager.is_alive():
            return "Binance WebSocket service is already stopped"

        binance_manager.stop()
        return "Binance WebSocket service stopped"
    except Exception as e:
        return f"Error stopping Binance WebSocket service: {str(e)}"
