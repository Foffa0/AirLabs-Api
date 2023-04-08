from flask import render_template, Blueprint, redirect, url_for, current_app, flash
from flask_login import current_user
from flask_login import login_required
#from app.models import Recipe
from app import db
from app.models import Alert, Aircraft, Airport
from sqlalchemy import desc
import requests
from requests.exceptions import HTTPError
from app.main.forms import AirportForm, AircraftForm
from app.data.airport import Airport_info
from app.data.aircraft import Aircraft_Info
import json
from app.decorators import check_confirmed
from app.tasks.task import startSchedule


main = Blueprint('main', __name__)

savedAirports = []

@main.route("/")
@main.route("/index")
def index():
    startSchedule()
    return render_template("public/index.html")

@main.route("/alerts", methods=['GET', 'POST'])
@login_required
@check_confirmed
def alerts():
    form = AirportForm()
    aircraftForm = AircraftForm()
    airports = Airport.query.filter_by(user_id=current_user.id)
    aircrafts = Aircraft.query.all()
    alerts = Alert.query.filter_by(user_id=current_user.id).all()
    alerts.sort(key=lambda r: r.time)
    return render_template("public/alerts.html", form=form, aircraftForm=aircraftForm, airports=airports, aircrafts=aircrafts, alerts=alerts)

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
            airportResults = []
            response = response.json()
            for airport in response["response"]["airports"]:
                airportResults.append(Airport_info(airport))
        airports = Airport.query.filter_by(user_id=current_user.id)
        alerts = Alert.query.filter_by(user_id=current_user.id).all()
        alerts.sort(key=lambda r: r.time)
        return render_template("public/alerts.html", form=form, aircraftForm=aircraftForm, airportResults=airportResults, airports=airports, alerts=alerts)


@main.route("/search-aircraft", methods=['GET', 'POST'])
@login_required
@check_confirmed
def searchAircraft():
    form = AirportForm()
    aircraftForm = AircraftForm()
    
    if aircraftForm.validate_on_submit():
        query = aircraftForm.query.data
        aircraftResults = []

        with open("app/data/aircrafts.json", "r", encoding="utf8") as read_file:
            data = json.load(read_file)
            for x, aircraft in enumerate(data):
                # check if engine count or aircraft name is given
                if aircraftForm.search_option.data == 1:
                    new_aircraft = None
                    if aircraft['icaoCode']:
                        if query in aircraft['icaoCode']:
                            new_aircraft = Aircraft_Info(data[x])
                    if query in aircraft['name']:
                        new_aircraft = Aircraft_Info(data[x])
                    elif query in aircraft['manufacturer']:
                        new_aircraft = Aircraft_Info(data[x])

                    if new_aircraft:
                        if not any(y.icao_code == new_aircraft.icao_code for y in aircraftResults):
                            aircraftResults.append(Aircraft_Info(data[x]))
                elif aircraftForm.search_option.data == 2:
                    if aircraft['engineCount'] == int(query):
                        if aircraft['icaoCode'] != None:
                            if not any(y.icao_code == aircraft['icaoCode'] for y in aircraftResults):
                                aircraftResults.append(Aircraft_Info(data[x]))

        airports = Airport.query.filter_by(user_id=current_user.id)
        airport_icao = aircraftForm.airport_icao.data
        aircrafts = Aircraft.query.all()
        alerts = Alert.query.filter_by(user_id=current_user.id).all()
        alerts.sort(key=lambda r: r.time)
        return render_template("public/alerts.html", form=form, aircraftForm=aircraftForm, aircraftResults=aircraftResults, airports=airports, searchAirportIcao=airport_icao, aircrafts=aircrafts, alerts=alerts)
    return redirect(url_for('main.alerts'))

@main.route("/save-airport/<string:icao_code>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def saveAirport(icao_code):
    userAirports = Airport.query.filter_by(user_id=current_user.id)
    for userAirport in userAirports:
        if userAirport.icao == icao_code.upper():
            flash('Airport already on the watchlist!', 'warning')
            return redirect(url_for('main.alerts'))
    try:
        response = requests.get(f'https://airlabs.co/api/v9/suggest?q={icao_code}&api_key={current_app.config["AIR_LABS_API_KEY"]}')
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        response = response.json()["response"]["airports"][0]
        airport = Airport(name=response["name"], icao=response["icao_code"], iata=response["iata_code"], user_id=current_user.id)
        db.session.add(airport)
        db.session.commit()
    return redirect(url_for('main.alerts'))

@main.route("/save-aircraft/<string:icao_code>/<int:airport>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def saveAircraft(icao_code, airport):
    if not Airport.query.get_or_404(airport).user_id == current_user.id:
        flash('Unable to save this aircraft!', 'warning')
        return redirect(url_for('main.alerts'))
    with open("app/data/aircrafts.json", "r", encoding="utf8") as read_file:
        data = json.load(read_file)
        aircraft = next((x for x in data if x['icaoCode'] == icao_code), None)
        userAircrafts = Aircraft.query.filter_by(airport_id=airport)
        for userAircraft in userAircrafts:
            if userAircraft.icao == icao_code.upper():
                flash('Aircraft already on the watchlist!', 'warning')
                return redirect(url_for('main.alerts'))
        db.session.add(Aircraft(name=aircraft['manufacturer'] + " " + aircraft['name'], icao=aircraft['icaoCode'], airport_id=airport, user_id=current_user.id))
        db.session.commit()
    return redirect(url_for('main.alerts'))

@main.route("/delete-airport/<int:id>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def deleteAirport(id):
    airport = Airport.query.get_or_404(id)
    if not airport.user_id == current_user.id:
        flash('Unable to delete this airport!', 'warning')
        return redirect(url_for('main.alerts'))
    aircrafts = Aircraft.query.all()
    for aircraft in aircrafts:
        if aircraft.airport_id == id:
            print("ddd")
            db.session.delete(Aircraft.query.get_or_404(aircraft.id))
            db.session.commit()
    
    db.session.delete(airport)
    db.session.commit()
    return redirect(url_for('main.alerts'))

@main.route("/delete-aircraft/<int:id>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def deleteAircraft(id):
    aircraft = Aircraft.query.get_or_404(id)
    airport = Airport.query.get_or_404(aircraft.airport_id)
    if not airport.user_id == current_user.id:
        flash('Unable to delete this aircraft!', 'warning')
        return redirect(url_for('main.alerts'))
    db.session.delete(aircraft)
    db.session.commit()
    return redirect(url_for('main.alerts'))
