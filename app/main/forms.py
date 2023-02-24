from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class AirportForm(FlaskForm):
    query = StringField('Airport', validators=[DataRequired()])
    submit = SubmitField('Speichern')

class AircraftForm(FlaskForm):
    search_type = SelectField('Search Type', choices=[('0','Aircraft Code'),('1','Manufacturer'),('2','Engine count'),('3','3'),('4','4'),('5', '5'),])
    query = StringField('Search Aircraft', validators=[DataRequired()])