from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired
from helpers.enums import ExchangeType  # Import your Enum

class ExchangeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], coerce=int)
    api_Key = StringField('API Key', validators=[DataRequired()])
    api_Secret = StringField('API Secret', validators=[DataRequired()])
    is_test = BooleanField('Is Test API', default=False)

    def __init__(self, *args, **kwargs):
        super(ExchangeForm, self).__init__(*args, **kwargs)
        
        # Populate choices for the type field with enum values
        self.type.choices = [(choice.value, choice.name) for choice in ExchangeType]
    