import sqlite3
from db import connect_database
from datetime import datetime, timezone


DATABASE_NAME = "Macrodrive.db"


# ============================================================
# CREATE CALENDAR TABLE
# ============================================================

def create_calendar_database():

    owns_connection = connection is None

    if owns_connection:
        connection = connect_database()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            event_key TEXT NOT NULL UNIQUE,

            country TEXT NOT NULL,

            region TEXT,

            event_name TEXT NOT NULL,

            event_type TEXT,

            scheduled_at TEXT NOT NULL,

            importance INTEGER DEFAULT 1,

            previous TEXT,

            consensus TEXT,

            actual TEXT,

            unit TEXT,

            source TEXT,

            source_url TEXT,

            status TEXT DEFAULT 'scheduled',

            created_at TEXT,

            updated_at TEXT
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# SAVE / UPDATE EVENT
# ============================================================

def save_event(event, connection=None):

    connection = connect_database()

    cursor = connection.cursor()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    cursor.execute("""
        INSERT INTO calendar_events (

            event_key,
            country,
            region,
            event_name,
            event_type,
            scheduled_at,
            importance,
            previous,
            consensus,
            actual,
            unit,
            source,
            source_url,
            status,
            created_at,
            updated_at
        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?
        )

        ON CONFLICT(event_key)

        DO UPDATE SET

            country =
                excluded.country,

            region =
                excluded.region,

            event_name =
                excluded.event_name,

            event_type =
                excluded.event_type,

            scheduled_at =
                excluded.scheduled_at,

            importance =
                excluded.importance,

            previous =
                excluded.previous,

            consensus =
                excluded.consensus,

            actual =
                excluded.actual,

            unit =
                excluded.unit,

            source =
                excluded.source,

            source_url =
                excluded.source_url,

            status =
                excluded.status,

            updated_at =
                excluded.updated_at
    """, (

        event["event_key"],
        event["country"],
        event.get("region", ""),
        event["event_name"],
        event.get("event_type", ""),
        event["scheduled_at"],
        event.get("importance", 1),
        event.get("previous"),
        event.get("consensus"),
        event.get("actual"),
        event.get("unit", ""),
        event.get("source", ""),
        event.get("source_url", ""),
        event.get("status", "scheduled"),
        now,
        now
    ))

    if owns_connection:
        connection.commit()
        connection.close()


def save_events(events, commit_every=25):
    connection = connect_database()

    try:
        for index, event in enumerate(events, start=1):
            save_event(
                event,
                connection=connection
            )

            if (
                index % commit_every == 0
                or index == len(events)
            ):
                connection.commit()

                print(
                    f"Calendar database progress: "
                    f"{index}/{len(events)}",
                    flush=True
                )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# GET EVENTS
# ============================================================

def get_calendar_events():

    connection = connect_database()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM calendar_events

        ORDER BY
            scheduled_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# GET COUNTRIES
# ============================================================

def get_calendar_countries():

    connection = connect_database()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT country

        FROM calendar_events

        ORDER BY country
    """)

    countries = [
        row[0]
        for row in cursor.fetchall()
    ]

    connection.close()

    return countries