# app/routes/page2.py
from flask import Blueprint, render_template

page2_bp = Blueprint('page2', __name__)

@page2_bp.route('/page2')
def page2():
    return render_template('page2.html')
