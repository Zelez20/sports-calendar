# generate_calendar.py
import uuid
from datetime import datetime, timedelta, date
import requests

def event(summary, start, end=None, desc="", location="", category=""):
    uid = f"{uuid.uuid4()}@sports"
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{summary}",
        f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}",
    ]
    if end:
        lines.append(f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}")
    if location:
        lines.append(f"LOCATION:{location}")
    if desc:
        lines.append(f"DESCRIPTION:{desc}")
    lines += [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        "TRIGGER:-PT1H",
        "END:VALARM",
        "END:VEVENT"
    ]
    return "\n".join(lines)

events = []

# (Static racing events go here — we’ll paste them in next)
calendar = "\n".join([
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Sports Calendar//EN",
    *events,
    "END:VCALENDAR"
])

with open("master.ics", "w") as f:
    f.write(calendar)
