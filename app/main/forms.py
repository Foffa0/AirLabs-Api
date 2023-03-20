from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class AirportForm(FlaskForm):
    query = StringField('Airport', validators=[DataRequired()])
    submit = SubmitField('Speichern')

class AircraftForm(FlaskForm):
    query = StringField('Search Aircraft', validators=[DataRequired()])
    submit = SubmitField('Search')