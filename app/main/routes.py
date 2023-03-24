from flask import render_template, Blueprint, redirect, url_for, current_app
from flask_login import current_user
from flask_login import login_required
#from app.models import Recipe
from app import db
from app.models import User, Aircraft, Airport
import requests
from requests.exceptions import HTTPError
from app.main.forms import AirportForm, AircraftForm
from app.data.airport import Airport
from app.data.aircraft import Aircraft
import json
from app.tasks.scraper import FlightAwareScraper
from app.decorators import check_confirmed


main = Blueprint('main', __name__)

savedAirports = []

@main.route("/")
@main.route("/index")
def index():

    return render_template("public/index.html")

@main.route("/alerts", methods=['GET', 'POST'])
@login_required
@check_confirmed
def alerts():
    form = AirportForm()
    aircraftForm = AircraftForm()
    return render_template("public/alerts.html", form=form, aircraftForm=aircraftForm, airports=savedAirports)

@main.route("/search-airport", methods=['GET', 'POST'])
@login_required
@check_confirmed
def searchAirport():
    form = AirportForm()
    aircraftForm = AircraftForm()

    if form.validate_on_submit():
        query = form.query.data
        try:
            response = requests.get(f'https://airlabs.co/api/v9/suggest?q={query}&api_key={current_app.config["AIR_LABS_API_KEY"]}')

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            airports = []
            response = response.json()
            for airport in response["response"]["airports"]:
                airports.append(Airport(airport))
        return render_template("public/alerts.html", form=form, aircraftForm=aircraftForm, airportResults=airports, airports=savedAirports)


@main.route("/search-aircraft", methods=['GET', 'POST'])
@login_required
@check_confirmed
def searchAircraft():
    form = AirportForm()
    aircraftForm = AircraftForm()
    
    if aircraftForm.validate_on_submit():
        query = aircraftForm.query.data
        aircrafts = []

        with open("app/data/aircrafts.json", "r", encoding="utf8") as read_file:
            data = json.load(read_file)
            for x, aircraft in enumerate(data):
                new_aircraft = None
                if aircraft['icaoCode']:
                    if query in aircraft['icaoCode']:
                        new_aircraft = Aircraft(data[x])
                if query in aircraft['name']:
                    new_aircraft = Aircraft(data[x])
                elif query in aircraft['manufacturer']:
                    new_aircraft = Aircraft(data[x])

                if new_aircraft:
                    if not any(x.icao_code == new_aircraft.icao_code for x in aircrafts):
                        aircrafts.append(Aircraft(data[x]))
        return render_template("public/alerts.html", form=form, aircraftForm=aircraftForm, aircraftResults=aircrafts, airports=savedAirports)
    return redirect(url_for('main.alerts'))

@main.route("/save-airport/<string:icao_code>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def saveAirport(icao_code):
    try:
        response = requests.get(f'https://airlabs.co/api/v9/suggest?q={icao_code}&api_key={current_app.config["AIR_LABS_API_KEY"]}')

        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        response = response.json()
        savedAirports.append(Airport(response["response"]["airports"][0]))

    #scraper = FlightAwareScraper()
    #scraper.getAirportData(response["response"]["airports"][0]['icao_code'])
    return redirect(url_for('main.alerts'))

@main.route("/save-aircraft/<string:icao_code>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def saveAircraft(icao_code):
    with open("app/data/aircrafts.json", "r", encoding="utf8") as read_file:
            data = json.load(read_file)
            aircraftt = next((x for x in data if x['icaoCode'] == icao_code), None)
            print(aircraftt)
            Aircraft(data[x])
    return redirect(url_for('main.alerts'))
