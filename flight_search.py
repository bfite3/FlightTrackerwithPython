import os
from datetime import datetime, timedelta
from typing import Any, NotRequired, TypedDict

import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv


load_dotenv()

FLIGHT_SEARCHER_ENDPOINT = (
    "https://tequila-api.kiwi.com/v2/search"
)

ORIGIN_IATA = os.environ.get("ORIGIN_IATA")
KIWI_API_KEY = os.environ.get("KIWI_API_KEY")

if not ORIGIN_IATA:
    raise ValueError(
        "ORIGIN_IATA environment variable is not configured."
    )

if not KIWI_API_KEY:
    raise ValueError(
        "KIWI_API_KEY environment variable is not configured."
    )


class FlightInfo(TypedDict):
    from_iata: str
    from_city: str
    to_iata: str
    to_city: str
    price: float
    leave_date: str
    return_date: str
    stopovers: NotRequired[list[str]]


class FlightSearch:
    """Search for qualifying flights using the flight API."""

    def __init__(self) -> None:
        self.flight_searcher_endpoint: str = (
            FLIGHT_SEARCHER_ENDPOINT
        )

        self.flight_searcher_headers: dict[str, str] = {
            "apikey": KIWI_API_KEY
        }

        self.from_iata: str = ""
        self.from_city: str = ""
        self.to_iata: str = ""
        self.to_city: str = ""
        self.price: float = 0.0
        self.leave_date: str = ""
        self.return_date: str = ""
        self.stopovers: list[str] = []

    def _build_search_params(
        self,
        fly_to: str,
        max_price: int,
        max_stopovers: int,
    ) -> dict[str, str | int]:
        """Build flight-search request parameters."""

        return {
            "fly_from": ORIGIN_IATA,
            "fly_to": fly_to,
            "date_from": (
                datetime.now() + timedelta(days=1)
            ).strftime("%d/%m/%Y"),
            "date_to": (
                datetime.now() + relativedelta(months=6)
            ).strftime("%d/%m/%Y"),
            "ret_from_diff_city": "false",
            "ret_to_diff_city": "false",
            "curr": "USD",
            "price_to": max_price,
            "max_stopovers": max_stopovers,
            "one_for_city": 1,
            "nights_in_dst_from": 7,
            "nights_in_dst_to": 28,
            "flight_type": "round",
        }

    def _search_flights(
        self,
        fly_to: str,
        max_price: int,
        max_stopovers: int,
    ) -> list[dict[str, Any]]:
        """Send a flight search request and return matching flights."""

        search_params = self._build_search_params(
            fly_to=fly_to,
            max_price=max_price,
            max_stopovers=max_stopovers,
        )

        response = requests.get(
            url=self.flight_searcher_endpoint,
            params=search_params,
            headers=self.flight_searcher_headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json().get("data", [])

    def search_direct_flights(
        self,
        fly_to: str,
        max_price: int,
    ) -> bool:
        """Search for a direct round-trip flight."""

        flight_data = self._search_flights(
            fly_to=fly_to,
            max_price=max_price,
            max_stopovers=0,
        )

        if not flight_data:
            print(
                f"No direct flights found to {fly_to} "
                "for under max price. "
                "Searching flights with a layover."
            )
            return False

        flight = flight_data[0]

        self._store_flight_details(flight)

        return True

    def search_layover_flights(
        self,
        fly_to: str,
        max_price: int,
    ) -> bool:
        """Search for a round-trip flight with stopovers."""

        flight_data = self._search_flights(
            fly_to=fly_to,
            max_price=max_price,
            max_stopovers=3,
        )

        if not flight_data:
            print(
                f"No flights found to {fly_to} "
                "with a layover for under max price."
            )
            return False

        flight = flight_data[0]

        route = self._store_flight_details(flight)

        for segment in route:
            stopover_iata = str(segment["flyTo"])
            stopover_city = str(segment["cityTo"])

            if stopover_iata not in {
                self.from_iata,
                self.to_iata,
            }:
                stopover = (
                    f"{stopover_city}-{stopover_iata}"
                )

                if stopover not in self.stopovers:
                    self.stopovers.append(stopover)

        return True

    def get_flight_info(
        self,
        layover_flight: bool,
    ) -> FlightInfo:
        """Return the flight details used for notification."""

        flight_info: FlightInfo = {
            "from_iata": self.from_iata,
            "from_city": self.from_city,
            "to_iata": self.to_iata,
            "to_city": self.to_city,
            "price": self.price,
            "leave_date": self.leave_date,
            "return_date": self.return_date,
        }

        if layover_flight:
            flight_info["stopovers"] = self.stopovers

        return flight_info

    @staticmethod
    def _get_trip_dates(
        route: list[dict[str, Any]],
    ) -> tuple[str, str]:
        """Return the outbound and return-trip departure dates."""

        leave_date = str(
            route[0]["local_departure"]
        ).split("T")[0]

        return_segments = [
            segment
            for segment in route
            if segment.get("return") == 1
        ]

        if not return_segments:
            raise ValueError(
                "Unable to identify the return flight segment."
            )

        return_date = str(
            return_segments[0]["local_departure"]
        ).split("T")[0]

        return leave_date, return_date

    def _store_flight_details(
        self,
        flight: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Store common flight details and return the route."""

        route = flight["route"]

        self.from_iata = str(flight["flyFrom"])
        self.from_city = str(flight["cityFrom"])
        self.to_iata = str(flight["flyTo"])
        self.to_city = str(flight["cityTo"])
        self.price = float(flight["price"])

        self.leave_date, self.return_date = (
            self._get_trip_dates(route)
        )

        self.stopovers = []

        return route