import requests

SHEETY_ENDPOINT_GET = "https://api.sheety.co/7a6327fc6ea294ff861d1c31744358c7/copyOfFlightDeals/prices"
SHEETY_ENDPOINT_PUT = "https://api.sheety.co/7a6327fc6ea294ff861d1c31744358c7/copyOfFlightDeals/prices"


class DataManager:
    # This class is responsible for talking to the Google Sheet.
    def __init__(self):
        self.sheety_endpoint_get = SHEETY_ENDPOINT_GET
        self.sheety_endpoint_put = SHEETY_ENDPOINT_PUT

    # This function will get the city name(s) from the Google Sheet
    def get_cities(self):
        sheety_response_get = requests.get(url=self.sheety_endpoint_get)
        sheety_response_get.raise_for_status()
        flight_data = sheety_response_get.json()
        self.flight_list = flight_data["prices"]

    # This function will input the IATA code(s) if they aren't already in the Google Sheet
    def input_iata(self, id, iata):
        sheety_put_config = {
            "price": {
                "iataCode": iata,
            }
        }

        sheety_response_put = requests.put(url=f"{self.sheety_endpoint_put}/{id}", json=sheety_put_config)
        sheety_response_put.raise_for_status()
