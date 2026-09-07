from macrocalendar import (
    create_calendar_database,
    save_events
)

from collectors import (
    uscalendar
)


# ============================================================
# RUN CALENDAR COLLECTION
# ============================================================

def run_calendar_collector():

    create_calendar_database()


    print()
    print("=" * 70)
    print(
        "Macrodrive CALENDAR UPDATE"
    )
    print("=" * 70)


    events = (
        uscalendar.collect()
    )


    print(
        f"Saving {len(events)} calendar events...",
        flush=True
    )

    save_events(
        events,
        commit_every=25
    )

    saved = len(events)


    print()
    print("=" * 70)

    print(
        "CALENDAR COLLECTION REPORT"
    )

    print("=" * 70)

    print(
        f"Events processed: "
        f"{len(events)}"
    )

    print(
        f"Events saved/updated: "
        f"{saved}"
    )

    print("=" * 70)


if __name__ == "__main__":

    run_calendar_collector()