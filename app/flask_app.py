from flask import Config, Flask, render_template
from flask_socketio import SocketIO

from helpers.settings.config import get_config

socketio = SocketIO(cors_allowed_origins="*")

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    
    # Use the appropriate configuration based on the environment
    app.config.from_object(get_config())

    @app.route('/')
    def home():
        return render_template('index.html')

    from routes.livetest import livetest_bp
    from routes.backtest import backtest_bp
    from routes.testpage import testpage_bp
    
    app.register_blueprint(backtest_bp)
    app.register_blueprint(livetest_bp)
    app.register_blueprint(testpage_bp)

    socketio.init_app(app)
    return app