import requests

FLIGHT_IATA_ENDPOINT = "https://api.tequila.kiwi.com/locations/query"
FLIGHT_IATA_TOKEN = "43xOu4w4SvJypJgv2ey-eXzV5wBWRYSa"


class FlightData:
    # This class is responsible for structuring the flight data.
    def __init__(self):
        self.flight_iata_endpoint = FLIGHT_IATA_ENDPOINT
        self.flight_iata_headers = {
            "apikey": FLIGHT_IATA_TOKEN
        }

    # This function will return the IATA code based off the city
    def get_iata(self, city):
        flight_iata_params = {
            "term": city
        }
        flight_iata_response = requests.get(url=self.flight_iata_endpoint, params=flight_iata_params,
                                            headers=self.flight_iata_headers)
        flight_iata_response.raise_for_status()
        flight_iata_data = flight_iata_response.json()

        return flight_iata_data["locations"][0]["code"]