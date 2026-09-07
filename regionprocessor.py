import sqlite3
from db import connect_database

from regiondetector import detect_regions

from database import (
    create_database,
    save_region,
    link_article_to_region,
    clear_regions,
    get_unprocessed_region_articles,
    mark_region_processed
)


DATABASE_NAME = "Macrodrive.db"


def get_articles():

    return get_unprocessed_region_articles()


def process_regions():

    # Make sure database tables exist
    create_database()

    # Get only articles not yet region-processed.
    articles = get_articles()

    print(
        f"\nProcessing regions for "
        f"{len(articles)} articles...\n"
    )

    articles_with_regions = 0
    articles_without_regions = 0

    # Process each article
    for article in articles:

        article_id = article[0]
        source = article[1]
        title = article[2]
        url = article[3]
        body_text = article[4] or ""

        # Detect regions
        regions = detect_regions(
            title,
            body_text
        )

        print("----------------------------------------")
        print(f"ID: {article_id}")
        print(f"Source: {source}")
        print(f"Title: {title}")

        # No region detected
        if not regions:

            print("Regions:")
            print("  - None")

            articles_without_regions += 1

            mark_region_processed(article_id)

            continue

        # At least one region detected
        articles_with_regions += 1

        print("Regions:")

        for result in regions:

            region = result["region"]
            score = result["score"]

            print(
                f"  - {region} "
                f"(score: {score})"
            )

            # Make sure region exists
            save_region(region)

            # Connect article to region
            link_article_to_region(
                url,
                region,
                score
            )

        mark_region_processed(article_id)

    # Final report
    print("\n========================================")
    print("REGION REPORT")
    print("========================================")
    print(
        f"Articles processed:     "
        f"{len(articles)}"
    )
    print(
        f"With region detected:   "
        f"{articles_with_regions}"
    )
    print(
        f"Without region:         "
        f"{articles_without_regions}"
    )
    print("========================================")


process_regions()