import os
import base64
import json
import requests
from caldav import DAVClient
from icalendar import Event, vCalAddress, vText
from datetime import datetime, timedelta


def create_event(
    event_data: dict,
) -> str:
    with DAVClient(
        url=os.getenv("CALDAV_URL"),
        username=os.getenv("CALDAV_USERNAME"),
        password=os.getenv("CALDAV_PASSWORD"),
    ) as client:
        calendar_tracker = client.calendar(url=os.getenv("CALENDAR_URL"))
        event = Event()

        deadline = event_data.get("deadline")
        summary = event_data.get("summary")
        description = event_data.get("description")
        attendee = event_data.get("attendee")

        deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
        event.add("dtstart", deadline_date)
        event.add("dtend", deadline_date + timedelta(days=1))
        event.add("dtstamp", datetime.now())
        event.add("summary", summary)
        event.add("class", "PRIVATE")
        organizer = vCalAddress(f"MAILTO:{os.getenv('CALDAV_USERNAME')}")
        event.add("organizer", organizer)

        if description:
            event.add("description", vText(description))

        event.add("attendee", vCalAddress(f"MAILTO:{attendee}"))
        created_event = calendar_tracker.add_event(event.to_ical())
        return created_event.url


def save_event_url(issue_key, event_url):
    headers = {
        os.getenv("ORGHEADER"): os.getenv("ORGID"),
        "Authorization": f"OAuth {os.getenv('OAUTH_TOKEN')}",
        "Content-Type": "application/json",
    }
    data = {os.getenv("EVENT_URL_FIELD"): event_url}
    response = requests.patch(
        f"https://api.tracker.yandex.net/v2/issues/{issue_key}",
        headers=headers,
        json=data,
    )
    response.raise_for_status()


def main(event, context):
    tracker_data = json.loads(base64.b64decode(event["body"]))
    created_event = create_event(
        tracker_data,
    )
    save_event_url(tracker_data["task_key"], str(created_event))
