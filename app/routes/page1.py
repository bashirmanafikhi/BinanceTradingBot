# app/routes/page1.py
from flask import Blueprint, render_template

page1_bp = Blueprint('page1', __name__)

@page1_bp.route('/page1')
def page1():
    return render_template('page1.html')
