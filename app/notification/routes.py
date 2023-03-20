import json
from flask import request, Response, render_template, jsonify, Flask, Blueprint, current_app
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import time
from firebase_admin import messaging
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

@notification.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
  registration_token = json.loads(request.data)['token']

  print(registration_token)
  # See documentation on defining a message payload.

  _send_fcm_message(_build_common_message(registration_token))  
  return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

PROJECT_ID = 'flightalert-380817'
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  credentials = service_account.Credentials.from_service_account_file(current_app.config['GOOGLE_APPLICATION_CREDENTIALS'], scopes=SCOPES)
  request = google.auth.transport.requests.Request()
  credentials.refresh(request)
  return credentials.token


def _send_fcm_message(fcm_message):
  """Send HTTP request to FCM with given message.
  Args:
    fcm_message: JSON object that will make up the body of the request.
  """
  # [START use_access_token]
  headers = {
    'Authorization': 'Bearer ' + _get_access_token(),
    'Content-Type': 'application/json; UTF-8',
  }
  # [END use_access_token]
  resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

  if resp.status_code == 200:
    print('Message sent to Firebase for delivery, response:')
    print(resp.text)
  else:
    print('Unable to send message to Firebase')
    print(resp.text)

def _build_common_message(token):
  """Construct common notifiation message.
  Construct a JSON object that will be used to define the
  common parts of a notification message that will be sent
  to any app instance subscribed to the news topic.
  """
  return {
    'message': {
      'token': token,
      'notification': {
        'title': 'FCM Notification',
        'body': 'Notification from FCM'
      }
    }
  }