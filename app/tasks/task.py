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
import random

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

  headers = {
    'Authorization': 'Bearer ' + _get_access_token(),
    'Content-Type': 'application/json; UTF-8',
  }

  resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

  if resp.status_code == 200:
    print('Message sent to Firebase for delivery, response:')
    print(resp.text)
  else:
    print('Unable to send message to Firebase')
    print(resp.text)
    print(resp.json()["error"]["status"])
    if resp.json()["error"]["status"] == "INVALID_ARGUMENT" or resp.json()["error"]["status"] == "NOT_FOUND":
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
          'title': 'New Arrival!',
          'body': f'Type: {schedule.aircraft} ({schedule.aircraft_icao}) \nAirport: {airport.name} ({airport.icao}/{airport.iata}) \nTime: {(schedule.time).strftime("%b %d, %H:%M")}',
        },
        'webpush': {
          'fcm_options': {
            'link': 'https://flight-alert.duckdns.org/alerts'
          }
        },
      }
    }
  elif schedule.type == 1:
     return {
      'message': {
        'token': token,
        'notification': {
          'title': 'New Departure',
          'body': f'Type: {schedule.aircraft} ({schedule.aircraft_icao}) \nAirport: {airport.name} ({airport.icao}/{airport.iata}) \nTime: {(schedule.time).strftime("%b %d, %H:%M")}',
        },
        'webpush': {
          'fcm_options': {
            'link': f'https://flight-alert.duckdns.org/alerts'
          }
        },
      }
    }

def run_continuously(app, interval=3600):
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
        schedule.every().day.do(background_job, app=app)
        while not cease_continuous_run.is_set():
          schedule.run_pending()
          #randomise the sleep time to avoid webscraping strikes from flight aware
          time.sleep(interval + random.randint(0,300))
          # time.sleep(interval)

  continuous_thread = ScheduleThread()
  continuous_thread.setDaemon(True)
  continuous_thread.start()
  return cease_continuous_run


def background_job(app):
  # send push messages to the users' devices
  all_airports = Airport.query.all()
  
  scraper = FlightAwareScraper()
  # save all already scraped airports in a list, so we can check for airprot duplicates 
  scraped_airports = []
  
  from app import db

  # remove all alerts and readd them
  alerts = Alert.query.all()
  for alert in alerts:
    db.session.delete(alert)
  db.session.commit()

  for airport in all_airports:
    # skip if the airport data was already collected
    if airport.icao in scraped_airports:
      continue
    else:
      scraped_airports.append(airport.icao)
    
    try:
      airport_schedule = scraper.getAirportData(airport.icao)
    except:
      continue

    users = User.query.all()
    for user in users:
      if not any(y.icao == airport.icao for y in user.airports):
        continue
      for user_airport in user.airports:
        if user_airport.icao == airport.icao:
          airport_id = user_airport.id

      aircrafts = Aircraft.query.filter_by(user_id=user.id)

      for x in airport_schedule:
        for aircraft in aircrafts:
          if aircraft.airport_id == airport_id:
            if str(aircraft.icao) == str(x.aircraft_icao):
              # add alert to user's alert page
              if x.type == 1:
                arrival = False
              else:
                arrival = True
              db.session.add(Alert(flightnumber=x.flightnumber, aircraft_icao=x.aircraft_icao, aircraft=x.aircraft, time=x.time, arrival=arrival, airport_icao=airport.icao, airport_name=airport.name, user_id=aircraft.user_id))
              db.session.commit()

              # send push messages with fcm
              devices = Notification.query.filter_by(user_id=aircraft.user_id)
              for device in devices:
                _send_fcm_message(_build_flight_alert_message(device.token, x, airport), device.token, app)
              continue
  
  # delete all unconfirmed users
  users = User.query.all()
  for user in users:
    if not user.confirmed:
      if datetime.datetime.now() > user.registered_on + datetime.timedelta(days=7):
        db.session.delete(user)
  db.session.commit()

  # delete old alerts
  # alerts = Alert.query.all()
  # for alert in alerts:
  #   if alert.time < datetime.datetime.now():
  #     db.session.delete(alert)
  # db.session.commit()


def startSchedule():
  print("Starting schedule")

  # Start the background thread
  stop_run_continuously = run_continuously(current_app._get_current_object())