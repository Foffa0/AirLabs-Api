class Airport_info():

    def __init__(self, data):
        self.data = data
        try:
            self.name = data["name"]
        except:
            self.name = ""
        try:
            self.iata_code = data["iata_code"]
        except:
            self.iata_code = ""
        try:
            self.icao_code = data["icao_code"]
        except:
            self.icao_code = ""
        try:
            self.country_code = data["country_code"]
        except:
            self.country_code = ""

        