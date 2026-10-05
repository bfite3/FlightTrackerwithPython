import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from flight_search import FlightInfo


load_dotenv()

MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASSWORD = os.environ.get("EMAIL_PASSWORD")

if not MY_EMAIL:
    raise ValueError(
        "MY_EMAIL environment variable is not configured."
    )

if not MY_PASSWORD:
    raise ValueError(
        "EMAIL_PASSWORD environment variable is not configured."
    )


class NotificationManager:
    """Send flight-deal notifications by email."""

    def __init__(self) -> None:
        self.from_address: str = MY_EMAIL

    def email_flight_deal(
        self,
        flight_info: FlightInfo,
        recipient_emails: list[str],
        layover_flight_found: bool,
    ) -> None:
        """Email a flight deal to each configured recipient."""

        price = flight_info["price"]
        from_city = flight_info["from_city"]
        from_iata = flight_info["from_iata"]
        to_city = flight_info["to_city"]
        to_iata = flight_info["to_iata"]
        leave_date = flight_info["leave_date"]
        return_date = flight_info["return_date"]

        message_body = (
            f"Low price alert! Only ${price} to fly from "
            f"{from_city}-{from_iata} to "
            f"{to_city}-{to_iata}, from "
            f"{leave_date} to {return_date}."
        )

        if layover_flight_found:
            stopovers = flight_info.get("stopovers", [])

            if stopovers:
                stopover_text = ", ".join(stopovers)

                message_body += (
                    "\n"
                    f"Flight includes stopover(s) via "
                    f"{stopover_text}."
                )

        with smtplib.SMTP(
            "smtp.gmail.com",
            port=587,
        ) as connection:
            connection.starttls()
            connection.login(
                user=MY_EMAIL,
                password=MY_PASSWORD,
            )

            for recipient_email in recipient_emails:
                message = EmailMessage()
                message["Subject"] = "Flight Deal Found"
                message["From"] = self.from_address
                message["To"] = recipient_email
                message.set_content(message_body)

                connection.send_message(message)

        print(
            f"Flight deal for {to_city} emailed "
            f"to {len(recipient_emails)} recipient(s)."
        )