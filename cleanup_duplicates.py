import re
from urllib.parse import (
    urlsplit,
    urlunsplit,
    parse_qsl,
    urlencode,
)

from db import connect_database


TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
    "cmpid",
    "campaign_id",
    "campaign",
}


def canonicalize_url(url):
    if not url:
        return ""

    try:
        parts = urlsplit(url.strip())

        query = [
            (key, value)
            for key, value in parse_qsl(
                parts.query,
                keep_blank_values=True,
            )
            if key.lower()
            not in TRACKING_QUERY_KEYS
        ]

        path = (
            parts.path.rstrip("/")
            or "/"
        )

        return urlunsplit((
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            urlencode(
                query,
                doseq=True,
            ),
            "",
        ))

    except Exception:
        return url.strip()


def normalize_title(title):
    if not title:
        return ""

    title = title.lower()

    title = re.sub(
        r"[^\w\s]",
        " ",
        title,
    )

    title = re.sub(
        r"\s+",
        " ",
        title,
    )

    return title.strip()


def merge_links(
    cursor,
    keep_id,
    remove_id,
    table,
    foreign_key,
):
    """
    Move category/region links from the duplicate article
    to the article we are keeping.

    If both articles already have the same link, retain
    whichever classification score is higher.
    """

    cursor.execute(
        f"""
        SELECT
            {foreign_key},
            score

        FROM {table}

        WHERE article_id = ?
        """,
        (
            remove_id,
        ),
    )

    links = cursor.fetchall()

    for target_id, link_score in links:

        cursor.execute(
            f"""
            INSERT INTO {table} (
                article_id,
                {foreign_key},
                score
            )

            VALUES (?, ?, ?)

            ON CONFLICT (
                article_id,
                {foreign_key}
            )

            DO UPDATE SET
                score = GREATEST(
                    {table}.score,
                    excluded.score
                )
            """,
            (
                keep_id,
                target_id,
                link_score,
            ),
        )

    cursor.execute(
        f"""
        DELETE FROM {table}

        WHERE article_id = ?
        """,
        (
            remove_id,
        ),
    )


def find_duplicates(rows):
    """
    Conservative duplicate detection.

    A row is considered a duplicate when either:

    1. Its canonical URL matches an earlier article.
    2. Its normalized title matches an earlier article
       from the SAME source.

    Articles from different publications are deliberately
    kept even if their headlines are identical.
    """

    seen_urls = {}
    seen_source_titles = {}

    duplicates = []

    for (
        article_id,
        source,
        title,
        url,
    ) in rows:

        canonical_url = (
            canonicalize_url(url)
        )

        source_key = (
            source or ""
        ).strip().lower()

        title_key = (
            normalize_title(title)
        )

        source_title_key = (
            source_key,
            title_key,
        )

        keep_id = None
        reason = None

        if (
            canonical_url
            and canonical_url
            in seen_urls
        ):
            keep_id = (
                seen_urls[
                    canonical_url
                ]
            )

            reason = (
                "canonical URL"
            )

        elif (
            title_key
            and source_title_key
            in seen_source_titles
        ):
            keep_id = (
                seen_source_titles[
                    source_title_key
                ]
            )

            reason = (
                "same-source title"
            )

        if keep_id:

            duplicates.append({
                "keep_id":
                    keep_id,

                "remove_id":
                    article_id,

                "source":
                    source,

                "title":
                    title,

                "reason":
                    reason,
            })

            continue

        if canonical_url:
            seen_urls[
                canonical_url
            ] = article_id

        if title_key:
            seen_source_titles[
                source_title_key
            ] = article_id

    return duplicates


def main():

    connection = (
        connect_database()
    )

    cursor = (
        connection.cursor()
    )

    cursor.execute("""
        SELECT
            id,
            source,
            title,
            url

        FROM articles

        ORDER BY id ASC
    """)

    rows = (
        cursor.fetchall()
    )

    duplicates = (
        find_duplicates(rows)
    )

    print(
        f"Duplicates found: "
        f"{len(duplicates)}",
        flush=True,
    )

    if not duplicates:

        connection.close()

        print(
            "Nothing to remove.",
            flush=True,
        )

        return

    print()

    for duplicate in duplicates:

        print(
            f"KEEP #{duplicate['keep_id']} | "
            f"REMOVE #{duplicate['remove_id']} | "
            f"{duplicate['reason']} | "
            f"{duplicate['source']} | "
            f"{duplicate['title']}",
            flush=True,
        )

    print()

    try:

        removed_count = 0

        for duplicate in duplicates:

            keep_id = (
                duplicate[
                    "keep_id"
                ]
            )

            remove_id = (
                duplicate[
                    "remove_id"
                ]
            )

            merge_links(
                cursor,
                keep_id,
                remove_id,
                "article_categories",
                "category_id",
            )

            merge_links(
                cursor,
                keep_id,
                remove_id,
                "article_regions",
                "region_id",
            )

            cursor.execute(
                """
                DELETE FROM articles

                WHERE id = ?
                """,
                (
                    remove_id,
                ),
            )

            removed_count += 1

            print(
                f"Removed article "
                f"#{remove_id}",
                flush=True,
            )

        connection.commit()

        print()
        print("=" * 70)
        print(
            "DUPLICATE CLEANUP COMPLETE"
        )
        print("=" * 70)

        print(
            f"Duplicate articles removed: "
            f"{removed_count}"
        )

        print("=" * 70)

    except Exception:

        connection.rollback()

        print(
            "Cleanup failed. "
            "Transaction rolled back.",
            flush=True,
        )

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()
