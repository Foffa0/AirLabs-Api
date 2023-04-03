import threading
import time
from flask import current_app
import json
import schedule
from app.tasks.scraper import FlightAwareScraper
from app.models import Notification, Aircraft, Airport, User, Alert
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import datetime
import time

#
# FMC push messages
#
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


def _send_fcm_message(fcm_message, token, app):
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
    print(resp.json()["error"]["status"])
    if resp.json()["error"]["status"] == "INVALID_ARGUMENT":
      device = Notification.query.filter_by(token=token).first()
      try:
        from app import db
        db.session.delete(device)
        db.session.commit()
      except Exception as e:
        print(e)

def _build_flight_alert_message(token, schedule, airport):
  """Construct common notifiation message.
  Construct a JSON object that will be used to define the
  common parts of a notification message that will be sent
  to any app instance subscribed to the news topic.
  """
  if schedule.type == 0:
    return {
      'message': {
        'token': token,
        'notification': {
          'title': 'New flight Alert',
          'body': f'{schedule.aircraft} ({schedule.aircraft_icao}) arriving at {airport} on {datetime.datetime.fromtimestamp(schedule.time).strftime("%b %d, %Y %H:%M")}',
        },
        'webpush': {
          'headers': {
            'image': 'https://www.gstatic.com/devrel-devsite/prod/vc7c98be6f4d139e237c3cdaad6a00bb295b070a83e505cb2fa4435daae3d0901/firebase/images/touchicon-180.png'
          },
          'fcm_options': {
            'link': f'https://de.flightaware.com/live/airport/{airport}'
          }
        },
        "android":{
          "notification":{
            "image":"https://www.gstatic.com/devrel-devsite/prod/vc7c98be6f4d139e237c3cdaad6a00bb295b070a83e505cb2fa4435daae3d0901/firebase/images/touchicon-180.png"
          }
        },
      }
    }
  elif schedule.type == 1:
     return {
      'message': {
        'token': token,
        'notification': {
          'title': 'New flight Alert',
          'body': f'{schedule.aircraft} ({schedule.aircraft_icao}) departing at {airport} on {datetime.datetime.fromtimestamp(schedule.time).strftime("%b %d, %Y %H:%M")}',
          'image': 'https://www.gstatic.com/devrel-devsite/prod/vc7c98be6f4d139e237c3cdaad6a00bb295b070a83e505cb2fa4435daae3d0901/firebase/images/touchicon-180.png'
        }
      }
    }

def run_continuously(app, interval=100):
  """Continuously run, while executing pending jobs at each
  elapsed time interval.
  @return cease_continuous_run: threading. Event which can
  be set to cease continuous run. Please note that it is
  *intended behavior that run_continuously() does not run
  missed jobs*. For example, if you've registered a job that
  should run every minute and you set a continuous run
  interval of one hour then your job won't be run 60 times
  at each interval but only once.
  """
  cease_continuous_run = threading.Event()
  
  class ScheduleThread(threading.Thread):
    @classmethod
    def run(cls):
      with app.app_context():
        schedule.every().minute.do(background_job, app=app)
        while not cease_continuous_run.is_set():
          schedule.run_pending()
          time.sleep(interval)

  continuous_thread = ScheduleThread()
  continuous_thread.setDaemon(True)
  continuous_thread.start()
  return cease_continuous_run


def background_job(app):
  # send push messages to the users' devices
  all_airports = Airport.query.all()
  sorted_airports = []
  for airport in all_airports:
    if not airport.icao in sorted_airports:
      sorted_airports.append(airport.icao)
  aircrafts = Aircraft.query.all()
  scraper = FlightAwareScraper()
  from app import db
  for airport in sorted_airports:
    airport_schedule = scraper.getAirportData(airport)
    for x in airport_schedule:
      for aircraft in aircrafts:
        if aircraft.icao == x.aircraft_icao:
          # add alert to user's alert page
          if x.type == 1:
            arrival = False
          else:
            arrival = True
          db.session.add(Alert(flightnumber=x.flightnumber, aircraft_icao=x.aircraft_icao, aircraft=x.aircraft, time=int(x.time), arrival=arrival, airport_icao=airport, user_id=aircraft.user_id))
          db.session.commit()

          devices = Notification.query.filter_by(user_id=aircraft.user_id)
          for device in devices:
            _send_fcm_message(_build_flight_alert_message(device.token, x, airport), device.token, app)
  
  # delete all unconfirmed users
  users = User.query.all()
  for user in users:
    if not user.confirmed:
      if datetime.datetime.now() > user.registered_on + datetime.timedelta(days=7):
        db.session.delete(user)
  db.session.commit()

  # delete old alerts
  alerts = Alert.query.all()
  for alert in alerts:
    if alert.time < int(time.time()):
      db.session.delete(alert)
  db.session.commit()


def startSchedule():
  print("Starting schedule")

  # Start the background thread
  stop_run_continuously = run_continuously(current_app._get_current_object())