import sqlite3
from datetime import datetime, timezone


DATABASE_NAME = "Macrodrive.db"


# ============================================================
# DATE HELPERS
# ============================================================

def parse_date(value):

    if not value:
        return None

    try:
        return datetime.fromisoformat(value)

    except ValueError:
        return None


def format_date(value):

    dt = parse_date(value)

    if not dt:
        return "Unknown"

    return dt.strftime(
        "%d %b %Y %H:%M UTC"
    )


def age_string(value):

    dt = parse_date(value)

    if not dt:
        return "Unknown"

    if dt.tzinfo is None:
        dt = dt.replace(
            tzinfo=timezone.utc
        )

    now = datetime.now(
        timezone.utc
    )

    difference = (
        now - dt
    )

    total_seconds = int(
        difference.total_seconds()
    )

    if total_seconds < 0:
        return "Future dated"

    hours = (
        total_seconds // 3600
    )

    days = (
        hours // 24
    )

    if days > 0:

        return (
            f"{days} day"
            + (
                "s"
                if days != 1
                else ""
            )
            + " ago"
        )

    if hours > 0:

        return (
            f"{hours} hour"
            + (
                "s"
                if hours != 1
                else ""
            )
            + " ago"
        )

    minutes = (
        total_seconds // 60
    )

    return (
        f"{minutes} minute"
        + (
            "s"
            if minutes != 1
            else ""
        )
        + " ago"
    )


# ============================================================
# SOURCE AUDIT
# ============================================================

def audit_sources():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = (
        sqlite3.Row
    )

    cursor = connection.cursor()

    # --------------------------------------------------------
    # GET SOURCES
    # --------------------------------------------------------

    cursor.execute("""
        SELECT DISTINCT source

        FROM articles

        ORDER BY source
    """)

    sources = [
        row["source"]
        for row in cursor.fetchall()
    ]

    print()
    print("=" * 72)
    print(
        "Macrodrive SOURCE AUDIT"
    )
    print("=" * 72)

    print(
        f"Sources in database: "
        f"{len(sources)}"
    )

    print("=" * 72)


    for source in sources:

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count

            FROM articles

            WHERE source = ?
        """, (
            source,
        ))

        total = (
            cursor.fetchone()["count"]
        )

        # ----------------------------------------------------
        # MACRO RELEVANT
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count

            FROM articles

            WHERE
                source = ?

                AND macro_relevant = 1
        """, (
            source,
        ))

        relevant = (
            cursor.fetchone()["count"]
        )

        # ----------------------------------------------------
        # NOT MACRO RELEVANT
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count

            FROM articles

            WHERE
                source = ?

                AND macro_relevant = 0
        """, (
            source,
        ))

        rejected = (
            cursor.fetchone()["count"]
        )

        # ----------------------------------------------------
        # AWAITING RELEVANCE PROCESSING
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count

            FROM articles

            WHERE
                source = ?

                AND macro_relevant IS NULL
        """, (
            source,
        ))

        awaiting = (
            cursor.fetchone()["count"]
        )

        # ----------------------------------------------------
        # WITHOUT BODY TEXT
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count

            FROM articles

            WHERE
                source = ?

                AND (
                    body_text IS NULL
                    OR body_text = ''
                )
        """, (
            source,
        ))

        no_text = (
            cursor.fetchone()["count"]
        )

        # ----------------------------------------------------
        # NEWEST COLLECTED ARTICLE
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                title,
                published_at

            FROM articles

            WHERE
                source = ?

                AND published_at IS NOT NULL

            ORDER BY
                published_at DESC

            LIMIT 1
        """, (
            source,
        ))

        newest = cursor.fetchone()

        # ----------------------------------------------------
        # NEWEST MACRO-RELEVANT ARTICLE
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                title,
                published_at

            FROM articles

            WHERE
                source = ?

                AND macro_relevant = 1

                AND published_at IS NOT NULL

            ORDER BY
                published_at DESC

            LIMIT 1
        """, (
            source,
        ))

        newest_relevant = (
            cursor.fetchone()
        )

        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        print()
        print(source.upper())
        print("-" * 72)

        print(
            f"Stored articles:          "
            f"{total}"
        )

        print(
            f"Macro relevant:           "
            f"{relevant}"
        )

        print(
            f"Rejected as non-macro:    "
            f"{rejected}"
        )

        print(
            f"Awaiting classification:  "
            f"{awaiting}"
        )

        print(
            f"Without processed text:   "
            f"{no_text}"
        )

        print()

        if newest:

            print(
                "NEWEST COLLECTED"
            )

            print(
                f"Date:  "
                f"{format_date(newest['published_at'])}"
            )

            print(
                f"Age:   "
                f"{age_string(newest['published_at'])}"
            )

            print(
                f"Title: "
                f"{newest['title']}"
            )

        else:

            print(
                "NEWEST COLLECTED"
            )

            print(
                "No dated articles found."
            )

        print()

        if newest_relevant:

            print(
                "NEWEST ON WEBSITE"
            )

            print(
                f"Date:  "
                f"{format_date(newest_relevant['published_at'])}"
            )

            print(
                f"Age:   "
                f"{age_string(newest_relevant['published_at'])}"
            )

            print(
                f"Title: "
                f"{newest_relevant['title']}"
            )

        else:

            print(
                "NEWEST ON WEBSITE"
            )

            print(
                "No macro-relevant articles."
            )

        # ----------------------------------------------------
        # POSSIBLE RELEVANCE GAP
        # ----------------------------------------------------

        if (
            newest
            and newest_relevant
            and newest["published_at"]
            != newest_relevant["published_at"]
        ):

            print()
            print(
                "NOTE:"
            )

            print(
                "The newest collected article "
                "is not the newest article "
                "shown on the website."
            )

            print(
                "This may simply mean newer "
                "articles were rejected by the "
                "macro relevance filter."
            )

        print()
        print("=" * 72)

    connection.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    audit_sources()