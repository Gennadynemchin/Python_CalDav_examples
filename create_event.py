from caldav import DAVClient
from icalendar import Event, vCalAddress, vText
from datetime import datetime, timedelta
from settings.logger import logger
from settings.settings import creds


def create_event(
    creds,
    deadline: str,
    summary: str,
    attendees: list,
    description: str | None = None,
) -> str:
    with DAVClient(
        url=creds.caldav_url,
        username=creds.caldav_username,
        password=creds.caldav_password,
    ) as client:
        calendar_tracker = client.calendar(url=creds.calendar_url)
        event = Event()
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

        logger.info(f"Added info to event: {event}")

        if attendees:
            logger.info(f"Found attendees: {attendees}")
            for email in attendees:
                attendee = vCalAddress(f"MAILTO:{email}")
                attendee.params["RSVP"] = vText("TRUE")
                event.add("attendee", attendee)
            logger.info(f"Added attendees to event: {event}")

        created_event = calendar_tracker.add_event(event.to_ical())
        logger.info(f"Created event: {created_event}")
        return created_event


if __name__ == "__main__":
    create_event(
        creds,
        deadline="2024-08-28",
        summary="August, 28th",
        attendees=["test1@test.ru", "test2@test.ru"],
    )
