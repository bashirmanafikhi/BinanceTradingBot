from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from flask_app import db
from helpers.models import Exchange, User, TradingBot
from pages.trading_bot.trading_bot_form import TradingBotForm


trading_bot_bp = Blueprint('trading_bot', __name__, url_prefix='/trading_bot')


@trading_bot_bp.route("/list")
@login_required
def user_trading_bots():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    trading_bots = user.trading_bots
    return render_template('/trading_bot/trading_bots.html', trading_bots=trading_bots)


@trading_bot_bp.route("/create", methods=['GET', 'POST'])
@login_required
def create_trading_bot():
    form = TradingBotForm()

    # Set choices for the exchange_id field
    form.exchange_id.choices = [(exchange.id, exchange.name) for exchange in Exchange.query.all()]

    if form.validate_on_submit():
        trading_bot = TradingBot(
            name=form.name.data, 
            symbol=form.symbol.data,
            exchange_id=form.exchange_id.data,
            user=current_user
        )
        db.session.add(trading_bot)
        db.session.commit()
        flash('TradingBot created successfully!', 'success')
        return redirect(url_for('trading_bot.user_trading_bots'))
    

    return render_template('/trading_bot/trading_bot_create_form.html', form=form)

@trading_bot_bp.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_trading_bot(id):
    trading_bot = TradingBot.query.get_or_404(id)
    form = TradingBotForm(obj=trading_bot)

    # Set choices for the exchange_id field
    form.exchange_id.choices = [(exchange.id, exchange.name) for exchange in Exchange.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(trading_bot)
        db.session.commit()
        flash('TradingBot updated successfully!', 'success')
        return redirect(url_for('trading_bot.user_trading_bots'))
    return render_template('/trading_bot/trading_bot_update_form.html', form=form)

@trading_bot_bp.route("/delete/<int:id>", methods=['POST'])
@login_required
def delete_trading_bot(id):
    trading_bot = TradingBot.query.get_or_404(id)
    db.session.delete(trading_bot)
    db.session.commit()
    flash('TradingBot deleted successfully!', 'success')
    return redirect(url_for('trading_bot.user_trading_bots'))
