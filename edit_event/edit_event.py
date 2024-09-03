import base64
import re
from caldav import DAVClient
from icalendar import vCalAddress, vText
from datetime import datetime, timedelta
from settings.settings import creds, Credentials


def from_byte_to_dict(tracker_data: bytes) -> dict:
    decoded_string = tracker_data.decode("utf-8")
    pattern = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    corrected_string = re.sub(pattern, r'"\1"', decoded_string)
    output_data = eval(corrected_string)
    return output_data


def edit_event(
    creds: Credentials,
    event_data: dict,
):
    with DAVClient(
        url=creds.caldav_url,
        username=creds.caldav_username,
        password=creds.caldav_password,
    ) as client:
        event = client.calendar(url=creds.calendar_url).event_by_url(
            event_data["event_url"]
        )
        new_date = event_data.get("deadline")
        attendees = event_data.get("attendees")
        event.load()
        event.vobject_instance.vevent.dtstamp.value = datetime.now()

        organizer = vCalAddress(f"MAILTO:{creds.organizer}")
        event.icalendar_component["organizer"] = organizer

        if new_date:
            new_date_formatted = datetime.strptime(new_date, "%Y-%m-%d").date()
            event.vobject_instance.vevent.dtstart.value = new_date_formatted
            event.vobject_instance.vevent.dtend.value = new_date_formatted + timedelta(
                days=1
            )

        if attendees:
            new_attendees = []
            for attendee in attendees:
                new_attendee = vCalAddress(f"MAILTO:{attendee}")
                new_attendee.params["RSVP"] = vText("TRUE")
                new_attendees.append(new_attendee)
            event.icalendar_component["attendee"] = new_attendees

        event.save()
        return event


def main(event, context):
    event_data = base64.b64decode(event["body"])
    tracker_data = from_byte_to_dict(event_data)
    edit_event(creds, tracker_data)
