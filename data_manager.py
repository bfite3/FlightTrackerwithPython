import os
from typing import Any

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials


load_dotenv()

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_FILE = os.environ.get(
    "GOOGLE_CREDENTIALS_FILE"
)

if not GOOGLE_SHEET_ID:
    raise ValueError(
        "GOOGLE_SHEET_ID environment variable is not configured."
    )

if not GOOGLE_CREDENTIALS_FILE:
    raise ValueError(
        "GOOGLE_CREDENTIALS_FILE environment variable is not configured."
    )


class DataManager:
    """Read and update flight-tracking data in Google Sheets."""

    def __init__(self) -> None:
        scopes: list[str] = [
            "https://www.googleapis.com/auth/spreadsheets"
        ]

        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=scopes,
        )

        client = gspread.authorize(credentials)

        self.spreadsheet = client.open_by_key(
            GOOGLE_SHEET_ID
        )

        self.prices_worksheet = self.spreadsheet.worksheet(
            "prices"
        )

    def get_cities(self) -> list[dict[str, Any]]:
        """Return destination records from the prices worksheet."""

        return self.prices_worksheet.get_all_records()

    def get_user_emails(self) -> list[str]:
        """Return recipient email addresses from the users worksheet."""

        users_worksheet = self.spreadsheet.worksheet(
            "users"
        )

        user_records = users_worksheet.get_all_records()

        return [
            str(user_record["Email"]).strip()
            for user_record in user_records
            if str(user_record["Email"]).strip()
        ]

    def input_iata(
        self,
        row_number: int,
        iata: str,
    ) -> None:
        """Update the IATA code for a destination row."""

        self.prices_worksheet.update_cell(
            row_number,
            2,
            iata,
        )