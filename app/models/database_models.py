from flask_login import UserMixin
from datetime import datetime
from trading_conditions.extra_orders_condition import ExtraOrdersCondition
from trading_conditions.take_profit_condition import TakeProfitCondition
from trading_conditions.stop_loss_condition import StopLossCondition
from trading_conditions.bollinger_bands_condition import BollingerBandsCondition
from trading_conditions.rsi_condition import RSICondition
from trading_strategies.conditions_strategy import ConditionsStrategy
from helpers.enums import BotType, ExchangeType
from flask_app import db
from sqlalchemy import Enum
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import Float
import json

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    exchanges = db.relationship('Exchange', backref='user', lazy=False)
    trading_bots = db.relationship('TradingBot', backref='user', lazy=False)
    
class Exchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now())
    type = db.Column(Enum(ExchangeType), nullable=False)
    api_key = db.Column(db.Text, nullable=False)
    api_secret = db.Column(db.Text, nullable=False)
    is_test = db.Column(db.Boolean, nullable=False)
    trading_bots = db.relationship('TradingBot', backref='exchange', lazy='subquery')

class TradingBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(255), nullable=False)
    base_asset = db.Column(db.String(100), nullable=False)
    quote_asset = db.Column(db.String(100), nullable=False)
    trade_size = db.Column(db.Float, nullable=True)
    bot_type = db.Column(Enum(BotType), nullable=True, default=BotType.LONG.value)
    
    # Stop Loss
    use_stop_loss = db.Column(db.Boolean, nullable=False, default=False)
    stop_loss_percentage = db.Column(db.Float, nullable=False, default=5)
    trailing_stop_loss = db.Column(db.Boolean, nullable=False, default=False)
    stop_loss_timeout = db.Column(db.Integer, nullable=False, default=60)
    
    # Take Profit
    use_take_profit = db.Column(db.Boolean, nullable=False, default=False)
    take_profit_percentage = db.Column(db.Float, nullable=False, default=10)
    trailing_take_profit = db.Column(db.Boolean, nullable=False, default=False)
    trailing_take_profit_deviation_percentage = db.Column(db.Float, nullable=False, default=3)
    
    # Extra Orders
    extra_orders_count = db.Column(db.Integer, nullable=False, default=0)
    
    extra_order_first_volume_scale = db.Column(db.Float, nullable=False, default=1)
    extra_order_first_deviation_percentage = db.Column(db.Float, nullable=False, default=1)
    
    extra_order_step_volume_scale = db.Column(db.Float, nullable=False, default=1)
    extra_order_step_deviation_scale = db.Column(db.Float, nullable=False, default=1)
    
    # start conditions
    start_conditions = db.Column(db.JSON, nullable=True)
    
    def get_symbol(self):
        return f'{self.base_asset}{self.quote_asset}'
    
    def get_strategy(self):
        return ConditionsStrategy(self.get_start_conditions())
    
    # test list
    start_conditions = db.Column(db.JSON, nullable=True)
    
    def get_start_conditions(self):
        conditions_list = []
        
        if(self.use_stop_loss):
            stop_loss_condition = StopLossCondition(self.stop_loss_percentage, 
                                                    self.trailing_stop_loss, 
                                                    self.stop_loss_timeout)
            conditions_list.append(stop_loss_condition)
        
        if(self.use_take_profit):
            take_profit_condition = TakeProfitCondition(self.take_profit_percentage, 
                                                        self.trailing_take_profit, 
                                                        self.trailing_take_profit_deviation_percentage)
            conditions_list.append(take_profit_condition)
        
        if(self.extra_orders_count > 0):
            extra_orders_condition = ExtraOrdersCondition(self.extra_orders_count, 
                                                          self.extra_order_first_volume_scale, 
                                                          self.extra_order_first_deviation_percentage,
                                                          self.extra_order_step_volume_scale,
                                                          self.extra_order_step_deviation_scale)
            conditions_list.append(extra_orders_condition)
        
        for condition in self.start_conditions:    
            if(condition['type'] == 'rsi'):
                rsi_condition = RSICondition(condition['rsi']['period'], 
                                             condition['rsi']['overbought'], 
                                             condition['rsi']['oversold'],
                                             condition['rsi']['use_to_open'],
                                             condition['rsi']['use_to_close'])
                conditions_list.append(rsi_condition)
                
            if(condition['type'] == 'bollinger_bands'):
                bollinger_condition = BollingerBandsCondition(
                                             condition['bollinger_bands']['period'], 
                                             condition['bollinger_bands']['stddev'],
                                             condition['bollinger_bands']['use_to_open'],
                                             condition['bollinger_bands']['use_to_close'])
                conditions_list.append(bollinger_condition)
                
        return conditions_list
    
    