from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from helpers.enums import BotType
from pages.trading_bot.trading_bot_management import update_running_trading_system
from current_app_manager import CurrentAppManager
from flask_app import db
from models.database_models import Exchange, User, TradingBot
from pages.trading_bot.trading_bot_form import IndicatorConditionForm, TradingBotForm
import json


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

    running_bots_count = len([trading_system for trading_system in trading_systems.values() if trading_system.is_running])
    payload = {
        "running_bots_count" : running_bots_count,
        "not_running_bots_count" : len(trading_bots) - running_bots_count,
        "total_trades_count" : sum(system.trades_count for system in trading_systems.values()),
        "total_profit" : sum(system.total_profit for system in trading_systems.values()),
        "bot_system_pairs" : bot_system_pairs
    }
    return render_template('/trading_bot/trading_bots.html', payload = payload)

@trading_bot_bp.route("/create", methods=['GET', 'POST'])
@login_required
def create_trading_bot():
    form = TradingBotForm()

    fill_exchanges(form)

    if form.validate_on_submit():
        trading_bot = TradingBot()
        
        for name, field in form._fields.items():
            if(name == 'start_conditions'):
                continue
            field.populate_obj(trading_bot, name)
            
        trading_bot.start_conditions = form.get_start_conditions()
        trading_bot.user = current_user  
        
        db.session.add(trading_bot)
        db.session.commit()
        flash('TradingBot created successfully!', 'success')
        return redirect(url_for('trading_bot.details', id=trading_bot.id))
    

    return render_template('/trading_bot/trading_bot_create.html', form=form)

def fill_exchanges(form):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    exchanges = user.exchanges
    form.set_exchange_choices(exchanges)

@trading_bot_bp.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_trading_bot(id):
    trading_bot = TradingBot.query.get_or_404(id)

    # Pass the Enum member to the form
    form = TradingBotForm(obj=trading_bot)
    fill_exchanges(form)
    
    if form.validate_on_submit(): 
        
        for name, field in form._fields.items():
            if(name == 'start_conditions'):
                continue
            field.populate_obj(trading_bot, name)
            
        trading_bot.start_conditions = form.get_start_conditions()
        
        db.session.commit()
        flash('TradingBot updated successfully!', 'success')
        update_running_trading_system(trading_bot)
        return redirect(url_for('trading_bot.details', id=trading_bot.id))
    return render_template('/trading_bot/trading_bot_update.html', form=form)

@trading_bot_bp.route("/delete/<int:id>", methods=['POST'])
@login_required
def delete_trading_bot(id):
    trading_bot = TradingBot.query.get_or_404(id)
    trading_system = CurrentAppManager.get_trading_system(trading_bot.id)
    if(trading_system is not None and trading_system.is_running):
        flash('TradingBot is running, stop it befor deletion!', 'danger')
        return redirect(url_for('trading_bot.user_trading_bots'))
    db.session.delete(trading_bot)
    db.session.commit()
    flash('TradingBot deleted successfully!', 'success')
    return redirect(url_for('trading_bot.user_trading_bots'))
