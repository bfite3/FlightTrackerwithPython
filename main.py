from data_manager import DataManager
from flight_data import FlightData
from flight_search import FlightSearch
from notification_manager import NotificationManager

data_manager = DataManager()
flight_data = FlightData()
flight_search = FlightSearch()
notification_manager = NotificationManager()

# Get cities from Google Sheet
data_manager.get_cities()
# Loop through cities
for city_dict in data_manager.flight_list:
    # Get IATA code from flight api
    iata_code = flight_data.get_iata(city_dict["city"])
    # If there isn't already an IATA code in the Google Sheet then add it
    if len(city_dict["iataCode"]) < 1:
        data_manager.input_iata(id=city_dict["id"], iata=iata_code)
    # Set this to false, so it can be set to true later on if no direct flight found
    layover_flight_found = False
    # Return true if direct flight found else return false
    direct_flight_found = flight_search.search_direct_flights(fly_to=iata_code, max_price=city_dict["lowestPrice"])
    # If direct flight found is false then try to find flight with layover
    if not direct_flight_found:
        layover_flight_found = flight_search.search_layover_flights(fly_to=iata_code)
    # If any type of flight was found get the data then email it
    if direct_flight_found or layover_flight_found:
        flight_info = flight_search.get_flight_info(layover_flight_found)
        notification_manager.email_flight_deal(flight_info, layover_flight_found)
