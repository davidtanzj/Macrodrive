import hashlib
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import certifi
import requests
from bs4 import BeautifulSoup


ECB_MEETING_URL = (
    "https://www.ecb.europa.eu/press/calendars/"
    "mgcgc/html/index.en.html"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

FRANKFURT = ZoneInfo("Europe/Berlin")

# ECB decisions are normally published at 14:15 CET/CEST and the
# press conference begins at 14:45 CET/CEST. Keep these constants
# isolated so they are easy to update if the ECB changes its schedule.
DECISION_TIME = (14, 15)
PRESS_CONFERENCE_TIME = (14, 45)


def normalize_spaces(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def build_event_key(source, event_name, scheduled_at):
    raw = f"{source}|{event_name}|{scheduled_at}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
    return f"{source.lower().replace(' ', '-')}-{digest}"


def build_utc_datetime(release_date, release_time):
    hour, minute = release_time
    local_dt = datetime(
        release_date.year,
        release_date.month,
        release_date.day,
        hour,
        minute,
        tzinfo=FRANKFURT,
    )
    return local_dt.astimezone(timezone.utc).isoformat()


def build_event(event_name, scheduled_at):
    return {
        "event_key": build_event_key("ECB", event_name, scheduled_at),
        "country": "Eurozone",
        "region": "Europe",
        "event_name": event_name,
        "event_type": "Central Banking & Rates",
        "scheduled_at": scheduled_at,
        "importance": 3,
        "previous": None,
        "consensus": None,
        "actual": None,
        "unit": "",
        "source": "European Central Bank",
        "source_url": ECB_MEETING_URL,
        "status": "scheduled",
    }


def collect_ecb():
    print()
    print("-" * 70)
    print("EUROPEAN CENTRAL BANK")
    print("-" * 70)
    print("Fetching ECB Governing Council calendar...")

    try:
        response = requests.get(
            ECB_MEETING_URL,
            headers=HEADERS,
            timeout=20,
            verify=certifi.where(),
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"FAILED: {error}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = normalize_spaces(soup.get_text("\n", strip=True))

    # Match only Day 2 monetary-policy meetings, which are the decision
    # days followed by the press conference. Example source text:
    # 29/10/2026 Governing Council ... monetary policy meeting ...
    # (Day 2), followed by press conference
    pattern = re.compile(
        r"(\d{2}/\d{2}/\d{4})\s+"
        r"Governing Council of the ECB:\s*"
        r"monetary policy meeting.*?"
        r"\(Day 2\),\s*followed by press conference",
        re.IGNORECASE,
    )

    events = []
    now = datetime.now(timezone.utc)

    for match in pattern.finditer(page_text):
        try:
            decision_date = datetime.strptime(
                match.group(1), "%d/%m/%Y"
            ).date()
        except ValueError:
            continue

        decision_at = build_utc_datetime(
            decision_date,
            DECISION_TIME,
        )
        press_at = build_utc_datetime(
            decision_date,
            PRESS_CONFERENCE_TIME,
        )

        # Keep upcoming/current-day events. Existing historical events in
        # Neon remain untouched when the official page stops listing them.
        if datetime.fromisoformat(press_at) < now:
            continue

        events.append(
            build_event("ECB Rate Decision", decision_at)
        )
        events.append(
            build_event("ECB Press Conference", press_at)
        )

    unique = {
        event["event_key"]: event
        for event in events
    }
    events = list(unique.values())
    events.sort(key=lambda event: event["scheduled_at"])

    print(f"Found {len(events)} upcoming ECB events.")
    return events


def collect():
    print()
    print("=" * 70)
    print("EUROZONE MACRO CALENDAR")
    print("=" * 70)

    events = collect_ecb()

    print()
    print("=" * 70)
    print("EUROZONE CALENDAR REPORT")
    print("=" * 70)
    print(f"Total events: {len(events)}")
    print("=" * 70)

    return events
