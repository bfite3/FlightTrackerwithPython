import smtplib
import requests
import os

MY_EMAIL = os.environ['MY_EMAIL']
MY_PASSWORD = os.environ['EMAIL_PASSWORD']
SHEETY_ENDPOINT_GET = "https://api.sheety.co/7a6327fc6ea294ff861d1c31744358c7/copyOfFlightDeals/users"

class NotificationManager:
    # This class is responsible for sending notifications with the deal flight details.
    def __init__(self):
        self.from_addrs = MY_EMAIL
        self.sheety_endpoint_get = SHEETY_ENDPOINT_GET

    # This function will email the flight data to the desired users on the "users" tab of the Google Sheet
    def email_flight_deal(self, flight_info, layover_flight_found):
        self.get_email_list()
        for email_dict in self.email_list:
            price = flight_info["price"]
            from_city = flight_info["from_city"]
            from_iata = flight_info["from_iata"]
            to_city = flight_info["to_city"]
            to_iata = flight_info["to_iata"]
            leave_date = flight_info["leave_date"]
            return_date = flight_info["return_date"]
            if not layover_flight_found:
                with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
                    connection.starttls()
                    connection.login(user=MY_EMAIL, password=MY_PASSWORD)
                    connection.sendmail(
                        from_addr=self.from_addrs,
                        to_addrs=email_dict["email"],
                        msg=f"Subject:Flight Found\n\nLow price alert! Only ${price} to fly from {from_city}-{from_iata} to {to_city}-{to_iata}, from {leave_date} to {return_date}")
                print(f"Direct flight found for {to_city} emailed.")
            else:
                stopover_city = flight_info["stop_over_city"]
                stopover_iata = flight_info["stop_over_iata"]
                with smtplib.SMTP("smtp.gmail.com") as connection:
                    connection.starttls()
                    connection.login(user=MY_EMAIL, password=MY_PASSWORD)
                    connection.sendmail(
                        from_addr=self.from_addrs,
                        to_addrs=email_dict["email"],
                        msg=f"Subject:Flight Found\n\nLow price alert! Only ${price} to fly from {from_city}-{from_iata} to {to_city}-{to_iata}, from {leave_date} to {return_date}.\nFlight has 1 stop over, via {stopover_city}-{stopover_iata}.")
                print(f"Flight with layover for {to_city} found emailed.")

    # This function will retrieve the emails from the users tab of the Google Sheet
    def get_email_list(self):
        sheety_response_get = requests.get(url=self.sheety_endpoint_get)
        sheety_response_get.raise_for_status()
        email_data = sheety_response_get.json()
        self.email_list = email_data["users"]

