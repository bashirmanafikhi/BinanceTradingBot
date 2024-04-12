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
