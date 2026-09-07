from macrocalendar import (
    create_calendar_database,
    save_event
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


    saved = 0


    for event in events:

        save_event(
            event
        )

        saved += 1


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