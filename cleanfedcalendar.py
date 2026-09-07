import sqlite3


DATABASE_NAME = "Macrodrive.db"


def clean_fed_calendar():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)

        FROM calendar_events

        WHERE source = 'Federal Reserve'
    """)

    count = cursor.fetchone()[0]

    cursor.execute("""
        DELETE FROM calendar_events

        WHERE source = 'Federal Reserve'
    """)

    connection.commit()
    connection.close()

    print()
    print("=" * 60)
    print("FED CALENDAR CLEANUP")
    print("=" * 60)
    print(f"Federal Reserve events deleted: {count}")
    print("=" * 60)


if __name__ == "__main__":

    clean_fed_calendar()