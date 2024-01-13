from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/test500')
def test_500():
    return render_template('errors/500.html')


# Custom error handler for internal server errors (HTTP 500)
@app.errorhandler(500)
def internal_server_error(e):
    # Log the error
    app.logger.error('An internal server error occurred: %s', e)
    # Return the error page from the 'errors' folder
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
