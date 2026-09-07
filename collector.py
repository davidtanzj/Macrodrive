from database import (
    create_database,
    save_article
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

    new_articles = 0

    print()
    print("=" * 70)
    print("NEW ARTICLES")
    print("=" * 70)

    for article in articles:

        if save_article(article):

            new_articles += 1

            print()
            print(
                f"Source: "
                f"{article['source']}"
            )

            print(
                f"Title: "
                f"{article['title']}"
            )

            print(
                f"Access: "
                f"{article['access_type']}"
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