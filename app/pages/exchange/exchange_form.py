from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired
from helpers.enums import ExchangeType  # Import your Enum

class ExchangeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], coerce=int, choices=[(choice.value, choice.name) for choice in ExchangeType])
    api_key = StringField('API Key', validators=[DataRequired()])
    api_secret = StringField('API Secret', validators=[DataRequired()])
    is_test = BooleanField('Is Test API', default=True)
    