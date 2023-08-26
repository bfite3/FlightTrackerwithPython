import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

FLIGHT_SEARCHER_ENDPOINT = "https://tequila-api.kiwi.com/v2/search"
FLIGHT_SEARCHER_TOKEN = "43xOu4w4SvJypJgv2ey-eXzV5wBWRYSa"
FLY_FROM = "CLE"


class FlightSearch:
    # This class is responsible for talking to the Flight Search API.
    def __init__(self):
        self.flight_searcher_endpoint = FLIGHT_SEARCHER_ENDPOINT
        self.flight_searcher_headers = {"apikey": FLIGHT_SEARCHER_TOKEN}

    # This function will search for a direct flight based off desired params
    def search_direct_flights(self, fly_to, max_price):
        self.flight_searcher_params = {
            "fly_from": FLY_FROM,
            "fly_to": fly_to,
            # "fly_to": "ATL",
            "date_from": (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"),
            "date_to": (datetime.now() + relativedelta(months=6)).strftime("%d/%m/%Y"),
            "ret_from_diff_city": "false",
            "ret_to_diff_city": "false",
            "curr": "USD",
            "price_to": max_price,
            # "price_to": 200,
            "max_stopovers": 0,
            "one_for_city": 1,
            "nights_in_dst_from": 7,
            "nights_in_dst_to": 28,
            "flight_type": "round",
        }

        flight_searcher_response = requests.get(url=self.flight_searcher_endpoint, params=self.flight_searcher_params,
                                                headers=self.flight_searcher_headers)
        flight_searcher_response.raise_for_status()
        flight_searcher_data = flight_searcher_response.json()

        try:
            self.from_iata = flight_searcher_data["data"][0]["flyFrom"]
            self.from_city = flight_searcher_data["data"][0]["cityFrom"]
            self.to_iata = flight_searcher_data["data"][0]["flyTo"]
            self.to_city = flight_searcher_data["data"][0]["cityTo"]
            self.price = flight_searcher_data["data"][0]["price"]
            self.leave_date = \
            (flight_searcher_data["data"][0]["route"][0]["local_departure"]).replace("T", " ").split()[0]
            self.return_date = flight_searcher_data["data"][0]["route"][1]["local_departure"].replace("T", " ").split()[
                0]
        except IndexError:
            print(f"No direct flights found to {fly_to} for under max price. Searching flights with a layover.")
            return False
        else:
            return True

    # This function will search for a flight with a layover with desired params
    # Max stopovers is based off stops, 0=direct 3=four stops, two stops there two stops back
    def search_layover_flights(self, fly_to):
        self.flight_searcher_params["max_stopovers"] = 3
        flight_searcher_response = requests.get(url=self.flight_searcher_endpoint, params=self.flight_searcher_params,
                                                headers=self.flight_searcher_headers)
        flight_searcher_response.raise_for_status()
        flight_searcher_data = flight_searcher_response.json()
        try:
            self.from_iata = flight_searcher_data["data"][0]["flyFrom"]
            self.from_city = flight_searcher_data["data"][0]["cityFrom"]
            self.to_iata = flight_searcher_data["data"][0]["flyTo"]
            self.to_city = flight_searcher_data["data"][0]["cityTo"]
            self.price = flight_searcher_data["data"][0]["price"]
            self.leave_date = \
            (flight_searcher_data["data"][0]["route"][0]["local_departure"]).replace("T", " ").split()[0]
            self.return_date = flight_searcher_data["data"][0]["route"][3]["local_departure"].replace("T", " ").split()[
                0]
            self.stopover_city = flight_searcher_data["data"][0]["route"][0]["cityTo"]
            self.stopover_iata = flight_searcher_data["data"][0]["route"][0]["cityCodeTo"]
        except IndexError:
            print(f"No flights found to {fly_to} with a layover for under max price.")
            return False
        else:
            return True

    # This function will build the flight info
    def get_flight_info(self, layover_flight):
        flight_info = {
            "from_iata": self.from_iata,
            "from_city": self.from_city,
            "to_iata": self.to_iata,
            "to_city": self.to_city,
            "price": self.price,
            "leave_date": self.leave_date,
            "return_date": self.return_date,
        }
        if layover_flight:
            flight_info["stop_over_city"] = self.stopover_city
            flight_info["stop_over_iata"] = self.stopover_iata

        return flight_info

