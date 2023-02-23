from flask import render_template, Blueprint, redirect, url_for
from flask_login import current_user
from flask_login import login_required
#from app.models import Recipe
#from app import db
import requests
from requests.exceptions import HTTPError
from app.main.forms import AirportForm
from app.data.airport import Airport

main = Blueprint('main', __name__)

savedAirports = []

@main.route("/")
@main.route("/index")
def index():
    # try:
    #     response = requests.get('https://airlabs.co/api/v9/flights?arr_icao=EDDN&api_key=')

    #     # If the response was successful, no Exception will be raised
    #     response.raise_for_status()
    # except HTTPError as http_err:
    #     print(f'HTTP error occurred: {http_err}')  # Python 3.6
    # except Exception as err:
    #     print(f'Other error occurred: {err}')  # Python 3.6
    # else:
    #     print(response.content)
    return render_template("public/index.html")

@main.route("/alerts", methods=['GET', 'POST'])
def alerts():
    form = AirportForm()
    if form.validate_on_submit():
        query = form.query.data
        try:
            response = requests.get(f'https://airlabs.co/api/v9/suggest?q={query}&api_key=')

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
            print(airports)
            return render_template("public/alerts.html", form=form, airportResults=airports)

    return render_template("public/alerts.html", form=form, airports=savedAirports)

@main.route("/save-airport/<string:icao_code>", methods=['GET', 'POST'])
def saveAirport(icao_code):
    try:
        response = requests.get(f'https://airlabs.co/api/v9/suggest?q={icao_code}&api_key=')

        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        response = response.json()
        savedAirports.append(Airport(response["response"]["airports"][0]))
    return redirect(url_for('main.alerts'))