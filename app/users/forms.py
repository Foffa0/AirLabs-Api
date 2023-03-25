from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User
from app import bcrypt


class RegistrationForm(FlaskForm):
    firstName = StringField('First name', validators=[DataRequired(), Length(min=1, max=40)])
    lastName = StringField('Last name', validators=[DataRequired(), Length(min=1, max=40)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=3, max=128)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email existiert bereits. Bitte wähle eine andere!')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Stay logged in')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    firstName = StringField('First name:', validators=[DataRequired(), Length(min=1, max=40)])
    lastName = StringField('Last name:', validators=[DataRequired(), Length(min=1, max=40)])
    email = StringField('Email address:', validators=[DataRequired(), Email()])
    submit = SubmitField('Save')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use. Please choose a different one!')

class UpdatePasswordForm(FlaskForm):
    oldPassword = PasswordField('Old password', validators=[DataRequired(), Length(min=5, max=50)])
    newPassword = PasswordField('New password', validators=[DataRequired(), Length(min=5, max=50)])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('newPassword')])
    submit = SubmitField('Save')
