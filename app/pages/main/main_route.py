from flask_app import db
from helpers.models import User ,TradingBot
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('/main/index.html')


@main_bp.route('/profile')
@login_required
def profile():
    return render_template('/main/profile.html', name=current_user.name)