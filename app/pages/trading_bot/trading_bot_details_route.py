from flask import Blueprint, copy_current_request_context, render_template, redirect, url_for, flash, current_app,request
from flask_login import current_user, login_required
from trading_system import TradingSystem
from trading_clients.binance_trading_client import BinanceTradingClient
from trading_clients.web_socket_services.my_binance_socket_manager import MyBinanceSocketManager
from current_app_manager import CurrentAppManager
from helpers.models import User, TradingBot
from pages.trading_bot.trading_bot_route import trading_bot_bp
from flask_app import socketio


@trading_bot_bp.route("/details/<int:id>")
@login_required
def details(id):
    trading_bot = TradingBot.query.get_or_404(id)
    start_kline_socket(trading_bot)
    
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    
    return render_template('/trading_bot/trading_bot_details.html', trading_bot=trading_bot, is_running= (trading_system is not None), socket_url = f"{current_app.config['SERVER_URL']}trading_bot_details")

def start_kline_socket(trading_bot):
    try:
        binance_websocket_manager = CurrentAppManager.get_websocket_manager(trading_bot.id)
        if binance_websocket_manager is None:
            exchange = trading_bot.exchange
            binance_websocket_manager = MyBinanceSocketManager(exchange.api_key, exchange.api_secret, exchange.is_test)
            CurrentAppManager.set_websocket_manager(trading_bot.id, binance_websocket_manager)
            
            binance_websocket_manager.start_kline_in_new_thread(
                symbol=trading_bot.symbol,
                callback=lambda data: kline_tick(data, trading_bot.id))
            
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
    
    binance_client = BinanceTradingClient(exchange.api_key, exchange.api_secret, exchange.is_test)
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



def kline_tick(data, trading_bot_id):
    
    
    trading_bot = TradingBot.query.get_or_404(trading_bot_id)
    trading_system = CurrentAppManager.get_trading_system(trading_bot_id)
    if(trading_system is None):
        return
    signals = trading_system.run_strategy(data)
    
    print(signals)

    # data = {
    #     "current_price": data['close'][0]
    # }
    # # Emit the data via socketio
    # socketio.emit("send_current_price", data, namespace="/trading_bot_details")





# symbol_info = binance_trading_client.get_symbol_info(trading_bot.symbol)
# base_asset = symbol_info["baseAsset"]
# quote_asset = symbol_info["quoteAsset"]
# base_balance = binance_trading_client.get_asset_balance(base_asset)
# quote_balance = binance_trading_client.get_asset_balance(quote_asset)


    
