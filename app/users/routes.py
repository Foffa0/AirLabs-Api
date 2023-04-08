from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, abort
from flask_login import login_user, current_user, logout_user, login_required
#from app import db, bcrypt
from app.models import User, Aircraft, Airport, Notification, Alert
from app.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdatePasswordForm, RequestResetForm, ResetPasswordForm
from app import db, bcrypt
import datetime
from app.users.utils import send__email
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
        user = User(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, password=hashed_password, confirmed=False, registered_on=datetime.datetime.now())
        db.session.add(user)
        db.session.commit()
        send__email(user, 0)
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
    send__email(current_user, 0)
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

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send__email(user, 1)
        flash(f'An email with a reset link has been sent to {user.email}.', 'info')
        return redirect(url_for('users.login'))
    return render_template('public/reset_request.html', title='Request password reset', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can log in now.', 'success')
        return redirect(url_for('users.login'))
    return render_template('public/reset_password.html', title='Reset FlightAlert password', form=form)


@users.route("/account/delete/<int:id>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def account_delete(id):
    if current_user.id != id and not current_user.admin:
        abort(403)
    
    user = User.query.get(id)
    if user.admin:
        abort(403)
    
    aircrafts = Aircraft.query.filter_by(user_id=user.id)
    for aircraft in aircrafts:
        db.session.delete(aircraft)
    db.session.commit()
    airports = Airport.query.filter_by(user_id=user.id)
    for airport in airports:
        db.session.delete(airport)
    db.session.commit()
    notifications = Notification.query.filter_by(user_id=user.id)
    for notification in notifications:
        db.session.delete(notification)
    db.session.commit()
    alerts = Alert.query.filter_by(user_id=user.id)
    for alert in alerts:
        db.session.delete(alert)
    
    db.session.delete(user)
    if current_user.id == id:
        logout_user()
    db.session.commit()
    flash('Account succesfully deleted.', 'success')
    return redirect(url_for('main.index'))

#
# Admin pages
#

@users.route("/admin/toggle/<int:id>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def admin_state(id):
    if current_user.id == id or not current_user.admin:
        abort(403)
    
    user = User.query.get(id)
    
    if user.email == current_app.config['ADMIN_EMAIL']:
        flash('You cannot remove admin state from the admin!', 'warning')
        return redirect(url_for('users.user_administration'))
    
    if user.admin:
        user.admin = False
    else:
        user.admin = True

    db.session.commit()

    flash('Account succesfully updated.', 'success')
    return redirect(url_for('users.admin'))

@users.route("/admin")
@login_required
@check_confirmed
def admin():
    if current_user.admin:
        users = User.query.all()
        airports = Airport.query.all()
        aircrafts = Aircraft.query.all()
        devices = Notification.query.all()
        alerts = Alert.query.all()
        return render_template('admin/admin.html', title='Admin FlightAlert', userCount=len(users), airportCount=len(airports), aircraftCount=len(aircrafts), devicesCount=len(devices), alertCount=len(alerts))
    else:
        abort(403)

@users.route("/admin/users")
@login_required
@check_confirmed
def admin_users():
    if current_user.admin:
        users = User.query.all()
        return render_template('admin/admin_details.html', title='Admin FlightAlert', users=users, airports=None, aircrafts=None, devices=None, alerts=None)
    else:
        abort(403)

@users.route("/admin/airports")
@login_required
@check_confirmed
def admin_airports():
    if current_user.admin:
        airports = Airport.query.all()
        return render_template('admin/admin_details.html', title='Admin FlightAlert', airports=airports, users=None, aircrafts=None, devices=None, alerts=None)
    else:
        abort(403)

@users.route("/admin/aircrafts")
@login_required
@check_confirmed
def admin_aircrafts():
    if current_user.admin:
        aircrafts = Aircraft.query.all()
        return render_template('admin/admin_details.html', title='Admin FlightAlert', aircrafts=aircrafts, airports=None, users=None, devices=None, alerts=None)
    else:
        abort(403)

@users.route("/admin/devices")
@login_required
@check_confirmed
def admin_devices():
    if current_user.admin:
        devices = Notification.query.all()
        return render_template('admin/admin_details.html', title='Admin FlightAlert', devices=devices, airports=None, aircrafts=None, users=None, alerts=None)
    else:
        abort(403)

@users.route("/admin/alerts")
@login_required
@check_confirmed
def admin_alerts():
    if current_user.admin:
        alerts = Alert.query.all()
        return render_template('admin/admin_details.html', title='Admin FlightAlert', alerts=alerts, airports=None, aircrafts=None, devices=None, users=None)
    else:
        abort(403)