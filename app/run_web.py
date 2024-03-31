from helpers.settings.log_config import configure_logging
from flask_app import create_app, socketio

app = create_app(debug=True)
configure_logging()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)