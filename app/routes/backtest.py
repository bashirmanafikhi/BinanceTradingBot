from flask import Blueprint, render_template
from flask_app import socketio

backtest_bp = Blueprint('backtest', __name__)


# routes
@backtest_bp.route('/backtest')
def main():
    return render_template('backtest/main.html')

# events
counter = 0
@socketio.on('increment_counter', namespace='/backtest')
def handle_increment_counter():
    global counter
    counter += 1
    data = {'counter': counter}
    socketio.emit('update_counter', data, namespace='/backtest')
