#!/usr/bin/env python3
"""
generate_calendar.py
Creates master.ics for:
- F1 2026 (race weekends)
- WRC 2026 (rally date ranges)
- GT World Challenge Europe 2026 (round date ranges)
- UFC (auto-updating via ESPN UFC schedule page)

All events include a 1-hour reminder (VALARM).
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable, Optional

import requests


# -----------------------------
# Helpers (ICS formatting)
# -----------------------------

def ics_escape(s: str) -> str:
    return (
        s.replace("\\", "\\\\")
         .replace("\n", "\\n")
         .replace(",", "\\,")
         .replace(";", "\\;")
    )

def dtstamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def fmt_date(d: date) -> str:
    return d.strftime("%Y%m%d")

def fmt_dt_local(d: datetime) -> str:
    # DTSTART;TZID=America/New_York:YYYYMMDDTHHMMSS
    return d.strftime("%Y%m%dT%H%M%S")

def vevent_all_day(
    summary: str,
    start_inclusive: date,
    end_inclusive: date,
    location: str = "",
    description: str = "",
    categories: str = "",
) -> str:
    uid = f"{uuid.uuid4()}@sports-calendar"
    dtend_exclusive = end_inclusive + timedelta(days=1)

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp_utc()}",
        f"SUMMARY:{ics_escape(summary)}",
        f"DTSTART;VALUE=DATE:{fmt_date(start_inclusive)}",
        f"DTEND;VALUE=DATE:{fmt_date(dtend_exclusive)}",
    ]
    if location:
        lines.append(f"LOCATION:{ics_escape(location)}")
    if categories:
        lines.append(f"CATEGORIES:{ics_escape(categories)}")
    if description:
        lines.append(f"DESCRIPTION:{ics_escape(description)}")

    # 1-hour reminder
    lines += [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder",
        "TRIGGER:-PT1H",
        "END:VALARM",
        "END:VEVENT",
    ]
    return "\n".join(lines)

def vevent_timed(
    summary: str,
    start_local: datetime,
    duration_hours: int = 5,
    tzid: str = "America/New_York",
    location: str = "",
    description: str = "",
    categories: str = "",
) -> str:
    uid = f"{uuid.uuid4()}@sports-calendar"
    end_local = start_local + timedelta(hours=duration_hours)

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp_utc()}",
        f"SUMMARY:{ics_escape(summary)}",
        f"DTSTART;TZID={tzid}:{fmt_dt_local(start_local)}",
        f"DTEND;TZID={tzid}:{fmt_dt_local(end_local)}",
    ]
    if location:
        lines.append(f"LOCATION:{ics_escape(location)}")
    if categories:
        lines.append(f"CATEGORIES:{ics_escape(categories)}")
    if description:
        lines.append(f"DESCRIPTION:{ics_escape(description)}")

    # 1-hour reminder
    lines += [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder",
        "TRIGGER:-PT1H",
        "END:VALARM",
        "END:VEVENT",
    ]
    return "\n".join(lines)


# -----------------------------
# Static calendars (2026)
# -----------------------------

def add_static_f1_2026(events: list[str]) -> None:
    # Official F1 2026 calendar (weekend date ranges) :contentReference[oaicite:2]{index=2}
    f1 = [
        ("Australian Grand Prix", "2026-03-06", "2026-03-08", "Melbourne, Australia"),
        ("Chinese Grand Prix", "2026-03-13", "2026-03-15", "Shanghai, China"),
        ("Japanese Grand Prix", "2026-03-27", "2026-03-29", "Suzuka, Japan"),
        ("Bahrain Grand Prix", "2026-04-10", "2026-04-12", "Sakhir, Bahrain"),
        ("Saudi Arabian Grand Prix", "2026-04-17", "2026-04-19", "Jeddah, Saudi Arabia"),
        ("Miami Grand Prix", "2026-05-01", "2026-05-03", "Miami, USA"),
        ("Canadian Grand Prix", "2026-05-22", "2026-05-24", "Montreal, Canada"),
        ("Monaco Grand Prix", "2026-06-05", "2026-06-07", "Monaco"),
        ("Barcelona-Catalunya Grand Prix", "2026-06-12", "2026-06-14", "Barcelona, Spain"),
        ("Austrian Grand Prix", "2026-06-26", "2026-06-28", "Spielberg, Austria"),
        ("British Grand Prix", "2026-07-03", "2026-07-05", "Silverstone, Great Britain"),
        ("Belgian Grand Prix", "2026-07-17", "2026-07-19", "Spa-Francorchamps, Belgium"),
        ("Hungarian Grand Prix", "2026-07-24", "2026-07-26", "Budapest, Hungary"),
        ("Dutch Grand Prix", "2026-08-21", "2026-08-23", "Zandvoort, Netherlands"),
        ("Italian Grand Prix", "2026-09-04", "2026-09-06", "Monza, Italy"),
        ("Spanish Grand Prix (Madrid)", "2026-09-11", "2026-09-13", "Madrid, Spain"),
        ("Azerbaijan Grand Prix", "2026-09-24", "2026-09-26", "Baku, Azerbaijan"),
        ("Singapore Grand Prix", "2026-10-09", "2026-10-11", "Singapore"),
        ("United States Grand Prix", "2026-10-23", "2026-10-25", "Austin, USA"),
        ("Mexico City Grand Prix", "2026-10-30", "2026-11-01", "Mexico City, Mexico"),
        ("São Paulo Grand Prix", "2026-11-06", "2026-11-08", "São Paulo, Brazil"),
        ("Las Vegas Grand Prix", "2026-11-19", "2026-11-21", "Las Vegas, USA"),
        ("Qatar Grand Prix", "2026-11-27", "2026-11-29", "Lusail, Qatar"),
        ("Abu Dhabi Grand Prix", "2026-12-04", "2026-12-06", "Abu Dhabi, UAE"),
    ]
    for name, s, e, loc in f1:
        sd = date.fromisoformat(s)
        ed = date.fromisoformat(e)
        events.append(
            vevent_all_day(
                summary=f"🟦 F1 – {name}",
                start_inclusive=sd,
                end_inclusive=ed,
                location=loc,
                description="Race weekend dates (session times not included).",
                categories="Formula 1",
            )
        )

def add_static_wrc_2026(events: list[str]) -> None:
    # WRC calendar 2026 date ranges :contentReference[oaicite:3]{index=3}
    wrc = [
        ("Rallye Monte-Carlo", "2026-01-22", "2026-01-25", "Monaco"),
        ("Rally Sweden", "2026-02-12", "2026-02-15", "Sweden"),
        ("Safari Rally Kenya", "2026-03-12", "2026-03-15", "Kenya"),
        ("Croatia Rally", "2026-04-09", "2026-04-12", "Croatia"),
        ("Rally Islas Canarias", "2026-04-23", "2026-04-26", "Spain"),
        ("Vodafone Rally de Portugal", "2026-05-07", "2026-05-10", "Portugal"),
        ("FORUM8 Rally Japan", "2026-05-28", "2026-05-31", "Japan"),
        ("EKO Acropolis Rally Greece", "2026-06-25", "2026-06-28", "Greece"),
        ("Delfi Rally Estonia", "2026-07-16", "2026-07-19", "Estonia"),
        ("Secto Rally Finland", "2026-07-30", "2026-08-02", "Finland"),
        ("ueno Rally del Paraguay", "2026-08-27", "2026-08-30", "Paraguay"),
        ("Rally Chile Bio Bío", "2026-09-10", "2026-09-13", "Chile"),
        ("Rally Italia Sardegna", "2026-10-01", "2026-10-04", "Italy"),
        ("Rally Saudi Arabia", "2026-11-11", "2026-11-14", "Saudi Arabia"),
    ]
    for name, s, e, loc in wrc:
        sd = date.fromisoformat(s)
        ed = date.fromisoformat(e)
        events.append(
            vevent_all_day(
                summary=f"🟩 WRC – {name}",
                start_inclusive=sd,
                end_inclusive=ed,
                location=loc,
                description="Rally date range (stage times not included).",
                categories="WRC",
            )
        )

def add_static_gtwc_europe_2026(events: list[str]) -> None:
    # GT World Challenge Europe 2026 calendar (round date ranges) :contentReference[oaicite:4]{index=4}
    gt = [
        ("Circuit Paul Ricard (Round 1)", "2026-04-10", "2026-04-12", "Le Castellet, France"),
        ("Brands Hatch (Round 2)", "2026-05-02", "2026-05-03", "Kent, Great Britain"),
        ("Monza (Round 3)", "2026-05-30", "2026-05-31", "Monza, Italy"),
        ("CrowdStrike 24 Hours of Spa (Round 4)", "2026-06-25", "2026-06-28", "Spa-Francorchamps, Belgium"),
        ("Misano (Round 5)", "2026-07-18", "2026-07-19", "Misano, Italy"),
        ("Magny-Cours (Round 6)", "2026-08-01", "2026-08-02", "Magny-Cours, France"),
        ("Nürburgring (Round 7)", "2026-08-29", "2026-08-30", "Nürburg, Germany"),
        ("Zandvoort (Round 8)", "2026-09-19", "2026-09-20", "Zandvoort, Netherlands"),
        ("Barcelona (Round 9)", "2026-10-03", "2026-10-04", "Barcelona, Spain"),
        ("Portimão (Round 10)", "2026-10-17", "2026-10-18", "Portimão, Portugal"),
    ]
    for name, s, e, loc in gt:
        sd = date.fromisoformat(s)
        ed = date.fromisoformat(e)
        events.append(
            vevent_all_day(
                summary=f"🟥 GTWC Europe – {name}",
                start_inclusive=sd,
                end_inclusive=ed,
                location=loc,
                description="Race weekend dates (session times not included).",
                categories="GT World Challenge Europe",
            )
        )


# -----------------------------
# UFC auto-updating (ESPN)
# -----------------------------

from zoneinfo import ZoneInfo

def fetch_ufc_events_from_espn_table(max_events: int = 200):
    """
    Scrape the visible UFC schedule table from ESPN.
    ESPN shows times in ET on the page. :contentReference[oaicite:2]{index=2}
    """
    url = "https://www.espn.com/mma/schedule/_/league/ufc"
    html = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"}).text

    # Example row text patterns on page:
    # "Jan 24 5:00 PM" then "UFC 324: ..." then "T-Mobile Arena, Las Vegas, NV"
    # We'll capture blocks containing Month Day, Time, Event, Location.
    # This regex is intentionally forgiving.
    row_re = re.compile(
        r'([A-Z][a-z]{2})\s+(\d{1,2})\s*.*?(\d{1,2}:\d{2}\s*[AP]M).*?'
        r'(UFC[^<\n\r]+).*?'
        r'([A-Za-z0-9].{5,120}?)\s*(?:</td>|</tr>)',
        re.S
    )

    month_map = {m: i for i, m in enumerate(
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], start=1
    )}

    et = ZoneInfo("America/New_York")
    now_et = datetime.now(et)

    out = []
    for mo, day, time_str, event_name, location in row_re.findall(html):
        try:
            year = now_et.year  # page is "2026 season" right now, but keep flexible
            # If we're late in year and see Jan/Feb, it might be next year:
            mnum = month_map.get(mo)
            if not mnum:
                continue

            # crude rollover: if month is much earlier than current month, bump year
            if mnum < (now_et.month - 6):
                year += 1

            dt_et = datetime.strptime(f"{year}-{mnum:02d}-{int(day):02d} {time_str.strip()}",
                                      "%Y-%m-%d %I:%M %p").replace(tzinfo=et)

            # Only keep upcoming (or very recent) events
            if dt_et < (now_et - timedelta(days=7)):
                continue

            out.append((event_name.strip(), dt_et, location.strip()))
            if len(out) >= max_events:
                break
        except Exception:
            continue

    # Deduplicate
    uniq = {}
    for name, dt_et, loc in out:
        uniq[(name, dt_et)] = (name, dt_et, loc)

    return [uniq[k] for k in sorted(uniq.keys(), key=lambda x: x[1])]

def vevent_timed_utc(summary: str, start_et: datetime, duration_hours: int = 5,
                    location: str = "", description: str = "", categories: str = "") -> str:
    uid = f"{uuid.uuid4()}@sports-calendar"
    start_utc = start_et.astimezone(timezone.utc)
    end_utc = (start_et + timedelta(hours=duration_hours)).astimezone(timezone.utc)

    def fmtz(d: datetime) -> str:
        return d.strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp_utc()}",
        f"SUMMARY:{ics_escape(summary)}",
        f"DTSTART:{fmtz(start_utc)}",
        f"DTEND:{fmtz(end_utc)}",
    ]
    if location:
        lines.append(f"LOCATION:{ics_escape(location)}")
    if categories:
        lines.append(f"CATEGORIES:{ics_escape(categories)}")
    if description:
        lines.append(f"DESCRIPTION:{ics_escape(description)}")

    lines += [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder",
        "TRIGGER:-PT1H",
        "END:VALARM",
        "END:VEVENT",
    ]
    return "\n".join(lines)

def add_dynamic_ufc(events: list[str]) -> None:
    for name, start_et, loc in fetch_ufc_events_from_espn_table():
        events.append(
            vevent_timed_utc(
                summary=f"🟪 {name}",
                start_et=start_et,
                duration_hours=5,
                location=loc,
                description="Auto-updated from ESPN UFC schedule (times shown as ET on ESPN).",
                categories="UFC",
            )
        )



# -----------------------------
# Build calendar
# -----------------------------

def build_calendar() -> str:
    events: list[str] = []

    add_static_f1_2026(events)
    add_static_wrc_2026(events)
    add_static_gtwc_europe_2026(events)

    # UFC auto-updates
    try:
        add_dynamic_ufc(events)
    except Exception as e:
        # Don't fail the whole calendar if ESPN changes something
        events.append(
            vevent_all_day(
                summary="🟪 UFC – (Auto-update temporarily unavailable)",
                start_inclusive=date.today(),
                end_inclusive=date.today(),
                description=f"UFC fetch failed: {e}",
                categories="UFC",
            )
        )

    cal_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Custom Sports Master Feed//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:WRC + GTWC Europe + F1 + UFC (Master Feed)",
        "X-WR-TIMEZONE:America/New_York",
        *events,
        "END:VCALENDAR",
        "",
    ]
    return "\n".join(cal_lines)


def main() -> None:
    ics = build_calendar()
    with open("master.ics", "w", encoding="utf-8") as f:
        f.write(ics)
    print("Wrote master.ics")

if __name__ == "__main__":
    main()
