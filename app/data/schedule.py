
class ArrivalOrLanding:
    def __init__(self, flightnumber, icao, aircraft, time, type):
        """
        :param flightnumber: the flightnumber of this flight
        :param aircraft_icao: aircraft type in icao format
        :param aircraft: full aircraft name
        :param time: arrival or departure time as datetime object
        :param type: arrival -->0 or departure -->1
        """
        self.flightnumber = flightnumber
        self.aircraft_icao = icao
        self.aircraft = aircraft
        self.time = time
        self.type = type