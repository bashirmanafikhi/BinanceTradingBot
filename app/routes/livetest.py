# app/routes/livetest.py
from flask import Blueprint, render_template

livetest_bp = Blueprint('livetest', __name__)

@livetest_bp.route('/livetest')
def main():
    return render_template('livetest/main.html')
