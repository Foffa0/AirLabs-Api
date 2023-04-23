from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Optional
from wtforms import widgets

class AirportForm(FlaskForm):
    query = StringField('Search Airport', validators=[DataRequired()])
    submit = SubmitField('Speichern')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class AircraftForm(FlaskForm):
    query = StringField('Search Aircraft', validators=[Optional()])
    airport_icao = StringField(validators=[DataRequired()])
    #search_option = RadioField('', choices=[(1,'aircraft'), (2, 'engine count')], default=1, coerce=int)
    search_option = SelectField(choices=[(1,'Aircraft'), (2, 'Engine count')], default=1, coerce=int)
    filter = MultiCheckboxField("Filter", choices=[(1, 'Military'), (2, 'Helicopter'), (3, 'Experimental'), (4, 'Prototype'), (5, 'UAV'), (6, 'Airship'), (7, 'Glider')], coerce=int, validators=[Optional()])
    submit = SubmitField('Search', name="submitBtn")
