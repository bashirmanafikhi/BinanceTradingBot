from flask import Config, Flask, render_template
from flask_socketio import SocketIO
from helpers.settings.log_config import configure_logging
from helpers.settings.config import get_config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__, template_folder='pages')
    app.debug = debug
    
    # Use the appropriate configuration based on the environment
    app.config.from_object(get_config())

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from helpers.models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    from pages.main.main_route import main_bp
    from pages.auth.auth_route import auth_bp
    from pages.exchange.exchange_route import exchange_bp
    from pages.trading_bot.trading_bot_route import trading_bot_bp
    from pages.livetest.livetest_route import livetest_bp
    from pages.testpage.testpage_route import testpage_bp
    
    app.register_blueprint(exchange_bp)
    app.register_blueprint(trading_bot_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(livetest_bp)
    app.register_blueprint(testpage_bp)


    # Create the database tables
    with app.app_context():
        db.create_all()

    socketio.init_app(app)
    return app