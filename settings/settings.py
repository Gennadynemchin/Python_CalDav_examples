import os
from dotenv import load_dotenv
from urllib.parse import urljoin


load_dotenv()


class Credentials:
    def __init__(self):
        self.caldav_url = os.getenv("CALDAV_URL")
        self.caldav_username = os.getenv("CALDAV_USERNAME")
        self.caldav_password = os.getenv("CALDAV_PASSWORD")
        self.calendar_url = urljoin(self.caldav_url, os.getenv("CALENDAR_URL"))
        self.organizer = os.getenv("ORGANIZER")


creds = Credentials()
