from db import connect_database

SOURCES_TO_REMOVE = (
    "Econbrowser",
    "Calculated Risk",
    "Marginal Revolution",
)


def remove_sources():
    connection = connect_database()
    cursor = connection.cursor()

    placeholders = ", ".join(
        "?" for _ in SOURCES_TO_REMOVE
    )

    cursor.execute(
        f"""
        SELECT id, source, title
        FROM articles
        WHERE source IN ({placeholders})
        ORDER BY source, id
        """,
        SOURCES_TO_REMOVE
    )

    articles = cursor.fetchall()
    article_ids = [row[0] for row in articles]

    print(
        f"Found {len(articles)} articles to remove.",
        flush=True
    )

    for source in SOURCES_TO_REMOVE:
        count = sum(
            1 for row in articles
            if row[1] == source
        )
        print(
            f"{source}: {count}",
            flush=True
        )

    if not article_ids:
        connection.close()
        print("Nothing to remove.", flush=True)
        return

    id_placeholders = ", ".join(
        "?" for _ in article_ids
    )

    try:
        cursor.execute(
            f"""
            DELETE FROM article_categories
            WHERE article_id IN ({id_placeholders})
            """,
            tuple(article_ids)
        )
        category_links = cursor.rowcount

        cursor.execute(
            f"""
            DELETE FROM article_regions
            WHERE article_id IN ({id_placeholders})
            """,
            tuple(article_ids)
        )
        region_links = cursor.rowcount

        cursor.execute(
            f"""
            DELETE FROM articles
            WHERE id IN ({id_placeholders})
            """,
            tuple(article_ids)
        )
        removed_articles = cursor.rowcount

        connection.commit()

        print()
        print("=" * 60)
        print("SOURCE CLEANUP COMPLETE")
        print("=" * 60)
        print(f"Articles removed:       {removed_articles}")
        print(f"Category links removed: {category_links}")
        print(f"Region links removed:   {region_links}")
        print("=" * 60)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    remove_sources()
