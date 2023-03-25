from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
#from app import db, bcrypt
from app.models import User
from app.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdatePasswordForm
from app.config import Config
from app import db, bcrypt
import datetime
from app.users.utils import send_activation_email
from app.decorators import check_confirmed

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.confirmed:
            flash('You are already logged in!', 'warning')
            return redirect(url_for('main.alerts'))
        return render_template('public/activate_account.html')
        
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, password=hashed_password, confirmed=False, registered_on=datetime.date.today())
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        login_user(user)
        return redirect(url_for('users.unconfirmed'))
    return render_template('public/register.html', title='Register FlightAlert Account', form=form)

@users.route('/account/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        user_email = current_user.verify_activation_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('users.unconfirmed'))
    if user_email is None:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('users.unconfirmed'))
    user = User.query.filter_by(email=user_email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        logout_user()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('users.login'))

@users.route('/resend')
@login_required
def resend_confirmation():
    send_activation_email(current_user)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('users.unconfirmed'))

@users.route('/activate_account')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('public/activate_account.html')


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login failed. Please check your email and password!', 'danger')
    return render_template('public/login.html', title='Login - FlightAlert', form=form)
    
@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
@check_confirmed
def account():
    form = UpdateAccountForm()
    pw_form = UpdatePasswordForm()

    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        db.session.commit()
        flash('Your account information has been successfully updated.', 'success')
        return render_template('public/account.html', title='Account - AirportActivity', accountForm=form, passwordForm=pw_form, user=current_user)
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
    
    if pw_form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password, pw_form.oldPassword.data):
            flash('Wrong password. Please try again!', 'warning')
            return render_template('public/account.html', title='Account - AirportActivity', accountForm=form, passwordForm=pw_form, user=current_user)

        hashed_password = bcrypt.generate_password_hash(pw_form.newPassword.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash('Your password has been successfully updated.', 'success')
    return render_template('public/account.html', title='Account - AirportActivity', accountForm=form, passwordForm=pw_form, user=current_user)
