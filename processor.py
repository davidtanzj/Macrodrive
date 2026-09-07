import sqlite3
from db import connect_database

from classifier import classify_article

from relevance import (
    calculate_relevance
)

from database import (
    create_database,
    save_category,
    link_article_to_category,
    clear_classifications,
    get_unclassified_articles
)


DATABASE_NAME = "Macrodrive.db"


def ensure_relevance_columns():

    connection = connect_database()

    cursor = connection.cursor()

    cursor.execute("""
        PRAGMA table_info(articles)
    """)

    columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "macro_relevant" not in columns:

        cursor.execute("""
            ALTER TABLE articles
            ADD COLUMN macro_relevant INTEGER
        """)

    if "relevance_score" not in columns:

        cursor.execute("""
            ALTER TABLE articles
            ADD COLUMN relevance_score INTEGER
        """)

    connection.commit()
    connection.close()


def get_articles():

    return get_unclassified_articles()


def save_relevance(
    article_id,
    relevant,
    score,
    connection=None
):

    owns_connection = connection is None

    if owns_connection:
        connection = connect_database()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE articles

        SET
            macro_relevant = ?,
            relevance_score = ?

        WHERE id = ?
    """, (
        1 if relevant else 0,
        score,
        article_id
    ))

    if owns_connection:
        connection.commit()
        connection.close()


def process_articles():

    create_database()

    ensure_relevance_columns()

    articles = get_articles()

    relevant_count = 0
    irrelevant_count = 0
    classified_count = 0
    unclassified_relevant = 0

    print(
        f"\nProcessing "
        f"{len(articles)} NEW/UNCLASSIFIED articles...\n"
    )

    relevance_connection = connect_database()

    for index, article in enumerate(
        articles,
        start=1
    ):

        article_id = article[0]
        source = article[1]
        title = article[2]
        url = article[3]
        body_text = article[4] or ""

        print("=" * 70)

        print(
            f"ARTICLE {article_id}"
        )

        print(
            f"Source: {source}"
        )

        print(
            f"Title: {title}"
        )

        # ------------------------------------
        # RELEVANCE
        # ------------------------------------

        relevance = calculate_relevance(
            title,
            body_text
        )

        save_relevance(
            article_id,
            relevance["relevant"],
            relevance["score"],
            connection=relevance_connection
        )

        if index % 50 == 0:
            relevance_connection.commit()
            print(
                f"Database progress: "
                f"{index}/{len(articles)}",
                flush=True
            )

        if not relevance["relevant"]:

            irrelevant_count += 1

            print(
                "Status: NOT MACRO RELEVANT"
            )

            print(
                f"Relevance score: "
                f"{relevance['score']}"
            )

            continue

        relevant_count += 1

        print(
            "Status: MACRO RELEVANT"
        )

        print(
            f"Relevance score: "
            f"{relevance['score']}"
        )

        # ------------------------------------
        # CLASSIFICATION
        # ------------------------------------

        results = classify_article(
            title,
            body_text
        )

        if not results:

            unclassified_relevant += 1

            print(
                "Topics: None detected"
            )

            continue

        classified_count += 1

        print("Topics:")

        for result in results:

            category = (
                result["category"]
            )

            score = result["score"]

            print(
                f"  - {category} "
                f"(score: {score})"
            )

            save_category(
                category
            )

            link_article_to_category(
                url,
                category,
                score
            )

    relevance_connection.commit()
    relevance_connection.close()

    print()
    print("=" * 70)
    print("Macrodrive PROCESSING REPORT")
    print("=" * 70)

    print(
        f"Articles processed:       "
        f"{len(articles)}"
    )

    print(
        f"Macro relevant:           "
        f"{relevant_count}"
    )

    print(
        f"Not macro relevant:       "
        f"{irrelevant_count}"
    )

    print(
        f"Relevant + classified:    "
        f"{classified_count}"
    )

    print(
        f"Relevant but unclassified:"
        f" {unclassified_relevant}"
    )

    print("=" * 70)


if __name__ == "__main__":

    process_articles()