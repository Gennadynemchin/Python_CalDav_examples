from caldav import DAVClient
from convert_data import from_byte_to_dict
from icalendar import vCalAddress, vText
from datetime import datetime, timedelta
from settings.logger import logger
from settings.settings import creds, Credentials


def edit_event(
    creds: Credentials,
    event_url: str,
    event_data: dict,
):
    with DAVClient(
        url=creds.caldav_url,
        username=creds.caldav_username,
        password=creds.caldav_password,
    ) as client:
        event = client.calendar(url=creds.calendar_url).event_by_url(event_url)
        new_date = event_data.get("deadline")
        attendees = event_data.get("attendees")
        event.load()
        logger.info(f"Loaded event: {event}")
        event.vobject_instance.vevent.dtstamp.value = datetime.now()

        if new_date:
            logger.info(f"Found new date: {new_date}")
            new_date_formatted = datetime.strptime(new_date, "%Y-%m-%d").date()
            event.vobject_instance.vevent.dtstart.value = new_date_formatted
            event.vobject_instance.vevent.dtend.value = new_date_formatted + timedelta(
                days=1
            )

        if attendees:
            logger.info(f"Found attendees: {attendees}")
            new_attendees = []
            for attendee in attendees:
                new_attendee = vCalAddress(f"MAILTO:{attendee}")
                new_attendee.params["RSVP"] = vText("TRUE")
                new_attendees.append(new_attendee)
            event.icalendar_component["attendee"] = new_attendees

        event.save()
        logger.info(f"Saved event: {event}")
        return event


if __name__ == "__main__":
    tracker_data = from_byte_to_dict(
                                        b'{"attendees": [test11@test.ru, test22@test.ru],\
                                        "deadline": "2027-08-27"}'
    )

    edit_event(
        creds,
        "https://caldav.yandex.ru/calendars/gnemchin%40yandex.ru/events-30436394/11be840a-6523-11ef-bd17-86c1c6bdf2ad.ics",
        tracker_data,
    )
