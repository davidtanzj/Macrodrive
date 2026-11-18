from macrocalendar import (
    create_calendar_database,
    save_events,
)

from collectors import (
    uscalendar,
    eurozonecalendar,
    centralbanks,
)


COLLECTORS = [
    ("United States", uscalendar),
    ("Eurozone", eurozonecalendar),
    ("Central Banks", centralbanks),
]


# ============================================================
# RUN CALENDAR COLLECTION
# ============================================================

def run_calendar_collector():
    create_calendar_database()

    print()
    print("=" * 70)
    print("Macrodrive CALENDAR UPDATE")
    print("=" * 70)

    events = []
    reports = []

    for name, collector in COLLECTORS:
        try:
            collected = collector.collect()
            events.extend(collected)
            reports.append((name, len(collected), "OK"))
        except Exception as error:
            # One country's parser should never prevent all other
            # calendars from updating.
            print()
            print(f"FAILED {name}: {error}", flush=True)
            reports.append((name, 0, f"FAILED: {error}"))

    print()
    print(f"Saving {len(events)} calendar events...", flush=True)

    save_events(
        events,
        commit_every=25,
    )

    print()
    print("=" * 70)
    print("CALENDAR COLLECTION REPORT")
    print("=" * 70)

    for name, count, status in reports:
        print(
            f"{name}: {count} events | {status}",
            flush=True,
        )

    print(f"Total events processed: {len(events)}")
    print(f"Events saved/updated: {len(events)}")
    print("=" * 70)


if __name__ == "__main__":
    run_calendar_collector()
