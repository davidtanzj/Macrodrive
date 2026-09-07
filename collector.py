from database import (
    create_database,
    save_article,
    get_existing_article_urls
)

from sources import SOURCES

from collectors import rss
from collectors import worldbank


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

    new_candidates = [
        article
        for article in articles
        if article.get("url")
        and article["url"] not in existing_urls
    ]

    new_articles = 0

    print()
    print("=" * 70)
    print("NEW ARTICLES")
    print("=" * 70)

    print(
        f"Collected: {len(articles)} | "
        f"Already known: {len(articles) - len(new_candidates)} | "
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