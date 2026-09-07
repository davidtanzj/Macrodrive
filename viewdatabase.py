import sqlite3


connection = sqlite3.connect("Macrodrive.db")

cursor = connection.cursor()


cursor.execute("""
    SELECT id, source, title, published
    FROM articles
    ORDER BY id DESC
""")


articles = cursor.fetchall()


print(f"\nMacrodrive currently has {len(articles)} articles.\n")


for article in articles:

    article_id = article[0]
    source = article[1]
    title = article[2]
    published = article[3]

    print("----------------------------------------")
    print(f"ID:        {article_id}")
    print(f"Source:    {source}")
    print(f"Title:     {title}")
    print(f"Published: {published}")


connection.close()