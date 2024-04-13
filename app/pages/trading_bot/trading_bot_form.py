from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, FloatField
from wtforms.validators import DataRequired, Optional, InputRequired
from wtforms import ValidationError

class TradingBotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    exchange_id = SelectField('Exchange', coerce=int, validators=[DataRequired()])
    base_asset = StringField('Base Asset', validators=[DataRequired()], default="BTC")
    quote_asset = StringField('Quote Asset', validators=[DataRequired()], default="USDT")
    
    use_bollinger_bands = BooleanField('Use Bollinger Bands', default=True)
    bollinger_bands_period = FloatField('Bollinger Bands Period', validators=[DataRequired()], default=600)
    bollinger_bands_stddev = FloatField('Bollinger Bands Standard Deviation', validators=[DataRequired()], default=2)
    
    use_rsi = BooleanField('Use RSI', default=True)
    rsi_period = FloatField('RSI Period', validators=[DataRequired()], default=30)
    rsi_overbought = FloatField('RSI Overbought Threshold', validators=[DataRequired()], default=70)
    rsi_oversold = FloatField('RSI Oversold Threshold', validators=[DataRequired()], default=30)

    trade_size = FloatField('Trade Size (Quote)', validators=[DataRequired()])

    def set_exchange_choices(self, exchanges):
        self.exchange_id.choices = [(exchange.id, exchange.name) for exchange in exchanges]
