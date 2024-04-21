from models.database_models import User ,TradingBot
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask import Blueprint, render_template, Response
import helpers.my_logger as my_logger
from flask_login import login_required


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('/main/index.html')


@main_bp.route('/profile')
@login_required
def profile():
    return render_template('/main/profile.html', name=current_user.name)

@main_bp.route('/show-logs', methods=['GET'])
@login_required
def show_logs():
    logs = my_logger.read_logs()
    return Response(logs, content_type='text/plain')