from flask_login import UserMixin
from datetime import datetime
from helpers.enums import ExchangeType
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
    exchanges = db.relationship('Exchange', backref='user', lazy=True)
    trading_bots = db.relationship('TradingBot', backref='user', lazy=False)

class TradingBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(255), nullable=False)
    symbol = db.Column(db.String(255), nullable=False)
    trade_percentage = db.Column(db.Float, nullable=True)
    trade_size = db.Column(db.Float, nullable=True)

    # Bollinger Bands Columns
    use_bollinger_bands = db.Column(db.Boolean, nullable=False, default=True)
    bollinger_bands_period = db.Column(db.Float, nullable=False, default=20)
    bollinger_bands_stddev = db.Column(db.Float, nullable=False, default=2)
    
    # RSI Columns
    use_rsi = db.Column(db.Boolean, nullable=False, default=True)
    rsi_period = db.Column(db.Float, nullable=False, default=14)
    rsi_overbought = db.Column(db.Float, nullable=False, default=70)
    rsi_oversold =db. Column(db.Float, nullable=False, default=30)

class Exchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now())
    type = db.Column(Enum(ExchangeType), nullable=False)
    api_Key = db.Column(db.Text, nullable=False)
    api_Secret = db.Column(db.Text, nullable=False)
    is_test = db.Column(db.Boolean, nullable=False)
    trading_bots = db.relationship('TradingBot', backref='exchange', lazy=False)
    