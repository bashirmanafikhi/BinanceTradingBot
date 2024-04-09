from flask import Blueprint, render_template, current_app,request,redirect, Response
from flask_app import socketio
import helpers.my_logger as my_logger
from trading_clients.trading_client_factory import TradingClientFactory
from flask_login import login_required

testpage_bp = Blueprint("testpage", __name__)


# routes
@testpage_bp.route("/testpage")
@login_required
def testpage():
    return render_template(
        "/testpage/testpage.html",
        socket_url=f"{current_app.config['SERVER_URL']}testpage",
        environment=current_app.config["ENVIRONMENT"],
        counter = counter
    )


# events
counter = 0


@socketio.on("increment_counter", namespace="/testpage")
def handle_increment_counter():
    global counter
    counter += 1
    data = {"counter": counter}
    socketio.emit("update_counter", data, namespace="/testpage")

    

@testpage_bp.route('/set-crypto-balances', methods=['POST'])
@login_required
def set_crypto_balances():
    #btc_balance = request.form.get('btcBalance')
    usdt_balance = request.form.get('UsdtBalance')
    
    if(usdt_balance is not None):
        trading_client_factory = TradingClientFactory()
        binance_client = trading_client_factory.create_binance_trading_client()
        binance_client.set_usdt_balance(usdt_balance)
        return binance_client.get_asset_balance("USDT")

    return "Balances received successfully"
