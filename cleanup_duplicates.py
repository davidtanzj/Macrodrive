import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from db import connect_database

TRACKING_QUERY_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term",
    "utm_content", "utm_id", "gclid", "fbclid", "mc_cid",
    "mc_eid", "cmpid", "campaign_id", "campaign"
}


def canonicalize_url(url):
    if not url:
        return ""
    parts = urlsplit(url.strip())
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in TRACKING_QUERY_KEYS
    ]
    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip("/") or "/",
        urlencode(query, doseq=True),
        ""
    ))


def normalize_title(title):
    title = (title or "").lower()
    title = re.sub(r"[^\w\s]", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def merge_links(cursor, keep_id, remove_id, table, foreign_key):
    cursor.execute(
        f"SELECT {foreign_key}, score FROM {table} WHERE article_id = ?",
        (remove_id,)
    )
    for target_id, score in cursor.fetchall():
        cursor.execute(
            f"""
            INSERT INTO {table} (article_id, {foreign_key}, score)
            VALUES (?, ?, ?)
            ON CONFLICT(article_id, {foreign_key})
            DO UPDATE SET score = GREATEST(
            {table}.score,
            excluded.score
)
            """,
            (keep_id, target_id, score)
        )
    cursor.execute(
        f"DELETE FROM {table} WHERE article_id = ?",
        (remove_id,)
    )


def main():
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, source, title, url
        FROM articles
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()

    seen_urls = {}
    seen_titles = {}
    duplicates = []

    for article_id, source, title, url in rows:
        canonical = canonicalize_url(url)
        title_key = (
            (source or "").strip().lower(),
            normalize_title(title)
        )

        keep_id = None
        reason = None

        if canonical and canonical in seen_urls:
            keep_id = seen_urls[canonical]
            reason = "canonical URL"
        elif title_key[1] and title_key in seen_titles:
            keep_id = seen_titles[title_key]
            reason = "same-source title"

        if keep_id:
            duplicates.append(
                (keep_id, article_id, source, title, reason)
            )
            continue

        if canonical:
            seen_urls[canonical] = article_id
        if title_key[1]:
            seen_titles[title_key] = article_id

    print(f"Duplicates found: {len(duplicates)}", flush=True)

    try:
        for keep_id, remove_id, source, title, reason in duplicates:
            merge_links(
                cursor, keep_id, remove_id,
                "article_categories", "category_id"
            )
            merge_links(
                cursor, keep_id, remove_id,
                "article_regions", "region_id"
            )
            cursor.execute(
                "DELETE FROM articles WHERE id = ?",
                (remove_id,)
            )
            print(
                f"Removed #{remove_id} ({reason}) "
                f"[{source}] {title}",
                flush=True
            )

        connection.commit()
        print(f"Removed {len(duplicates)} duplicate articles.", flush=True)

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
