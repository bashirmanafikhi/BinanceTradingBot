from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from flask_app import db
from helpers.models import User, Exchange
from pages.exchange.exchange_form import ExchangeForm
from helpers.enums import ExchangeType


exchange_bp = Blueprint('exchange', __name__, url_prefix='/exchange')

@exchange_bp.route("/list")
@login_required
def user_exchanges():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    exchanges = user.exchanges
    return render_template('/exchange/exchanges.html', exchanges=exchanges, user=user)

@exchange_bp.route("/create", methods=['GET', 'POST'])
@login_required
def create_exchange():
    form = ExchangeForm()
    if form.validate_on_submit():
        exchange = Exchange(
            name=form.name.data, 
            type=ExchangeType(form.type.data),
            api_Key=form.api_Key.data,
            api_Secret=form.api_Secret.data,
            is_test=form.is_test.data,
            user=current_user
        )
        db.session.add(exchange)
        db.session.commit()
        flash('Exchange created successfully!', 'success')
        return redirect(url_for('exchange.user_exchanges'))
    return render_template('/exchange/exchange_create_form.html', form=form, exchange_types=ExchangeType)

@exchange_bp.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_exchange(id):
    exchange = Exchange.query.get_or_404(id)
    form = ExchangeForm(obj=exchange)
    if form.validate_on_submit():
        form.populate_obj(exchange)
        exchange.type = ExchangeType(form.type.data)
        db.session.commit()
        flash('Exchange updated successfully!', 'success')
        return redirect(url_for('exchange.user_exchanges'))
    return render_template('exchange/exchange_update_form.html', form=form)

@exchange_bp.route("/delete/<int:id>", methods=['POST'])
@login_required
def delete_exchange(id):
    exchange = Exchange.query.get_or_404(id)
    db.session.delete(exchange)
    db.session.commit()
    flash('Exchange deleted successfully!', 'success')
    return redirect(url_for('exchange.user_exchanges'))
