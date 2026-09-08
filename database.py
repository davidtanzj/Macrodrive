import json
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

            relevance_score INTEGER,
            region_processed INTEGER DEFAULT 0
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
            "INTEGER",

        "region_processed":
            "INTEGER DEFAULT 0"
    }

    region_processed_added = (
        "region_processed" not in existing_columns
    )

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

    if region_processed_added:
        cursor.execute("""
            UPDATE articles
            SET region_processed = 1
        """)


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


    # ========================================================
    # DAILY AI MARKET BRIEFS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_briefs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            brief_date TEXT NOT NULL UNIQUE,

            headline TEXT NOT NULL,

            teaser TEXT NOT NULL,

            sections_json TEXT NOT NULL,

            what_to_watch_json TEXT NOT NULL,

            trending_topics_json TEXT NOT NULL,

            trending_regions_json TEXT NOT NULL,

            articles_analyzed INTEGER NOT NULL DEFAULT 0,

            sources_analyzed INTEGER NOT NULL DEFAULT 0,

            generated_at TEXT NOT NULL
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
# INCREMENTAL ARTICLE HELPERS
# ============================================================

def get_existing_article_urls():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("SELECT url FROM articles")
    urls = {row[0] for row in cursor.fetchall() if row[0]}
    connection.close()
    return urls


def get_unclassified_articles():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, source, title, url, body_text
        FROM articles
        WHERE macro_relevant IS NULL
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_unprocessed_region_articles():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, source, title, url, body_text
        FROM articles
        WHERE COALESCE(region_processed, 0) = 0
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows


def mark_region_processed(article_id):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE articles
        SET region_processed = 1
        WHERE id = ?
    """, (article_id,))
    connection.commit()
    connection.close()


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

# ============================================================
# DAILY BRIEF FUNCTIONS
# ============================================================

def save_daily_brief(brief):
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO daily_briefs (
            brief_date,
            headline,
            teaser,
            sections_json,
            what_to_watch_json,
            trending_topics_json,
            trending_regions_json,
            articles_analyzed,
            sources_analyzed,
            generated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT (brief_date)
        DO UPDATE SET
            headline = excluded.headline,
            teaser = excluded.teaser,
            sections_json = excluded.sections_json,
            what_to_watch_json = excluded.what_to_watch_json,
            trending_topics_json = excluded.trending_topics_json,
            trending_regions_json = excluded.trending_regions_json,
            articles_analyzed = excluded.articles_analyzed,
            sources_analyzed = excluded.sources_analyzed,
            generated_at = excluded.generated_at
    """, (
        brief["brief_date"],
        brief["headline"],
        brief["teaser"],
        json.dumps(brief["sections"], ensure_ascii=False),
        json.dumps(brief["what_to_watch"], ensure_ascii=False),
        json.dumps(brief["trending_topics"], ensure_ascii=False),
        json.dumps(brief["trending_regions"], ensure_ascii=False),
        brief["articles_analyzed"],
        brief["sources_analyzed"],
        brief["generated_at"],
    ))

    connection.commit()
    connection.close()


def get_latest_daily_brief():
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            brief_date,
            headline,
            teaser,
            sections_json,
            what_to_watch_json,
            trending_topics_json,
            trending_regions_json,
            articles_analyzed,
            sources_analyzed,
            generated_at
        FROM daily_briefs
        ORDER BY brief_date DESC, generated_at DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    connection.close()

    if not row:
        return None

    return {
        "brief_date": row[0],
        "headline": row[1],
        "teaser": row[2],
        "sections": json.loads(row[3]),
        "what_to_watch": json.loads(row[4]),
        "trending_topics": json.loads(row[5]),
        "trending_regions": json.loads(row[6]),
        "articles_analyzed": row[7],
        "sources_analyzed": row[8],
        "generated_at": row[9],
    }
