from flask_wtf import FlaskForm
from wtforms import FieldList, Form, FormField, IntegerField, StringField, SelectField, BooleanField, FloatField
from wtforms.validators import DataRequired, Optional, InputRequired
from wtforms import ValidationError
import json

from helpers.enums import BotType


class BollingerBandsForm(Form):
    period = FloatField('Period', validators=[Optional()], default=600)
    stddev = FloatField('Standard Deviation', validators=[Optional()], default=2)
    use_to_open = BooleanField('Open Trades', default=True)
    use_to_close = BooleanField('Close Trades', default=False)

class RSIForm(Form):
    period = FloatField('Period', validators=[Optional()], default=30)
    overbought = FloatField('Overbought Threshold', validators=[Optional()], default=70)
    oversold = FloatField('Oversold Threshold', validators=[Optional()], default=30)
    use_to_open = BooleanField('Open Trades', default=True)
    use_to_close = BooleanField('Close Trades', default=False)

class IndicatorConditionForm(FlaskForm):
    type = SelectField('Type', choices=[('none',''),('bollinger_bands', 'Bollinger Bands'), ('rsi', 'RSI')], validators=[Optional()])
    bollinger_bands = FormField(BollingerBandsForm)
    rsi = FormField(RSIForm)

class TradingBotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    base_asset = StringField('Base Asset', validators=[DataRequired()], default="BTC")
    quote_asset = StringField('Quote Asset', validators=[DataRequired()], default="USDT")
    exchange_id = SelectField('Exchange', coerce=int, validators=[DataRequired()])
    trade_size = FloatField('Trade Size (Quote)', validators=[DataRequired()])
    bot_type = SelectField('Bot Type', choices=[(botType.value, botType.name) for botType in BotType], validators=[Optional()])
    
    # Stop Loss
    use_stop_loss = BooleanField('Use Stop Loss', default=False)
    stop_loss_percentage = FloatField('Stop Loss Deviation Percentage', default=5)
    trailing_stop_loss = BooleanField('Trailing Stop Loss', default=False)
    stop_loss_timeout = IntegerField('Stop Loss Timeout', default=60)
    
    # Take Profit
    use_take_profit = BooleanField('Use Take Profit', default=False)
    take_profit_percentage = FloatField('Take Profit Percentage', default=10)
    trailing_take_profit = BooleanField('Trailing Take Profit', default=False)
    trailing_take_profit_deviation_percentage = FloatField('Trailing Take Profit Deviation Percentage', default=3)
    
    # Extra Orders
    extra_order_size = FloatField('Extra Order Size', default=0)
    extra_orders_count = IntegerField('Extra Orders Count', default=0)
    extra_order_deviation = FloatField('Extra Order Deviation', default=1)
    extra_order_size_scale = FloatField('Extra Order Size Scale', default=1)
    extra_order_deviation_scale = FloatField('Extra Order Deviation Scale', default=1)

    start_conditions = FieldList(FormField(IndicatorConditionForm), min_entries=3)
    
    def set_exchange_choices(self, exchanges):
        self.exchange_id.choices = [(exchange.id, exchange.name) for exchange in exchanges]
        
    # Method to convert form data to JSON compatible with the TradingBot model
    def get_start_conditions(self):
        conditions = []
        for form in self.start_conditions:
            if form.data['type'] == 'bollinger_bands':
                condition = {
                    'type': 'bollinger_bands',
                    'bollinger_bands': {
                        'period': form.bollinger_bands.period.data,
                        'stddev': form.bollinger_bands.stddev.data,
                        'use_to_open' : form.bollinger_bands.use_to_open.data,
                        'use_to_close' :form.bollinger_bands.use_to_close.data
                    }
                }
                conditions.append(condition)
            elif form.data['type'] == 'rsi':
                condition = {
                    'type': 'rsi',
                    'rsi': {
                        'period': form.rsi.period.data,
                        'overbought': form.rsi.overbought.data,
                        'oversold': form.rsi.oversold.data,
                        'use_to_open' : form.rsi.use_to_open.data,
                        'use_to_close' :form.rsi.use_to_close.data
                    }
                }
                conditions.append(condition)
        return conditions

