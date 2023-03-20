class Aircraft():

    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.icao_code = data["icaoCode"]
        self.manufacturer = data["manufacturer"]