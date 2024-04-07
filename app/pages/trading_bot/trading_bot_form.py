from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired

class TradingBotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    symbol = StringField('Symbol', validators=[DataRequired()])
    exchange_id = SelectField('Exchange', coerce=int, validators=[DataRequired()])

    def set_exchange_choices(self, exchanges):
        self.exchange_id.choices = [(exchange.id, exchange.name) for exchange in exchanges]
    