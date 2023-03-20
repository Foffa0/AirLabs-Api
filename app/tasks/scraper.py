from bs4 import BeautifulSoup
import urllib.request
import http.cookiejar
import lxml
import locale
import calendar
import datetime
import random
locale.setlocale(locale.LC_TIME, "de_DE") #for the 24h time format (for datetime)
from app.config import Config
from flask import current_app
from app.data.schedule import ArrivalOrLanding
import re

class FlightAwareScraper:
    def __init__(self):
        pass

    def getProxy(self):
        proxyList = []
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        source = opener.open('https://free-proxy-list.net/')
        soup = BeautifulSoup(source, 'lxml')
        table = soup.select('.table,.table-striped,.table-bordered')[0]
        table.thead.replace_with('')
        #count the number of proxies
        counter = 0

        for table_cell in table.find_all('tr'):
            if table_cell.find_all('td')[6] == 'yes':
                http = 'https://'
            else:
                http = 'http://'
            proxy = http + table_cell.find_all('td')[0].text + ':' + table_cell.find_all('td')[1].text
            proxyList.append(proxy)
            counter += 1
            if counter == 5:
                break
        return proxyList
        
    global logged_in

    def getAirportData(self, airportCode):
        #proxies
        proxies = self.getProxy()
        logged_in = False
        try:
            source = urllib.request.urlopen('https://de.flightaware.com/')
            soup = BeautifulSoup(source, 'lxml')
            if current_app.config['FLIGHTAWARE_USERNAME'] in soup.body.findAll(text=current_app.config['FLIGHTAWARE_USERNAME']):
                logged_in = True
        except:
            logged_in = False

        if logged_in == False: 
            ########## see: https://github.com/luxzg/Python3/commit/68b780e3ab1402be9e37a8a3f6d06bcea4b6732a#diff-0680ac0627f7a09dfac8ce2d1eed06be
            # your base URL here, will be used for headers and such, with and without https://
            base_url = 'de.flightaware.com'
            https_base_url = 'https://' + base_url
            # here goes URL that's found inside form action='.....'
            authentication_url = https_base_url + '/account/session'
            #! username and password for login
            username = current_app.config['FLIGHTAWARE_USERNAME']
            password = current_app.config['FLIGHTAWARE_PASSWORD']

            headers={"Content-Type":"application/x-www-form-urlencoded",
            "User-agent":"Mozilla/5.0 Chrome/81.0.4044.92",  
            "Host":base_url,
            "Origin":https_base_url,
            "Referer":https_base_url}
            # initiate the cookie jar (using : http.cookiejar and urllib.request)
            cookie_jar = http.cookiejar.CookieJar()

            randomProxy = random.choice(proxies)
            proxy = urllib.request.ProxyHandler({randomProxy.partition(':')[0]: randomProxy})

            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar), proxy)
            urllib.request.install_opener(opener)
            # first a simple request, just to get login page and parse out the token
            request = urllib.request.Request(https_base_url)
            response = urllib.request.urlopen(request)
            contents = response.read()

            soup = BeautifulSoup(contents, 'lxml')
            form = soup.find(id='loginForm')
            token = form.find("input", {"name":"token"})['value']
            # here we craft our payload, it's all the form fields, including HIDDEN fields!
            payload = {
                'token':token,
                'mode':'login',
                'flightaware_username':username,
                'flightaware_password':password
            }
            # now we prepare all we need for login
            #   data - with our payload (user/pass/token) urlencoded and encoded as bytes
            data = urllib.parse.urlencode(payload)
            binary_data = data.encode('UTF-8')
            # and put the URL + encoded data + correct headers into our POST request
            #   btw, despite what I thought it is automatically treated as POST
            request = urllib.request.Request(authentication_url, binary_data, headers)
            response = urllib.request.urlopen(request)

            logout_url = https_base_url + '/account/session/logout/' + token

            logged_in = True


        date = datetime.date.today()

        ### Arrivals ###

        #create request
        # randomProxy = random.choice(proxies)
        # proxy = urllib.request.ProxyHandler({randomProxy.partition(':')[0]: randomProxy})
        # opener = urllib.request.build_opener(proxy)
        # opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        # urllib.request.install_opener(opener)


        #count the offset for the request
        counter = 0

        schedule = []

        while datetime.date.today() + datetime.timedelta(days=7) != date or counter <= 800:

            source = urllib.request.urlopen(f'https://de.flightaware.com/live/airport/{airportCode}/arrivals?;offset={counter};order=actualarrivaltime;sort=ASC')
            print(counter)
            counter += 40
            soup = BeautifulSoup(source, 'lxml')

            arrivals_board = soup.select('.prettyTable,.fullWidth')
            table = arrivals_board[1]
            table.thead.replace_with('')

            # check if table is empty
            if table.find_all('td')[0].has_attr('class'):
                if table.find_all('td')[0]['class'][0] == 'row1':
                    break

            # iterate through the whole table
            for table_cell in table.find_all('tr'):
                # get date from the weekday in the table
                if table_cell.find_all('td')[4].text.startswith(calendar.day_abbr[date.weekday()]):
                    date = date
                elif table_cell.find_all('td')[4].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=1)).weekday()]):
                    date = date + datetime.timedelta(days=1)
                elif table_cell.find_all('td')[4].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=2)).weekday()]):
                    date = date + datetime.timedelta(days=2)
                elif table_cell.find_all('td')[4].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=3)).weekday()]):
                    date = date + datetime.timedelta(days=3)
                else:
                    continue

                # convert the date and the time from the table to unix timecode
                date_format = datetime.datetime.strptime(str(date)+ ", " + re.search(r'\d{2}:\d{2}', table_cell.find_all('td')[4].text).group(), "%Y-%m-%d, %H:%M")
                unix_time = datetime.datetime.timestamp(date_format)
                schedule.append(ArrivalOrLanding(table_cell.find_all('td')[0].text, table_cell.find_all('td')[1].span.get("title"), table_cell.find_all('td')[1].text, unix_time, 0))
                
            
            if datetime.date.today() + datetime.timedelta(days=7) == date or counter >= 800:
                break

        ### planned Arrivals ###

        #count the offset for the request
        counter = 0
        date = datetime.date.today()

        while datetime.date.today() + datetime.timedelta(days=7) != date or counter <= 800:
            #create request
            a_source = urllib.request.urlopen(f'https://de.flightaware.com/live/airport/{airportCode}/enroute?;offset={counter};order=estimatedarrivaltime;sort=ASC')
            print(counter)
            counter += 40
            a_soup = BeautifulSoup(a_source, 'lxml')

            p_arrivals_board = a_soup.select('.prettyTable,.fullWidth')
            table = p_arrivals_board[1]
            table.thead.replace_with('')

            # check if table is empty
            if table.find_all('td')[0].has_attr('class'):
                if table.find_all('td')[0]['class'][0] == 'row1':
                    break

            # iterate through the whole table
            for table_cell in table.find_all('tr'):
                # get date from the weekday in the table
                if table_cell.find_all('td')[5].text.startswith(calendar.day_abbr[date.weekday()]):
                    date = date
                elif table_cell.find_all('td')[5].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=1)).weekday()]):
                    date = date + datetime.timedelta(days=1)
                elif table_cell.find_all('td')[5].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=2)).weekday()]):
                    date = date + datetime.timedelta(days=2)
                elif table_cell.find_all('td')[5].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=3)).weekday()]):
                    date = date + datetime.timedelta(days=3)
                else:
                    continue

                # convert the date and the time from the table to unix timecode
                date_format = datetime.datetime.strptime(str(date) + ", " + re.search(r'\d{2}:\d{2}', table_cell.find_all('td')[5].text).group(), "%Y-%m-%d, %H:%M")
                unix_time = datetime.datetime.timestamp(date_format)
                schedule.append(ArrivalOrLanding(table_cell.find_all('td')[0].text, table_cell.find_all('td')[1].span.get("title"), table_cell.find_all('td')[1].text, unix_time, 0))
                

            if datetime.date.today() + datetime.timedelta(days=7) == date or counter >= 800:
                break


        ### Departures ###

        #count the offset for the request
        counter = 0
        date = datetime.date.today()

        while datetime.date.today() + datetime.timedelta(days=7) != date or counter <= 800:
            #create request
            source = urllib.request.urlopen(f'https://de.flightaware.com/live/airport/{airportCode}/departures?;offset={counter};order=actualdeparturetime;sort=ASC')
            counter += 40
            soup = BeautifulSoup(source, 'lxml')

            departures_board = soup.select('.prettyTable,.fullWidth')
            table = departures_board[1]
            table.thead.replace_with('')

            # check if table is empty
            if table.find_all('td')[0].has_attr('class'):
                if table.find_all('td')[0]['class'][0] == 'row1':
                    break

            # iterate through the whole table
            for table_cell in table.find_all('tr'):
                # get date from the weekday in the table
                if table_cell.find_all('td')[3].text.startswith(calendar.day_abbr[date.weekday()]):
                    date = date
                elif table_cell.find_all('td')[3].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=1)).weekday()]):
                    date = date + datetime.timedelta(days=1)
                elif table_cell.find_all('td')[3].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=2)).weekday()]):
                    date = date + datetime.timedelta(days=2)
                elif table_cell.find_all('td')[3].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=3)).weekday()]):
                    date = date + datetime.timedelta(days=3)
                else:
                    continue

                # convert the date and the time from the table to unix timecode
                date_format = datetime.datetime.strptime(str(date) + ", " + re.search(r'\d{2}:\d{2}', table_cell.find_all('td')[3].text).group(), "%Y-%m-%d, %H:%M")
                unix_time = datetime.datetime.timestamp(date_format)
                schedule.append(ArrivalOrLanding(table_cell.find_all('td')[0].text, table_cell.find_all('td')[1].span.get("title"), table_cell.find_all('td')[1].text, unix_time, 1))
                
                if datetime.date.today() + datetime.timedelta(days=7):
                    break


        ### planned Departures ###

        #count the offset for the request
        counter = 0
        date = datetime.date.today()

        while datetime.date.today() + datetime.timedelta(days=7) != date or counter <= 800:
            #create request
            source = urllib.request.urlopen(f'https://de.flightaware.com/live/airport/{airportCode}/scheduled?;offset={counter};order=filed_departuretime;sort=ASC')
            counter += 40
            soup = BeautifulSoup(source, 'lxml')

            p_departures_board = soup.select('.prettyTable,.fullWidth')
            table = p_departures_board[1]
            table.thead.replace_with('')

            # check if table is empty
            if table.find_all('td')[0].has_attr('class'):
                if table.find_all('td')[0]['class'][0] == 'row1':
                    break

            # iterate through the whole table
            for table_cell in table.find_all('tr'):
                # get date from the weekday in the table
                if table_cell.find_all('td')[3].text.startswith(calendar.day_abbr[date.weekday()]):
                    date = date
                elif table_cell.find_all('td')[3].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=1)).weekday()]):
                    date = date + datetime.timedelta(days=1)
                elif table_cell.find_all('td')[3].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=2)).weekday()]):
                    date = date + datetime.timedelta(days=2)
                elif table_cell.find_all('td')[3].text.startswith(calendar.day_abbr[(date + datetime.timedelta(days=3)).weekday()]):
                    date = date + datetime.timedelta(days=3)
                else:
                    continue

                # convert the date and the time from the table to unix timecode
                date_format = datetime.datetime.strptime(str(date) + ", " + re.search(r'\d{2}:\d{2}', table_cell.find_all('td')[3].text).group(), "%Y-%m-%d, %H:%M")
                unix_time = datetime.datetime.timestamp(date_format)
                schedule.append(ArrivalOrLanding(table_cell.find_all('td')[0].text, table_cell.find_all('td')[1].span.get("title"), table_cell.find_all('td')[1].text, unix_time, 1))
                
                if datetime.date.today() + datetime.timedelta(days=7):
                    break
        print(schedule)
