from datetime import datetime, timedelta
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
import pytz
from config.config import CALENDAR_CREDETIAL_PATH

def get_calendar_events(date):
    date = date.split("DATE = ")[1].strip()
    date = datetime.strptime(date, "%d %B %Y")
    
    credentials = service_account.Credentials.from_service_account_file(CALENDAR_CREDETIAL_PATH, scopes=["https://www.googleapis.com/auth/calendar"])
    gc = GoogleCalendar(credentials=credentials)
    events = []

    # Specify the time zone for the calendar events
    event_timezone = pytz.timezone('Europe/Prague')

    for event in gc.get_events(date, date + timedelta(days=1), order_by="startTime", single_events=True):
        # Convert event start and end times to the specified time zone
        event_start_local = event.start.astimezone(event_timezone)
        event_end_local = event.end.astimezone(event_timezone)

        # Format the event details with localized time
        events.append(f"- {event.summary} at {event.location} from {event_start_local.strftime('%I:%M%p')} to {event_end_local.strftime('%I:%M%p')}")

    if events:
        return f"{len(events)} events on {date.strftime('%d %B %Y')} in USER's Calendar:\n" + "\n".join(events)
    else:
        return f"No events found on {date.strftime('%d %B %Y')}."

if __name__ == "__main__":
    print(get_calendar_events(datetime.strptime("28 October 2023", "%d %B %Y")))
