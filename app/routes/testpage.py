from flask import Blueprint, render_template
from flask_app import socketio

testpage_bp = Blueprint('testpage', __name__)

# routes
@testpage_bp.route('/testpage')
def testpage():
    return render_template('testpage/testpage.html')