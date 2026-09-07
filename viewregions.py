import sqlite3


DATABASE_NAME = "Macrodrive.db"


connection = sqlite3.connect(DATABASE_NAME)

cursor = connection.cursor()


cursor.execute("""
    SELECT
        articles.id,
        articles.title,
        regions.name,
        article_regions.score

    FROM article_regions

    JOIN articles
        ON article_regions.article_id = articles.id

    JOIN regions
        ON article_regions.region_id = regions.id

    ORDER BY
        articles.id,
        article_regions.score DESC
""")


results = cursor.fetchall()


connection.close()


current_id = None


for article_id, title, region, score in results:

    if article_id != current_id:

        print("\n========================================")
        print(f"ARTICLE {article_id}")
        print(title)
        print("----------------------------------------")

        current_id = article_id

    print(
        f"{region}: {score}"
    )