import json
from flask import request, render_template, Blueprint, flash, redirect, url_for
from flask_login import current_user
from app.models import Notification
from app import db
from flask_login import login_required
from app.decorators import check_confirmed

# if the operating machine settings are corrupted
import mimetypes
mimetypes.add_type('text/javascript', '.js')

notification = Blueprint('notification', __name__)

@notification.route('/notify')
def index():
  return render_template('public/web_push.html')

@notification.route('/firebase-messaging-sw.js')
def service_worker():
  from flask import make_response, send_from_directory
  response = make_response(send_from_directory(directory='static',path='firebase-messaging-sw.js'))
  response.headers['Content-Type'] = 'application/javascript'
  response.headers['Service-Worker-Allowed'] = '/'
  return response

@notification.route('/add-token', methods = ['POST'])
@login_required
@check_confirmed
def get_device_token():
  registration_token = json.loads(request.data)['token']

  device = Notification.query.filter_by(token=registration_token).first()
  if device:
    flash('Token already in database!', 'warning')
    return redirect(url_for('main.alerts'))

  device = Notification(token=registration_token, user_id=current_user.id)
  db.session.add(device)
  db.session.commit()
  return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@notification.route('/remove-token', methods = ['POST'])
@login_required
@check_confirmed
def remove_device_token():
  registration_token = json.loads(request.data)['token']
  try:
    device = Notification.query.filter_by(token=registration_token).first()
    if not device is None:
      db.session.delete(device)
      db.session.commit()
  except:
    pass
  return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 