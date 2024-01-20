from flask import Blueprint, render_template

backtest_bp = Blueprint('backtest', __name__)

# routes
@backtest_bp.route('/backtest')
def main():
    return render_template('backtest/main.html')
