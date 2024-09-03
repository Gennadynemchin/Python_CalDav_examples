import base64
import re
import requests
import json
from caldav import DAVClient
from icalendar import Event, vCalAddress, vText
from datetime import datetime, timedelta
from settings.settings import creds


def from_byte_to_dict(tracker_data: bytes) -> dict:
    decoded_string = tracker_data.decode("utf-8")
    pattern = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    corrected_string = re.sub(pattern, r'"\1"', decoded_string)
    output_data = eval(corrected_string)
    return output_data


def create_event(
    creds,
    event_data: dict,
) -> str:
    with DAVClient(
        url=creds.caldav_url,
        username=creds.caldav_username,
        password=creds.caldav_password,
    ) as client:
        calendar_tracker = client.calendar(url=creds.calendar_url)
        event = Event()

        deadline = event_data.get("deadline")
        summary = event_data.get("summary")
        description = event_data.get("description")
        attendees = event_data.get("attendees")

        deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
        event.add("dtstart", deadline_date)
        event.add("dtend", deadline_date + timedelta(days=1))
        event.add("dtstamp", datetime.now())
        event.add("summary", summary)
        event.add("class", "PRIVATE")
        organizer = vCalAddress(f"MAILTO:{creds.organizer}")
        event.add("organizer", organizer)

        if description:
            event.add("description", vText(description))

        if len(attendees) > 0:
            for email in attendees:
                attendee = vCalAddress(f"MAILTO:{email}")
                attendee.params["RSVP"] = vText("TRUE")
                event.add("attendee", attendee)

        created_event = calendar_tracker.add_event(event.to_ical())
        return created_event.url


def save_event_url(issue_key, event_url):
    headers = {
        creds.orgheader: creds.orgid,
        "Authorization": f"OAuth {creds.oauth_token}",
        "Content-Type": "application/json",
    }
    data = json.dumps({creds.event_url_field: event_url})
    response = requests.patch(
        f"https://api.tracker.yandex.net/v2/issues/{issue_key}",
        headers=headers,
        data=data,
    )
    response.raise_for_status()


def main(event, context):
    event_data = base64.b64decode(event["body"])
    tracker_data = from_byte_to_dict(event_data)
    created_event = create_event(
        creds,
        tracker_data,
    )
    save_event_url(tracker_data["task_key"], str(created_event))
