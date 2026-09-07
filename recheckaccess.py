import sqlite3

from accessdetector import (
    detect_access,
    get_source_default
)


DATABASE_NAME = "Macrodrive.db"


def recheck_access():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            id,
            source,
            body_text

        FROM articles
    """)


    articles = cursor.fetchall()


    updated = 0


    for (
        article_id,
        source,
        body_text
    ) in articles:


        # Known sources can be corrected immediately.

        default_access = (
            get_source_default(
                source
            )
        )


        if default_access != "unknown":

            cursor.execute("""
                UPDATE articles

                SET access_type = ?

                WHERE id = ?
            """, (
                default_access,
                article_id
            ))

            updated += 1

            continue


        # For mixed publishers, substantial text already
        # stored is evidence that we previously obtained
        # accessible content, but without re-fetching the
        # original page we do not claim a paywall.

        if (
            body_text
            and len(
                body_text.strip()
            ) >= 500
        ):

            cursor.execute("""
                UPDATE articles

                SET access_type = 'free'

                WHERE id = ?
            """, (
                article_id,
            ))

            updated += 1

        else:

            cursor.execute("""
                UPDATE articles

                SET access_type = 'unknown'

                WHERE id = ?
            """, (
                article_id,
            ))


    connection.commit()

    connection.close()


    print()
    print("=" * 60)
    print(
        "ACCESS RECHECK COMPLETE"
    )
    print("=" * 60)

    print(
        f"Articles updated: {updated}"
    )

    print("=" * 60)


if __name__ == "__main__":

    recheck_access()