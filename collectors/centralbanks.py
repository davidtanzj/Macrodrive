import hashlib
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "central_banks.yaml",
)

DEFAULT_TIME = "09:00"


def build_event_key(source_key, event_name, scheduled_at):
    raw = f"{source_key}|{event_name}|{scheduled_at}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
    return f"{source_key.lower().replace(' ', '-')}-{digest}"


def build_utc_datetime(date_string, time_string, tz_name):
    local_dt = datetime.strptime(
        f"{date_string} {time_string}",
        "%Y-%m-%d %H:%M",
    ).replace(tzinfo=ZoneInfo(tz_name))

    return local_dt.astimezone(timezone.utc).isoformat()


def load_config():
    # Lazy import so a missing PyYAML does not break the importer; the
    # failure is caught by calendarcollector.py's per-collector guard.
    import yaml

    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def collect():
    config = load_config()

    events = []
    now = datetime.now(timezone.utc)

    for bank in config.get("banks", []):
        bank_time = bank.get("time", DEFAULT_TIME)

        for entry in bank.get("events", []):
            scheduled_at = build_utc_datetime(
                entry["date"],
                entry.get("time", bank_time),
                bank["timezone"],
            )

            # Keep only upcoming events, matching the ECB/FOMC collectors.
            if datetime.fromisoformat(scheduled_at) < now:
                continue

            events.append({
                "event_key": build_event_key(
                    bank["code"],
                    entry["name"],
                    scheduled_at,
                ),
                "country": bank["country"],
                "region": bank["region"],
                "event_name": entry["name"],
                "event_type": bank["event_type"],
                "scheduled_at": scheduled_at,
                "importance": entry.get("importance", 2),
                "previous": None,
                "consensus": None,
                "actual": None,
                "unit": "",
                "source": bank["name"],
                "source_url": bank["source_url"],
                "status": "scheduled",
            })

    events.sort(key=lambda event: event["scheduled_at"])

    print(f"Loaded {len(events)} upcoming central bank events.", flush=True)
    return events
