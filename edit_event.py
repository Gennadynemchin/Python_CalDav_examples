import os
import base64
import json
from caldav import DAVClient
from dotenv import load_dotenv
from icalendar import vCalAddress
from datetime import datetime, timedelta


load_dotenv()


def edit_event(
    event_data: dict,
):
    with DAVClient(
        url=os.getenv("CALDAV_URL"),
        username=os.getenv("CALDAV_USERNAME"),
        password=os.getenv("CALDAV_PASSWORD"),
    ) as client:
        event = client.calendar(url=os.getenv("CALENDAR_URL")).event_by_url(
            event_data["event_url"]
        )
        new_date = event_data.get("deadline")
        attendee = event_data.get("attendee")
        event.load()
        event.vobject_instance.vevent.dtstamp.value = datetime.now()

        organizer = vCalAddress(f"MAILTO:{os.getenv('CALDAV_USERNAME')}")
        event.icalendar_component["organizer"] = organizer

        if new_date:
            new_date_formatted = datetime.strptime(new_date, "%Y-%m-%d").date()
            event.vobject_instance.vevent.dtstart.value = new_date_formatted
            event.vobject_instance.vevent.dtend.value = new_date_formatted + timedelta(
                days=1
            )
        if attendee:
            new_attendee = vCalAddress(f"MAILTO:{attendee}")
            event.icalendar_component["attendee"] = new_attendee
        event.save()
        return event


def main(event, context):
    tracker_data = json.loads(base64.b64decode(event["body"]))
    edit_event(tracker_data)
