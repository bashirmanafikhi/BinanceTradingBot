from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from pages.trading_bot.trading_bot_management import update_running_trading_system
from current_app_manager import CurrentAppManager
from flask_app import db
from helpers.models import Exchange, User, TradingBot
from pages.trading_bot.trading_bot_form import TradingBotForm

trading_bot_bp = Blueprint('trading_bot', __name__, url_prefix='/trading_bot')

from . import trading_bot_details_route

@trading_bot_bp.route("/list")
@login_required
def user_trading_bots():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    trading_bots = user.trading_bots
    
    trading_systems = CurrentAppManager.get_all_trading_systems()
    
    bot_system_pairs = []
    for bot in trading_bots:
        trading_system = trading_systems.get(bot.id)
        bot_system_pairs.append((bot, trading_system))
        
    # Sort the list by total_profit
    bot_system_pairs = sorted(bot_system_pairs, key=lambda pair: pair[1].total_profit if pair[1] else float('-inf'), reverse=True)

    payload = {
        "running_bots_count" : len(trading_systems),
        "not_running_bots_count" : len(trading_bots) - len(trading_systems),
        "total_trades_count" : sum(system.trades_count for system in trading_systems.values()),
        "total_profit" : sum(system.total_profit for system in trading_systems.values()),
        "bot_system_pairs" : bot_system_pairs
    }
    return render_template('/trading_bot/trading_bots.html', payload = payload)


@trading_bot_bp.route("/create", methods=['GET', 'POST'])
@login_required
def create_trading_bot():
    form = TradingBotForm()

    form.exchange_id.choices = [(exchange.id, exchange.name) for exchange in Exchange.query.all()]

    if form.validate_on_submit():
        
        trading_bot = TradingBot()
        form.populate_obj(trading_bot) 
        trading_bot.user = current_user  
        
        db.session.add(trading_bot)
        db.session.commit()
        flash('TradingBot created successfully!', 'success')
        return redirect(url_for('trading_bot.details', id=trading_bot.id))
    

    return render_template('/trading_bot/trading_bot_create.html', form=form)

@trading_bot_bp.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_trading_bot(id):
    trading_bot = TradingBot.query.get_or_404(id)
    form = TradingBotForm(obj=trading_bot)

    form.exchange_id.choices = [(exchange.id, exchange.name) for exchange in Exchange.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(trading_bot)
        
        db.session.commit()
        flash('TradingBot updated successfully!', 'success')
        update_running_trading_system(trading_bot)
        return redirect(url_for('trading_bot.details', id=trading_bot.id))
    return render_template('/trading_bot/trading_bot_update.html', form=form)

@trading_bot_bp.route("/delete/<int:id>", methods=['POST'])
@login_required
def delete_trading_bot(id):
    #todo: prevent remove if the bot is running.
    trading_bot = TradingBot.query.get_or_404(id)
    db.session.delete(trading_bot)
    db.session.commit()
    flash('TradingBot deleted successfully!', 'success')
    return redirect(url_for('trading_bot.user_trading_bots'))
