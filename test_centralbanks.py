import hashlib
import os
from datetime import datetime, timezone

import yaml

from collectors import centralbanks


FAILURES = []


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        FAILURES.append(label)


def main():
    print("=" * 60)
    print("test_centralbanks.py")
    print("=" * 60)

    # --- Config file exists and parses -------------------------------
    config_path = centralbanks.CONFIG_PATH
    check("central_banks.yaml exists", os.path.isfile(config_path))

    with open(config_path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    banks = config.get("banks", [])
    check("config has 16 banks", len(banks) == 16)

    expected_codes = {
        "BOE", "BOJ", "SNB", "BOC", "RBA", "RBNZ", "NORGES",
        "RIKSBANK", "RBI", "BOK", "BI", "BSP", "BOT", "BNM",
        "PBOC", "MAS",
    }
    codes = {bank["code"] for bank in banks}
    check("all 16 bank codes present", codes == expected_codes)

    # --- Every bank carries required metadata ------------------------
    required_bank_keys = {
        "code", "name", "country", "region", "timezone",
        "event_type", "source_url", "events",
    }
    for bank in banks:
        check(
            f"{bank['code']} has required keys",
            required_bank_keys <= set(bank.keys()),
        )
        check(
            f"{bank['code']} has a source_url",
            isinstance(bank.get("source_url"), str)
            and bank["source_url"].startswith("http"),
        )
        check(
            f"{bank['code']} has >=1 event",
            len(bank.get("events", [])) >= 1,
        )
        for entry in bank["events"]:
            check(
                f"{bank['code']} event date format",
                len(entry.get("date", "")) == 10
                and entry["date"][4] == "-" and entry["date"][7] == "-",
            )

    # --- PBoC is labelled as LPR fixing, MAS as policy statement ------
    pboc = next(b for b in banks if b["code"] == "PBOC")
    check(
        "PBoC events are LPR fixings",
        all("LPR" in e["name"] for e in pboc["events"]),
    )
    check("PBoC has 12 monthly LPR events", len(pboc["events"]) == 12)

    mas = next(b for b in banks if b["code"] == "MAS")
    check(
        "MAS events are monetary policy statements",
        all("Monetary Policy Statement" in e["name"] for e in mas["events"]),
    )

    # --- Timezone conversion (winter GMT vs summer BST) ----------------
    check(
        "London summer converts to UTC (12:00 BST -> 11:00 UTC)",
        centralbanks.build_utc_datetime(
            "2026-06-18", "12:00", "Europe/London"
        ) == "2026-06-18T11:00:00+00:00",
    )
    check(
        "London winter converts to UTC (12:00 GMT -> 12:00 UTC)",
        centralbanks.build_utc_datetime(
            "2026-12-17", "12:00", "Europe/London"
        ) == "2026-12-17T12:00:00+00:00",
    )

    # --- event_key matches existing hash pattern ----------------------
    raw = "BOE|Bank of England Rate Decision|2026-12-17T12:00:00+00:00"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
    expected_key = f"boe-{digest}"
    check(
        "event_key matches sha256 pattern",
        centralbanks.build_event_key(
            "BOE",
            "Bank of England Rate Decision",
            "2026-12-17T12:00:00+00:00",
        ) == expected_key,
    )

    # --- collect() returns valid, unique, upcoming events -------------
    events = centralbanks.collect()
    check("collect() returned events", len(events) > 0)

    keys = [e["event_key"] for e in events]
    check("event keys are unique", len(keys) == len(set(keys)))

    now = datetime.now(timezone.utc)
    required_event_keys = {
        "event_key", "country", "region", "event_name", "event_type",
        "scheduled_at", "importance", "source", "source_url", "status",
    }
    for event in events:
        check(
            f"event {event['event_name']} has required keys",
            required_event_keys <= set(event.keys()),
        )
        scheduled = datetime.fromisoformat(event["scheduled_at"])
        check(
            f"event {event['event_name']} is in the future",
            scheduled >= now,
        )
        check(
            f"event {event['event_name']} has UTC tz",
            event["scheduled_at"].endswith("+00:00"),
        )

    # --- Summary ------------------------------------------------------
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} checks failed")
        for failure in FAILURES:
            print(f"  - {failure}")
        raise SystemExit(1)

    print(f"PASSED: all checks passed ({len(events)} upcoming events)")
    for event in events:
        print(
            f"  {event['scheduled_at'][:10]}  "
            f"{event['country']:<16} {event['event_name']}"
        )


if __name__ == "__main__":
    main()
