# run.py

from flask import Flask, render_template
from flask_socketio import SocketIO
from routes.page1 import page1_bp
from routes.page2 import page2_bp

app = Flask(__name__)
socketio = SocketIO(app)

# Define your routes or import them from another module
app.register_blueprint(page1_bp)
app.register_blueprint(page2_bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
