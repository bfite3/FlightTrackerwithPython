import os

import requests
from dotenv import load_dotenv


load_dotenv()

FLIGHT_IATA_ENDPOINT = (
    "https://api.tequila.kiwi.com/locations/query"
)

KIWI_API_KEY = os.environ.get("KIWI_API_KEY")

if not KIWI_API_KEY:
    raise ValueError(
        "KIWI_API_KEY environment variable is not configured."
    )


class FlightData:
    """Retrieve airport IATA codes from the flight API."""

    def __init__(self) -> None:
        self.flight_iata_endpoint: str = FLIGHT_IATA_ENDPOINT
        self.flight_iata_headers: dict[str, str] = {
            "apikey": KIWI_API_KEY
        }

    def get_iata(self, city: str) -> str:
        """Return the IATA code for a city."""

        flight_iata_params: dict[str, str] = {
            "term": city
        }

        response = requests.get(
            url=self.flight_iata_endpoint,
            params=flight_iata_params,
            headers=self.flight_iata_headers,
            timeout=30,
        )

        response.raise_for_status()

        flight_iata_data = response.json()

        locations = flight_iata_data.get("locations", [])

        if not locations:
            raise ValueError(
                f"No IATA code found for city: {city}"
            )

        return str(locations[0]["code"])