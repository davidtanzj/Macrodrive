import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from database import (
    create_database,
    save_article,
    get_existing_article_urls
)

from sources import SOURCES

from collectors import rss
from collectors import worldbank



TRACKING_QUERY_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term",
    "utm_content", "utm_id", "gclid", "fbclid", "mc_cid",
    "mc_eid", "cmpid", "campaign_id", "campaign"
}


def canonicalize_url(url):
    """Normalize URLs for duplicate detection without changing stored URLs."""
    if not url:
        return ""

    try:
        parts = urlsplit(url.strip())

        query = [
            (key, value)
            for key, value in parse_qsl(
                parts.query,
                keep_blank_values=True
            )
            if key.lower() not in TRACKING_QUERY_KEYS
        ]

        path = parts.path.rstrip("/") or "/"

        return urlunsplit((
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            urlencode(query, doseq=True),
            ""  # fragments never identify a different article
        ))

    except Exception:
        return url.strip()


def normalize_title(title):
    """Conservative same-source title key for exact duplicate headlines."""
    if not title:
        return ""

    title = title.lower()
    title = re.sub(r"[^\w\s]", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def deduplicate_candidates(articles, existing_urls):
    """
    Remove:
    1. exact/canonical URL duplicates;
    2. duplicate normalized titles from the SAME source in this collection.

    Cross-publication stories are deliberately retained.
    """
    existing_canonical = {
        canonicalize_url(url)
        for url in existing_urls
        if url
    }

    seen_urls = set(existing_canonical)
    seen_source_titles = set()
    unique = []
    skipped_url = 0
    skipped_title = 0

    for article in articles:
        url = article.get("url", "")
        canonical = canonicalize_url(url)

        if not canonical or canonical in seen_urls:
            skipped_url += 1
            continue

        source = (article.get("source") or "").strip().lower()
        title_key = normalize_title(article.get("title", ""))
        source_title_key = (source, title_key)

        if title_key and source_title_key in seen_source_titles:
            skipped_title += 1
            continue

        seen_urls.add(canonical)

        if title_key:
            seen_source_titles.add(source_title_key)

        unique.append(article)

    return unique, skipped_url, skipped_title


def collect_source(source):

    source_type = source.get(
        "type"
    )

    if source_type == "rss":

        articles = rss.collect(
            source
        )

    elif (
        source_type
        == "worldbank_api"
    ):

        articles = worldbank.collect(
            source
        )

    else:

        print(
            f"\nUnknown source type: "
            f"{source_type}"
        )

        return []

    text_mode = source.get(
        "text_mode",
        "full"
    )

    access_type = source.get(
        "access_type",
        "unknown"
    )

    for article in articles:

        article["text_mode"] = (
            text_mode
        )

        article["access_type"] = (
            access_type
        )

    return articles


def collect_articles():

    all_articles = []

    for source in SOURCES:

        if not source.get(
            "enabled",
            True
        ):
            continue

        source_name = source.get(
            "name",
            "Unknown source"
        )

        print(
            f"Fetching: {source_name}...",
            flush=True
        )

        articles = collect_source(
            source
        )

        print(
            f"  Found {len(articles)} articles.",
            flush=True
        )

        all_articles.extend(
            articles
        )

    return all_articles


def run_collector():

    create_database()

    articles = collect_articles()

    existing_urls = get_existing_article_urls()

    (
        new_candidates,
        skipped_url_duplicates,
        skipped_title_duplicates
    ) = deduplicate_candidates(
        articles,
        existing_urls
    )

    new_articles = 0

    print()
    print("=" * 70)
    print("NEW ARTICLES")
    print("=" * 70)

    print(
        f"Collected: {len(articles)} | "
        f"URL duplicates: {skipped_url_duplicates} | "
        f"Same-source title duplicates: {skipped_title_duplicates} | "
        f"New candidates: {len(new_candidates)}",
        flush=True
    )

    for index, article in enumerate(new_candidates, start=1):

        if save_article(article):
            new_articles += 1
            print(
                f"[{index}/{len(new_candidates)}] "
                f"{article['source']}: {article['title']}",
                flush=True
            )

    print()
    print("=" * 70)
    print(
        "Macrodrive COLLECTION REPORT"
    )
    print("=" * 70)

    print(
        f"Articles processed: "
        f"{len(articles)}"
    )

    print(
        f"New articles saved: "
        f"{new_articles}"
    )

    print("=" * 70)


if __name__ == "__main__":

    run_collector()