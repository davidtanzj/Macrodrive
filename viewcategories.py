import sqlite3


connection = sqlite3.connect("Macrodrive.db")

cursor = connection.cursor()


cursor.execute("""
    SELECT
        articles.id,
        articles.title,
        categories.name,
        article_categories.score

    FROM article_categories

    JOIN articles
        ON article_categories.article_id = articles.id

    JOIN categories
        ON article_categories.category_id = categories.id

    ORDER BY
        articles.id,
        article_categories.score DESC
""")


results = cursor.fetchall()


current_id = None


for article_id, title, category, score in results:

    if article_id != current_id:

        print("\n========================================")
        print(f"ARTICLE {article_id}")
        print(title)
        print("----------------------------------------")

        current_id = article_id

    print(
        f"{category}: {score}"
    )


connection.close()