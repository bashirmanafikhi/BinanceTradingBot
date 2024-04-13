import csv
from io import BytesIO, StringIO
import os
import time
from flask import Blueprint, copy_current_request_context, render_template, redirect, send_file, url_for, flash, current_app,request
from flask_login import current_user, login_required
import pandas as pd
from trading_clients.fake_trading_client import FakeTradingClient
from trading_system import TradingSystem
from trading_clients.binance_trading_client import BinanceTradingClient
from trading_clients.web_socket_services.my_binance_socket_manager import MyBinanceSocketManager
from current_app_manager import CurrentAppManager
from helpers.models import User, TradingBot
from pages.trading_bot.trading_bot_route import trading_bot_bp
import pages.trading_bot.trading_bot_management as bot_management
from flask_app import socketio

@trading_bot_bp.route("/details/<int:id>")
@login_required
def details(id):
    trading_bot = TradingBot.query.get_or_404(id)
    #start_kline_socket(trading_bot)
    
    socket_url = f"{current_app.config['SERVER_URL']}trading_bot_details"
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)

    return render_template(
        '/trading_bot/trading_bot_details.html', 
        trading_bot=trading_bot, 
        is_running= (trading_system is not None), 
        socket_url=socket_url)


@trading_bot_bp.route('/download_csv/<int:id>')
def download_csv(id):
    trading_bot = TradingBot.query.get_or_404(id)
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    csv_buffer = bot_management.generate_csv(trading_system)

    if csv_buffer is None:
        return "No data to download"

    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{trading_bot.symbol}.csv'
    )


@socketio.on("connect", namespace="/trading_bot_details")
def handle_connect():
    print(f"handle_connect livetest")


@trading_bot_bp.route("/start-bot", methods=['POST'])
@login_required
def start_bot():
    id = request.form.get('id')
    return bot_management.start_bot(id, kline_tick)

    
@trading_bot_bp.route("/stop-bot", methods=['POST'])
@login_required
def stop_bot():
    id = request.form.get('id')
    return bot_management.stop_bot(id)


def kline_tick(data, trading_bot_id):
    trading_system = CurrentAppManager.get_trading_system(trading_bot_id)
    if(trading_system is None):
        return
    
    signals = trading_system.run_strategy(data)
    
    data = bot_management.get_chart_details(trading_system, signals)
    
    socketio.emit(f"update_data_{trading_bot_id}", data, namespace="/trading_bot_details")

@socketio.on("backtest", namespace="/trading_bot_details")
def handle_backtest(id):
    trading_bot = TradingBot.query.get_or_404(id)
    
    file_path = f'backtest/{trading_bot.symbol}.csv'

    # Check if the file exists
    if not os.path.exists(file_path):
        print("File does not exist.")
        socketio.emit(f"update_data_{trading_bot.id}", None, namespace="/trading_bot_details")
        return

    # Read the CSV file into a DataFrame
    data = pd.read_csv(file_path, usecols=['timestamp','open','high','low','close'])
    
    # Now you can work with your DataFrame
    print(data.head())  # Print the first few rows of the DataFrame
    
    binance_client = FakeTradingClient()
    strategy = trading_bot.get_strategy()
    trading_system = TradingSystem(trading_bot.symbol, strategy, binance_client, trading_bot.trade_percentage, trading_bot.trade_size)
    
    signals = trading_system.run_strategy(data)
    
    data = bot_management.get_chart_details(trading_system, signals, plot_size= None)
    
    socketio.emit(f"update_data_{trading_bot.id}", data, namespace="/trading_bot_details")
    