class Airport_info():

    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.iata_code = data["iata_code"]
        self.icao_code = data["icao_code"]
        self.country_code = data["country_code"]

        