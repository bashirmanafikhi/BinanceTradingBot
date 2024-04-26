import os
import helpers.my_logger as my_logger
from flask import render_template, redirect, send_file, url_for, flash, current_app,request
from flask_login import current_user, login_required
import pandas as pd
from trading_clients.fake_trading_client import FakeTradingClient
from trading_system import TradingSystem
from current_app_manager import CurrentAppManager
from models.database_models import User, TradingBot
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
        is_running= (trading_system is not None and trading_system.is_running), 
        socket_url=socket_url)


@trading_bot_bp.route('/download_csv/<int:id>')
def download_csv(id):
    trading_bot = TradingBot.query.get_or_404(id)
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    csv_buffer = bot_management.generate_csv(trading_system)

    if csv_buffer is None:
        flash("No data to download", 'danger')
        return redirect(url_for('trading_bot.details', id=id))

    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{trading_bot.get_symbol()}.csv'
    )


@socketio.on("connect", namespace="/trading_bot_details")
def handle_connect():
    print(f"handle_connect livetest")


@trading_bot_bp.route("/start-bot", methods=['POST'])
@login_required
def start_bot():
    id = request.form.get('id')
    result = bot_management.start_bot(id, kline_tick)
    
    flash(result, 'primary')
    return redirect(url_for('trading_bot.details', id=id))

    
@trading_bot_bp.route("/stop-bot", methods=['POST'])
@login_required
def stop_bot():
    id = request.form.get('id')
    result = bot_management.stop_bot(id)
    
    flash(result, 'primary')
    return redirect(url_for('trading_bot.details', id=id))


def kline_tick(data, trading_bot_id):
    trading_system = CurrentAppManager.get_trading_system(trading_bot_id)
    if(trading_system is None):
        return
    
    signals = trading_system.process(data)
    
    data = bot_management.get_chart_details(trading_system, signals)
    
    socketio.emit(f"update_data_{trading_bot_id}", data, namespace="/trading_bot_details")

@socketio.on("backtest", namespace="/trading_bot_details")
def handle_backtest(id):
    trading_bot = TradingBot.query.get_or_404(id)
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if(trading_system is not None and trading_system.is_running):
        print('The bot is running, you can not backtest while the bot is running')
        socketio.emit(f"update_data_{trading_bot.id}", None, namespace="/trading_bot_details")
        return
    
    file_path = f'backtest/{trading_bot.get_symbol()}.csv'

    # Check if the file exists
    if not os.path.exists(file_path):
        print('File is not exist for backtesting.')
        socketio.emit(f"update_data_{trading_bot.id}", None, namespace="/trading_bot_details")
        return

    # Read the CSV file into a DataFrame
    data = pd.read_csv(file_path, usecols=['timestamp','open','high','low','close'])
    
    binance_client = FakeTradingClient()
    strategy = trading_bot.get_strategy()
    trading_system = TradingSystem(trading_bot.base_asset, trading_bot.quote_asset, strategy, binance_client, trading_bot.trade_size)
    
    signals = trading_system.process(data)
    
    for order in trading_system.orders_history:
        my_logger.info(f"action = {order.action},  price = {order.price}, quantity = {order.quantity}, profit = {order.profit}")
    
    total_paid_commission = binance_client.total_paid_commission
    my_logger.info("total_paid_commission :" + str(total_paid_commission))
    
    my_logger.info(f"total_profit = {trading_system.total_profit}")
    my_logger.info(f"total_trades = {len(trading_system.orders_history)}")
    
    data = bot_management.get_chart_details(trading_system, signals, plot_size= None)
    socketio.emit(f"update_data_{trading_bot.id}", data, namespace="/trading_bot_details")
    