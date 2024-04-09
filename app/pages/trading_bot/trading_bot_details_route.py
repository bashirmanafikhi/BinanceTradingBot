import time
from flask import Blueprint, copy_current_request_context, render_template, redirect, url_for, flash, current_app,request
from flask_login import current_user, login_required
from trading_clients.fake_trading_client import FakeTradingClient
from trading_system import TradingSystem
from trading_clients.binance_trading_client import BinanceTradingClient
from trading_clients.web_socket_services.my_binance_socket_manager import MyBinanceSocketManager
from current_app_manager import CurrentAppManager
from helpers.models import User, TradingBot
from pages.trading_bot.trading_bot_route import trading_bot_bp
from flask_app import socketio
from flask_socketio import SocketIO, emit

@trading_bot_bp.route("/details/<int:id>")
@login_required
def details(id):
    trading_bot = TradingBot.query.get_or_404(id)
    #start_kline_socket(trading_bot)
    
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    socket_url = f"{current_app.config['SERVER_URL']}trading_bot_details"

    return render_template(
        '/trading_bot/trading_bot_details.html', 
        trading_bot=trading_bot, 
        is_running= (trading_system is not None), 
        socket_url=socket_url)

@socketio.on("connect", namespace="/trading_bot_details")
def handle_connect():
    print(f"handle_connect livetest")

def start_kline_socket(trading_bot):
    try:
        binance_websocket_manager = CurrentAppManager.get_websocket_manager(trading_bot.id)
        if binance_websocket_manager is None:
            exchange = trading_bot.exchange
            binance_websocket_manager = MyBinanceSocketManager(exchange.api_key, exchange.api_secret, exchange.is_test)
            CurrentAppManager.set_websocket_manager(trading_bot.id, binance_websocket_manager)
            
            binance_websocket_manager.start_kline_in_new_thread(
                symbol=trading_bot.symbol,
                callback=lambda data: kline_tick(data, trading_bot.id, socketio))
            
    except Exception as e:
        # Handle the exception as per your application's requirements
        print(f"An error occurred: {e}")


@trading_bot_bp.route("/start-bot", methods=['POST'])
@login_required
def start_bot():
    id = request.form.get('id')
    trading_bot = TradingBot.query.get_or_404(id)
    
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if(trading_system is not None):
        return "Already running!"
    
    start_kline_socket(trading_bot)
    
    exchange = trading_bot.exchange
    
    #binance_client = BinanceTradingClient(exchange.api_key, exchange.api_secret, exchange.is_test)
    binance_client = FakeTradingClient()
    strategy = trading_bot.get_strategy()
    trading_system = TradingSystem(trading_bot.symbol, strategy, binance_client, trading_bot.trade_percentage, trading_bot.trade_size)
    
    CurrentAppManager.set_trading_system(trading_bot.id, trading_system)

    return "Started successfully.", 200

    
@trading_bot_bp.route("/stop-bot", methods=['POST'])
@login_required
def stop_bot():
    
    id = request.form.get('id')
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



def kline_tick(data, trading_bot_id, socketio):
    
    trading_system = CurrentAppManager.get_trading_system(trading_bot_id)
    if(trading_system is None):
        return
    
    signals = trading_system.run_strategy(data)
    
    send_chart_details(trading_bot_id, trading_system, signals, socketio)

def send_chart_details(trading_bot_id, trading_system, signals, socketio):

    plot_size = 5000
    signals = signals.tail(plot_size)
    last_signal = signals.iloc[-1]
    total_profit = trading_system.total_profit
    total_trades_count = trading_system.trades_count
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
    
    socketio.emit(f"update_data_{trading_bot_id}", data, namespace="/trading_bot_details")


# symbol_info = binance_trading_client.get_symbol_info(trading_bot.symbol)
# base_asset = symbol_info["baseAsset"]
# quote_asset = symbol_info["quoteAsset"]
# base_balance = binance_trading_client.get_asset_balance(base_asset)
# quote_balance = binance_trading_client.get_asset_balance(quote_asset)


    
