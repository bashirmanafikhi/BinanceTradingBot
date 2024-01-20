from flask import Blueprint, render_template, current_app
from flask_app import socketio
from binance import ThreadedWebsocketManager
from helpers.binance_websocket import get_binance_websocket_service
from trading_clients.trading_client_factory import TradingClientFactory
from trading_strategies.bollinger_rsi_strategy import BollingerRSIStrategyEdited
from trading_strategies.trading_strategy import TradingStrategy
from trading_system import TradingSystem

livetest_bp = Blueprint("livetest", __name__)


@livetest_bp.route("/livetest")
def livetest():
    binance_manager_status = "Running" if is_binance_manager_alive() else "Stopped"
    return render_template(
        "livetest/livetest.html", binance_manager_status=binance_manager_status, socket_url = f"{current_app.config['SERVER_URL']}livetest"
    )


def get_current_binance_manager():
    if "binance_manager" not in current_app.extensions:
        return get_new_binance_manager()
    return current_app.extensions["binance_manager"]


def get_new_binance_manager():
    current_app.extensions["binance_manager"] = get_binance_websocket_service()
    return current_app.extensions["binance_manager"]


def create_trading_system():
    symbol = "BTCUSDT"
    trading_client_factory = TradingClientFactory()
    binance_client = trading_client_factory.create_binance_trading_client()

    strategy = BollingerRSIStrategyEdited(30, 2, 13, 70, 30)

    return TradingSystem(symbol, strategy, binance_client)


def is_binance_manager_alive():
    return get_current_binance_manager().is_alive()


@socketio.on('connect', namespace='/livetest')
def handle_connect():
    print(f"handle_connect livetest")

@socketio.on('disconnect', namespace='/livetest')
def handle_disconnect():
    print(f"handle_disconnect livetest")


def on_kline_data_callback(trading_system, data):
    signals, total_profit, total_trades_count = trading_system.run_strategy(data)

    data = {
        "total_profit": float(total_profit),
        "total_trades_count": total_trades_count,
    }
    
    socketio.emit("update_data", data, namespace="/livetest")


@livetest_bp.route("/start-binance-websocket")
def start_binance_websocket():
    try:
        if is_binance_manager_alive():
            return "Binance WebSocket service is already running"

        binance_manager = get_new_binance_manager()

        trading_system = create_trading_system()

        binance_manager.start()

        binance_manager.start_kline_socket(
            symbol=trading_system.symbol,
            callback=lambda data: on_kline_data_callback(trading_system, data),
        )

        return "Binance WebSocket service started"
    except Exception as e:
        return f"Error starting Binance WebSocket service: {str(e)}"


@livetest_bp.route("/stop-binance-websocket")
def stop_binance_websocket():
    try:
        binance_manager = get_current_binance_manager()

        if not binance_manager.is_alive():
            return "Binance WebSocket service is already stopped"

        binance_manager.stop()
        return "Binance WebSocket service stopped"
    except Exception as e:
        return f"Error stopping Binance WebSocket service: {str(e)}"
