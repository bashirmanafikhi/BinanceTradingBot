from flask import Blueprint, render_template, current_app,request
from flask_app import socketio
from binance import ThreadedWebsocketManager
from helpers.binance_websocket import get_binance_websocket_service
from trading_clients.trading_client_factory import TradingClientFactory
from trading_strategies.bollinger_rsi_strategy import BollingerRSIStrategyEdited
from trading_strategies.trading_strategy import TradingStrategy
from trading_system import TradingSystem
import math

livetest_bp = Blueprint("livetest", __name__)

@livetest_bp.route("/livetest")
def livetest():
    # binance_manager_status = "Running" if is_binance_manager_alive() else "Stopped"
    return render_template(
        "livetest/livetest.html",
        #binance_manager_status=binance_manager_status,
        socket_url=f"{current_app.config['SERVER_URL']}livetest",
    )




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


def on_kline_data_callback(trading_system, data):
    signals, total_profit, total_trades_count = trading_system.run_strategy(data)

    signals = signals.tail(100)

    # Convert data to lists
    close_x_data = signals.index.tolist()
    close_y_data = signals['close'].tolist()

    # Prepare data dictionary
    data = {
        "total_profit": float(total_profit),
        "total_trades_count": total_trades_count,
        "price_x_data": close_x_data,
        "price_y_data": close_y_data
    }

    # Check if 'BBL' and 'BBU' columns exist in the DataFrame
    if 'BBL' in signals.columns and 'BBU' in signals.columns:
        # Drop rows with NaN values in 'BBL' and 'BBU' columns
        bollinger_signals = signals[['BBL', 'BBU']].dropna()

        # Take the last 60 rows
        bollinger_signals = bollinger_signals.tail(60)

        # Extract x data
        data["bbl_bbu_x_data"] = bollinger_signals.index.tolist()

        # Extract y data for 'BBL' and 'BBU'
        data["bbl_y_data"] = bollinger_signals['BBL'].tolist()
        data["bbu_y_data"] = bollinger_signals['BBU'].tolist()

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
    bollinger_window = int(request.form.get('bollinger_window'))
    bollinger_dev = int(request.form.get('bollinger_dev'))
    rsi_window = int(request.form.get('rsi_window'))
    rsi_overbought = int(request.form.get('rsi_overbought'))
    rsi_oversold = int(request.form.get('rsi_oversold'))

    try:
        if is_binance_manager_alive():
            return "Binance WebSocket service is already running"

        binance_manager = get_new_binance_websocket_manager()

        trading_client_factory = TradingClientFactory()
        binance_client = trading_client_factory.create_binance_trading_client()
        #binance_client = trading_client_factory.create_fake_trading_client()

        strategy = BollingerRSIStrategyEdited(bollinger_window, bollinger_dev, rsi_window, rsi_overbought, rsi_oversold)

        trading_system = TradingSystem(symbol, strategy, binance_client)

        binance_manager.start()

        binance_manager.start_kline_socket(
            symbol=trading_system.symbol,
            callback=lambda data: on_kline_data_callback(trading_system, data),
        )

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


@livetest_bp.route('/set-crypto-balances', methods=['POST'])
def set_crypto_balances():
    #btc_balance = request.form.get('btcBalance')
    usdt_balance = request.form.get('UsdtBalance')
    
    if(usdt_balance is not None):
        trading_client_factory = TradingClientFactory()
        binance_client = trading_client_factory.create_binance_trading_client()
        binance_client.set_usdt_balance(usdt_balance)
        return binance_client.get_asset_balance("USDT")

    return "Balances received successfully"