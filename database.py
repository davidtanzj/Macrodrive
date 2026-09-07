import sqlite3
from db import connect_database

from dateutils import normalize_date


DATABASE_NAME = "Macrodrive.db"


# ============================================================
# DATABASE SETUP
# ============================================================

def create_database():

    connection = connect_database()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            source TEXT NOT NULL,

            title TEXT NOT NULL,

            url TEXT NOT NULL UNIQUE,

            published TEXT,

            published_at TEXT,

            description TEXT,

            provided_text TEXT,

            body_text TEXT,

            text_mode TEXT DEFAULT 'full',

            access_type TEXT DEFAULT 'unknown',

            macro_relevant INTEGER,

            relevance_score INTEGER
        )
    """)

    cursor.execute("""
        PRAGMA table_info(articles)
    """)

    existing_columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    columns_to_add = {

        "published_at":
            "TEXT",

        "description":
            "TEXT",

        "provided_text":
            "TEXT",

        "body_text":
            "TEXT",

        "text_mode":
            "TEXT DEFAULT 'full'",

        "access_type":
            "TEXT DEFAULT 'unknown'",

        "macro_relevant":
            "INTEGER",

        "relevance_score":
            "INTEGER"
    }

    for (
        column_name,
        column_type
    ) in columns_to_add.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE articles
                ADD COLUMN {column_name} {column_type}
                """
            )


    # ========================================================
    # CATEGORIES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL UNIQUE
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_categories (

            article_id INTEGER NOT NULL,

            category_id INTEGER NOT NULL,

            score INTEGER NOT NULL DEFAULT 0,

            PRIMARY KEY (
                article_id,
                category_id
            )
        )
    """)


    cursor.execute("""
        PRAGMA table_info(article_categories)
    """)

    category_columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "score" not in category_columns:

        cursor.execute("""
            ALTER TABLE article_categories

            ADD COLUMN score INTEGER
            NOT NULL DEFAULT 0
        """)


    # ========================================================
    # REGIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL UNIQUE
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_regions (

            article_id INTEGER NOT NULL,

            region_id INTEGER NOT NULL,

            score INTEGER NOT NULL DEFAULT 0,

            PRIMARY KEY (
                article_id,
                region_id
            )
        )
    """)


    connection.commit()

    connection.close()


# ============================================================
# SAVE ARTICLE
# ============================================================

def save_article(article):

    connection = connect_database()

    cursor = connection.cursor()


    published_at = normalize_date(
        article.get(
            "published",
            ""
        )
    )


    text_mode = article.get(
        "text_mode",
        "full"
    )


    access_type = article.get(
        "access_type",
        "unknown"
    )


    cursor.execute("""
        INSERT OR IGNORE INTO articles (

            source,
            title,
            url,
            published,
            published_at,
            description,
            provided_text,
            text_mode,
            access_type

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        article["source"],

        article["title"],

        article["url"],

        article.get(
            "published",
            "Unknown"
        ),

        published_at,

        article.get(
            "description",
            ""
        ),

        article.get(
            "provided_text",
            ""
        ),

        text_mode,

        access_type
    ))


    was_inserted = (
        cursor.rowcount > 0
    )


    if not was_inserted:

        cursor.execute("""
            UPDATE articles

            SET

                published_at =
                    CASE
                        WHEN ? IS NOT NULL
                        THEN ?
                        ELSE published_at
                    END,

                description =
                    CASE
                        WHEN ? != ''
                        THEN ?
                        ELSE description
                    END,

                provided_text =
                    CASE
                        WHEN ? != ''
                        THEN ?
                        ELSE provided_text
                    END,

                text_mode = ?,

                access_type =
                    CASE

                        WHEN access_type
                             IN ('free', 'paywalled')

                        AND ? = 'unknown'

                        THEN access_type

                        ELSE ?

                    END

            WHERE url = ?
        """, (

            published_at,
            published_at,

            article.get(
                "description",
                ""
            ),

            article.get(
                "description",
                ""
            ),

            article.get(
                "provided_text",
                ""
            ),

            article.get(
                "provided_text",
                ""
            ),

            text_mode,

            access_type,

            access_type,

            article["url"]
        ))


    connection.commit()

    connection.close()


    return was_inserted


# ============================================================
# UPDATE ACCESS STATUS
# ============================================================

def update_article_access(
    article_id,
    access_type
):

    if access_type not in (
        "free",
        "paywalled",
        "unknown"
    ):

        return


    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        UPDATE articles

        SET access_type = ?

        WHERE id = ?
    """, (
        access_type,
        article_id
    ))


    connection.commit()

    connection.close()


# ============================================================
# NORMALIZE DATES
# ============================================================

def normalize_existing_dates():

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            id,
            published

        FROM articles

        WHERE published_at IS NULL
           OR published_at = ''
    """)


    articles = cursor.fetchall()


    updated = 0
    failed = 0


    for (
        article_id,
        published
    ) in articles:


        normalized = normalize_date(
            published
        )


        if normalized:

            cursor.execute("""
                UPDATE articles

                SET published_at = ?

                WHERE id = ?
            """, (
                normalized,
                article_id
            ))

            updated += 1

        else:

            failed += 1


    connection.commit()

    connection.close()


    return updated, failed


# ============================================================
# TEXT PROCESSING
# ============================================================

def get_articles_without_text():

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            id,
            source,
            title,
            url,
            provided_text,
            description,
            text_mode,
            access_type

        FROM articles

        WHERE body_text IS NULL
           OR body_text = ''
    """)


    articles = cursor.fetchall()


    connection.close()


    return articles


def save_article_text(
    article_id,
    body_text
):

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        UPDATE articles

        SET body_text = ?

        WHERE id = ?
    """, (
        body_text,
        article_id
    ))


    connection.commit()

    connection.close()


# ============================================================
# CATEGORY FUNCTIONS
# ============================================================

def save_category(
    category_name
):

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        INSERT OR IGNORE INTO categories (
            name
        )

        VALUES (?)
    """, (
        category_name,
    ))


    connection.commit()

    connection.close()


def link_article_to_category(
    article_url,
    category_name,
    score
):

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT id

        FROM articles

        WHERE url = ?
    """, (
        article_url,
    ))


    article = cursor.fetchone()


    cursor.execute("""
        SELECT id

        FROM categories

        WHERE name = ?
    """, (
        category_name,
    ))


    category = cursor.fetchone()


    if article and category:

        cursor.execute("""
            INSERT INTO article_categories (
                article_id,
                category_id,
                score
            )

            VALUES (?, ?, ?)

            ON CONFLICT (
                article_id,
                category_id
            )

            DO UPDATE SET
                score = excluded.score
        """, (
            article[0],
            category[0],
            score
        ))


    connection.commit()

    connection.close()


def clear_classifications():

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        DELETE FROM article_categories
    """)


    cursor.execute("""
        DELETE FROM categories
    """)


    connection.commit()

    connection.close()


# ============================================================
# REGION FUNCTIONS
# ============================================================

def save_region(
    region_name
):

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        INSERT OR IGNORE INTO regions (
            name
        )

        VALUES (?)
    """, (
        region_name,
    ))


    connection.commit()

    connection.close()


def link_article_to_region(
    article_url,
    region_name,
    score
):

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT id

        FROM articles

        WHERE url = ?
    """, (
        article_url,
    ))


    article = cursor.fetchone()


    cursor.execute("""
        SELECT id

        FROM regions

        WHERE name = ?
    """, (
        region_name,
    ))


    region = cursor.fetchone()


    if article and region:

        cursor.execute("""
            INSERT INTO article_regions (
                article_id,
                region_id,
                score
            )

            VALUES (?, ?, ?)

            ON CONFLICT (
                article_id,
                region_id
            )

            DO UPDATE SET
                score = excluded.score
        """, (
            article[0],
            region[0],
            score
        ))

    # ========================================================
    # CALENDAR EVENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            event_key TEXT NOT NULL UNIQUE,

            country TEXT NOT NULL,

            region TEXT,

            event_name TEXT NOT NULL,

            event_type TEXT,

            scheduled_at TEXT NOT NULL,

            importance INTEGER DEFAULT 1,

            previous TEXT,

            consensus TEXT,

            actual TEXT,

            unit TEXT,

            source TEXT,

            source_url TEXT,

            status TEXT DEFAULT 'scheduled',

            created_at TEXT,

            updated_at TEXT
        )
    """)
    connection.commit()

    connection.close()


def clear_regions():

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        DELETE FROM article_regions
    """)


    cursor.execute("""
        DELETE FROM regions
    """)


    connection.commit()

    connection.close()