# Flight Tracker with Python

A Python-based flight price tracking application that reads destination and pricing targets from Google Sheets, searches for qualifying round-trip flights, and sends email alerts when a matching deal is found.

The project integrates the Google Sheets API, a flight-search API, and Gmail SMTP to create an automated workflow for monitoring airfare against user-defined price thresholds.

## Features

- Reads destination cities and target prices from Google Sheets
- Retrieves and stores missing airport IATA codes
- Searches for direct round-trip flights
- Falls back to flights with stopovers when no direct flight is available
- Supports multiple stopovers in returned itineraries
- Identifies outbound and return-trip dates from route data
- Sends flight-deal alerts by email
- Supports multiple email recipients
- Uses environment variables for configuration and credentials
- Continues processing remaining destinations if one destination fails

## Project Architecture

```text
Google Sheets
     |
     v
DataManager
     |
     +----> Destination cities
     +----> Target prices
     +----> Recipient emails
     |
     v
FlightData
     |
     +----> Retrieve missing IATA codes
     |
     v
FlightSearch
     |
     +----> Direct flight search
     |
     +----> Layover flight search
     |
     +----> Route and stopover parsing
     |
     v
NotificationManager
     |
     v
Gmail SMTP
     |
     v
Email flight alerts
```

## Technologies

- Python
- Google Sheets API
- gspread
- Google service accounts
- Requests
- python-dotenv
- python-dateutil
- Gmail SMTP
- REST APIs

## Project Structure

```text
FlightTrackerwithPython/
├── data_manager.py
├── flight_data.py
├── flight_search.py
├── main.py
├── notification_manager.py
├── requirements.txt
├── .env.example
└── .gitignore
```

### `main.py`

Coordinates the application workflow.

It:

1. Loads destination and recipient data from Google Sheets
2. Retrieves missing IATA codes
3. Searches for direct flights
4. Searches for flights with stopovers when necessary
5. Builds flight information
6. Sends email notifications for qualifying deals
7. Continues to the next destination if an individual search fails

### `data_manager.py`

Handles communication with Google Sheets.

Responsibilities include:

- Reading destination cities
- Reading target prices
- Reading recipient email addresses
- Updating missing IATA codes in the spreadsheet

Authentication is handled through a Google Cloud service account.

### `flight_data.py`

Retrieves airport IATA codes from the flight API.

If a destination in Google Sheets does not already contain an IATA code, the application queries the API and writes the returned code back to the spreadsheet.

### `flight_search.py`

Handles flight-search logic.

Responsibilities include:

- Building API request parameters
- Searching for direct flights
- Searching for flights with stopovers
- Parsing flight API responses
- Determining outbound and return-trip dates
- Identifying intermediate stopovers
- Returning structured flight information

The search currently checks flights from the configured origin airport for travel beginning within the next six months.

Qualifying flights must also meet the maximum price configured for the destination in Google Sheets.

### `notification_manager.py`

Handles email notifications using Gmail SMTP.

When a qualifying flight is found, the application sends an email containing:

- Origin city and airport
- Destination city and airport
- Flight price
- Departure date
- Return date
- Stopover information, when applicable

## Google Sheets Configuration

The application expects a Google Sheet containing two worksheets.

### `prices`

Example:

| City | IATACode | LowestPrice |
| --- | --- | ---: |
| Seattle | SEA | 150 |
| Miami | MIA | 150 |
| San Francisco | SFO | 200 |
| Berlin | BER | 1000 |

`IATACode` may initially be blank. When possible, the application retrieves the code from the flight API and updates the worksheet automatically.

### `users`

Example:

| Email |
| --- |
| example@email.com |

Each email address in this worksheet receives qualifying flight-deal notifications.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/bfite3/FlightTrackerwithPython.git
cd FlightTrackerwithPython
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Google Sheets access

Create a Google Cloud service account with access to the Google Sheets API.

Download the service-account credentials file and store it locally, for example:

```text
credentials/google-service-account.json
```

Share the target Google Sheet with the service account's email address.

The `credentials/` directory is excluded from Git and should never be committed.

### 5. Create the environment file

Copy:

```text
.env.example
```

to:

```text
.env
```

Then provide the required values:

```env
KIWI_API_KEY=
MY_EMAIL=
EMAIL_PASSWORD=
GOOGLE_SHEET_ID=
GOOGLE_CREDENTIALS_FILE=credentials/google-service-account.json
ORIGIN_IATA=
```

### 6. Run the application

```bash
python main.py
```

## Search Behavior

For each destination, the application first searches for a direct round-trip flight that satisfies the configured maximum price.

If no direct flight is found, it performs another search allowing stopovers.

Search parameters currently include:

- Round-trip flights
- User-configured origin airport
- Destination-specific maximum price
- Travel beginning within the next six months
- Trips lasting between 7 and 28 nights
- USD pricing
- Direct-flight preference with layover fallback

## Error Handling

Each destination is processed independently.

If an API request, spreadsheet operation, or other destination-specific step fails, the application reports the error and continues processing the remaining destinations rather than terminating the entire run.

## Security

Sensitive configuration is stored outside the source code using environment variables.

The following are excluded from version control:

```text
.env
credentials/
.venv/
.idea/
__pycache__/
*.pyc
```

API keys, email credentials, Google service-account credentials, and other secrets should never be committed to the repository.


## AI-Assisted Refactoring

This project was originally built as a smaller flight-tracking application and was later refactored with the assistance of ChatGPT.

AI was used as a development aid to review the existing code, identify maintainability and security issues, explain refactoring options, and suggest incremental improvements. The changes were reviewed, implemented, and tested by the developer rather than applied as an automated rewrite.

The refactoring work included:

- Replacing the previous Sheety integration with direct Google Sheets API access
- Moving API keys, email credentials, spreadsheet configuration, and the origin airport into environment variables
- Adding a Google Cloud service account for Google Sheets authentication
- Introducing `TypedDict` for structured flight information
- Supporting multiple stopovers instead of assuming a single layover
- Improving return-date parsing from the flight itinerary
- Reusing a single SMTP connection when emailing multiple recipients
- Removing hidden coupling between direct-flight and layover searches
- Extracting reusable helpers for API parameter construction, requests, response parsing, and flight-detail storage
- Adding per-destination error handling so one failed search does not stop the entire run
- Improving type hints, naming, formatting, dependency management, and repository security practices

The refactoring process was intentionally incremental. Each major change was tested against the live integrations before moving to the next step, including Google Sheets access, flight searches, itinerary parsing, and email delivery.

Using AI in this way supported code review and learning while keeping implementation decisions, testing, and final validation developer-controlled.

## Notes

This project uses a legacy flight-search API integration. API availability, authentication requirements, or endpoint behavior may change over time.

The project is intended to demonstrate:

- Python automation
- REST API integration
- Google Sheets integration
- External service authentication
- Data parsing and transformation
- Error handling
- Email automation
- Modular application design

## Future Improvements

Potential enhancements include:

- Scheduled execution using a job scheduler or cloud service
- Logging instead of console output
- More specific exception handling
- Automated tests
- Retry logic for transient API failures
- More detailed flight itinerary information
- HTML-formatted notification emails
- Deployment to a cloud environment
