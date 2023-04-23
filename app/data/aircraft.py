class Aircraft_Info():

    def __init__(self, data):
        self.name = data["name"]
        self.icao_code = data["icaoCode"]
        self.manufacturer = data["manufacturer"]
        self.url = data["url"]
        self.tags = list()
        for tag in data["tags"]:
            if tag == "Military": 
                self.tags.append(1)
            if tag == "Experimental": 
                self.tags.append(3)
            if tag == "Prototype": 
                self.tags.append(4)
            if tag == "UAV": 
                self.tags.append(5)
            if tag == "Cancelled": 
                self.tags.append(8)
        if data["aircraftFamily"] == "airship":
            self.tags.append(6)
        elif data["aircraftFamily"] == "helicopter":
            self.tags.append(2)
        elif data["aircraftFamily"] == "glider":
            self.tags.append(7)

    def hasTags(self, tagList):
        '''
        Check if an Aircraft has all of the given filters in its tag attribute.

        :param tagList: List of tags represented by integers
        '''
        skip = False
        for filterElement in tagList:
            if not filterElement in self.tags:
                skip = True
                break
        if not skip:
            return True
        return False