from helpers.settings.log_config import configure_logging
from flask_app import create_app, socketio


app = create_app(debug=True)

if __name__ == '__main__':
    configure_logging()
    socketio.run(app)