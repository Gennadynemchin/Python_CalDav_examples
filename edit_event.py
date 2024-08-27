from caldav import DAVClient
from icalendar import vCalAddress, vText
from datetime import datetime, timedelta
from settings.logger import logger
from settings.settings import creds, Credentials


def edit_event(
    creds: Credentials,
    event_url: str,
    new_date: str | None = None,
    attendees: list | None = None,
):
    with DAVClient(
        url=creds.caldav_url,
        username=creds.caldav_username,
        password=creds.caldav_password,
    ) as client:
        event = client.calendar(url=creds.calendar_url).event_by_url(event_url)

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
    edit_event(
        creds,
        "LINK TO ICS",
        attendees=["test3@test.ru"],
    )
