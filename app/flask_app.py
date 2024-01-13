from flask import Flask, render_template
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    #app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    @app.route('/')
    def home():
        return render_template('index.html')

    from routes.backtest import backtest_bp
    from routes.livetest import livetest_bp
    
    app.register_blueprint(backtest_bp)
    app.register_blueprint(livetest_bp)

    socketio.init_app(app)
    return app