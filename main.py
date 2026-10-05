from data_manager import DataManager
from flight_data import FlightData
from flight_search import FlightSearch
from notification_manager import NotificationManager


def main() -> None:
    data_manager = DataManager()
    flight_data = FlightData()
    flight_search = FlightSearch()
    notification_manager = NotificationManager()

    cities = data_manager.get_cities()
    recipient_emails = data_manager.get_user_emails()

    for row_number, city_record in enumerate(
        cities,
        start=2,
    ):
        city_name = str(
            city_record["City"]
        ).strip()

        try:
            iata_code = str(
                city_record["IATACode"]
            ).strip()
            max_price = int(
                city_record["LowestPrice"]
            )

            if not iata_code:
                iata_code = flight_data.get_iata(city_name)

                data_manager.input_iata(
                    row_number=row_number,
                    iata=iata_code,
                )

            layover_flight_found = False

            direct_flight_found = (
                flight_search.search_direct_flights(
                    fly_to=iata_code,
                    max_price=max_price,
                )
            )

            if not direct_flight_found:
                layover_flight_found = (
                    flight_search.search_layover_flights(
                        fly_to=iata_code,
                        max_price=max_price,
                    )
                )

            if direct_flight_found or layover_flight_found:
                flight_info = flight_search.get_flight_info(
                    layover_flight_found
                )

                notification_manager.email_flight_deal(
                    flight_info=flight_info,
                    recipient_emails=recipient_emails,
                    layover_flight_found=layover_flight_found,
                )

        except Exception as error:
            print(
                f"Error processing {city_name}: "
                f"{error}"
            )


if __name__ == "__main__":
    main()