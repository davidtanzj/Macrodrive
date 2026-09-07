import sqlite3

from classifier import classify_article
from relevance import calculate_relevance


DATABASE_NAME = "Macrodrive.db"


connection = sqlite3.connect(
    DATABASE_NAME
)

cursor = connection.cursor()


cursor.execute("""
    SELECT
        id,
        source,
        title,
        body_text

    FROM articles

    ORDER BY id
""")


articles = cursor.fetchall()

connection.close()


for article in articles:

    article_id = article[0]
    source = article[1]
    title = article[2]
    body_text = article[3] or ""

    relevance = calculate_relevance(
        title,
        body_text
    )

    print()
    print("=" * 75)

    print(
        f"ARTICLE {article_id}"
    )

    print(
        f"Source: {source}"
    )

    print(
        f"Title: {title}"
    )

    print("-" * 75)

    # ----------------------------------------
    # RELEVANCE
    # ----------------------------------------

    if relevance["relevant"]:

        print(
            f"RELEVANT "
            f"[score: {relevance['score']}]"
        )

    else:

        print(
            f"NOT RELEVANT "
            f"[score: {relevance['score']}]"
        )

        reason = relevance.get(
            "reason"
        )

        if reason:

            print(
                f"Reason: {reason}"
            )

        continue

    # ----------------------------------------
    # CLASSIFICATION
    # ----------------------------------------

    results = classify_article(
        title,
        body_text
    )

    if not results:

        print()
        print(
            "NO TOPIC CLASSIFICATION"
        )

        continue

    print()
    print("TOPICS")

    for result in results:

        print()
        print(
            f"{result['category']} "
            f"[score: {result['score']}, "
            f"threshold: "
            f"{result['threshold']}]"
        )

        if result["bonus"]:

            print(
                f"  Concept bonus: "
                f"+{result['bonus']}"
            )

        if result["title_matches"]:

            print("  TITLE")

            for match in (
                result["title_matches"]
            ):

                print(
                    f"    "
                    f"{match['keyword']} "
                    f"+{match['points']}"
                )

        if result["opening_matches"]:

            print("  OPENING")

            for match in (
                result["opening_matches"]
            ):

                print(
                    f"    "
                    f"{match['keyword']} "
                    f"+{match['points']}"
                )

        if result["body_matches"]:

            print("  BODY")

            for match in (
                result["body_matches"]
            ):

                print(
                    f"    "
                    f"{match['keyword']} "
                    f"+{match['points']}"
                )