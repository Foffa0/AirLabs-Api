from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, abort, session
from flask_login import login_user, current_user, logout_user, login_required
#from app import db, bcrypt
from app.models import User, Aircraft, Airport, Notification, Alert
from app.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdatePasswordForm, RequestResetForm, ResetPasswordForm
from app import db, bcrypt
import datetime
from hashlib import sha256
from google_auth_oauthlib.flow import InstalledAppFlow
from app.users.utils import send__email
from app.decorators import check_confirmed, admin_required
import os
import pickle

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
    if current_user.confirmed:
        flash('Account already confirmed', 'warning')
        return redirect(url_for('main.index'))
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
    if not current_user.confirmed:
        response = send__email(current_user, 0)

        # check if the oauth2 client token needs to be renewed
        if (response == -1 and current_user.admin):
            return redirect(url_for('users.authorize'))
        
        flash('A new confirmation email has been sent.', 'success')
        return redirect(url_for('users.unconfirmed'))
    flash('Account already confirmed', 'warning')
    return redirect(url_for('main.index'))

@users.route('/activate_account')
@login_required
def unconfirmed():
    if current_user.confirmed:
        flash('Account already confirmed', 'warning')
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
        response = send__email(user, 1)

        # check if the oauth2 client token needs to be renewed
        if response == -1 and current_user.admin:
            return redirect(url_for('users.authorize'))

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
@admin_required
def admin_state(id):
    if current_user.id == id:
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
@admin_required
def admin():
    users = User.query.all()
    airports = Airport.query.all()
    aircrafts = Aircraft.query.all()
    devices = Notification.query.all()
    alerts = Alert.query.all()
    return render_template('admin/admin.html', title='Admin FlightAlert', userCount=len(users), airportCount=len(airports), aircraftCount=len(aircrafts), devicesCount=len(devices), alertCount=len(alerts))

@users.route("/admin/users")
@login_required
@check_confirmed
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/admin_details.html', title='Admin FlightAlert', users=users, airports=None, aircrafts=None, devices=None, alerts=None)

@users.route("/admin/airports")
@login_required
@check_confirmed
@admin_required
def admin_airports():
    airports = Airport.query.all()
    return render_template('admin/admin_details.html', title='Admin FlightAlert', airports=airports, users=None, aircrafts=None, devices=None, alerts=None)

@users.route("/admin/aircrafts")
@login_required
@check_confirmed
@admin_required
def admin_aircrafts():
        aircrafts = Aircraft.query.all()
        return render_template('admin/admin_details.html', title='Admin FlightAlert', aircrafts=aircrafts, airports=None, users=None, devices=None, alerts=None)

@users.route("/admin/devices")
@login_required
@check_confirmed
@admin_required
def admin_devices():
    devices = Notification.query.all()
    return render_template('admin/admin_details.html', title='Admin FlightAlert', devices=devices, airports=None, aircrafts=None, users=None, alerts=None)

@users.route("/admin/alerts")
@login_required
@check_confirmed
@admin_required
def admin_alerts():
    alerts = Alert.query.all()
    return render_template('admin/admin_details.html', title='Admin FlightAlert', alerts=alerts, airports=None, aircrafts=None, devices=None, users=None)


@users.route("/oauth/authorize")
@login_required
@check_confirmed
@admin_required
def authorize():
    SCOPES = ['https://mail.google.com/']
    flow = InstalledAppFlow.from_client_secrets_file(current_app.config['OAUTH2_TOKEN'], SCOPES)

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = 'https://flight-alert.duckdns.org/oauth2callback'

    stateHash = sha256(os.urandom(1024)).hexdigest()
     
    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        state=stateHash,
        login_hint='noreply.airportactivity@gmail.com',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@users.route('/oauth2callback')
@login_required
@check_confirmed
@admin_required
def oauth2callback():
    SCOPES = ['https://mail.google.com/']
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = InstalledAppFlow.from_client_secrets_file(
        current_app.config['OAUTH2_TOKEN'], scopes=SCOPES, state=state)
    flow.redirect_uri = 'https://flight-alert.duckdns.org/oauth2callback'

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = 'https://flight-alert.duckdns.org' + request.full_path
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    # Save the access token in token.pickle file for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials, token)
  
    flash('succesfully updated credentials')
    return redirect(url_for('main.index'))
