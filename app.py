from macrocalendar import (
    create_calendar_database,
    get_calendar_events,
    get_calendar_countries
)

import sqlite3
from db import connect_database, using_postgres
import re

from datetime import (
    datetime,
    timezone,
    timedelta
)

from flask import (
    Flask,
    render_template,
    request
)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from urllib.parse import urlsplit

from database import (
    create_database,
    normalize_existing_dates,
    get_latest_daily_brief
)


app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["120 per minute"],
    storage_uri="memory://"
)

print(
    "DATABASE BACKEND:",
    "PostgreSQL" if using_postgres() else "SQLite",
    flush=True
)

def initialize_application_database():
    create_database()
    create_calendar_database()
    normalize_existing_dates()


initialize_application_database()


DATABASE_NAME = "Macrodrive.db"


# ============================================================
# SECURITY
# ============================================================

MAX_SEARCH_QUERY_LENGTH = 200


def safe_external_url(url):
    if not url:
        return ""

    try:
        parsed = urlsplit(url.strip())

        if parsed.scheme not in ("http", "https"):
            return ""

        if not parsed.netloc:
            return ""

        return url.strip()

    except (TypeError, ValueError):
        return ""


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )

    if request.is_secure:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


# ============================================================
# DATE DISPLAY
# ============================================================

def format_date(
    published_at,
    original_date
):

    if published_at:

        try:

            dt = datetime.fromisoformat(
                published_at
            )

            return dt.strftime(
                "%d %b %Y · %H:%M UTC"
            )

        except ValueError:

            pass


    if (
        original_date
        and original_date != "Unknown"
    ):

        return original_date


    return "Date unavailable"


# ============================================================
# FILTER OPTIONS
# ============================================================

def get_filter_options():

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT DISTINCT
            categories.name

        FROM categories

        JOIN article_categories
            ON categories.id
            = article_categories.category_id

        JOIN articles
            ON articles.id
            = article_categories.article_id

        WHERE
            articles.macro_relevant = 1

        ORDER BY
            categories.name
    """)


    topics = [
        row[0]
        for row in cursor.fetchall()
    ]


    cursor.execute("""
        SELECT DISTINCT
            regions.name

        FROM regions

        JOIN article_regions
            ON regions.id
            = article_regions.region_id

        JOIN articles
            ON articles.id
            = article_regions.article_id

        WHERE
            articles.macro_relevant = 1

        ORDER BY
            regions.name
    """)


    regions = [
        row[0]
        for row in cursor.fetchall()
    ]


    cursor.execute("""
        SELECT DISTINCT
            source

        FROM articles

        WHERE
            macro_relevant = 1

        ORDER BY
            source
    """)


    sources = [
        row[0]
        for row in cursor.fetchall()
    ]


    connection.close()


    return (
        topics,
        regions,
        sources
    )


# ============================================================
# ARTICLE CATEGORIES
# ============================================================

def get_article_categories(
    cursor,
    article_id
):

    cursor.execute("""
        SELECT
            categories.name

        FROM article_categories

        JOIN categories
            ON categories.id
            = article_categories.category_id

        WHERE
            article_categories.article_id = ?

        ORDER BY
            article_categories.score DESC
    """, (
        article_id,
    ))


    return [
        row["name"]
        for row in cursor.fetchall()
    ]


# ============================================================
# ARTICLE REGIONS
# ============================================================

def get_article_regions(
    cursor,
    article_id
):

    cursor.execute("""
        SELECT
            regions.name

        FROM article_regions

        JOIN regions
            ON regions.id
            = article_regions.region_id

        WHERE
            article_regions.article_id = ?

        ORDER BY
            article_regions.score DESC
    """, (
        article_id,
    ))


    return [
        row["name"]
        for row in cursor.fetchall()
    ]


# ============================================================
# BUILD ARTICLE
# ============================================================

def build_article(
    cursor,
    row,
    search_score=None
):

    article_id = row["id"]


    categories = (
        get_article_categories(
            cursor,
            article_id
        )
    )


    regions = (
        get_article_regions(
            cursor,
            article_id
        )
    )


    body_text = (
        row["body_text"] or ""
    )


    access_type = (
        row["access_type"]
        or "unknown"
    )


    # AI summaries will only be allowed when:
    #
    # 1. The article is confirmed free.
    # 2. We have substantial article text.

    can_summarize = (
        access_type == "free"
        and len(body_text) >= 500
    )


    return {

        "id":
            article_id,

        "source":
            row["source"],

        "title":
            row["title"],

        "url":
            safe_external_url(
                row["url"]
            ),

        "published_at":
            row["published_at"],

        "display_date":
            format_date(
                row["published_at"],
                row["published"]
            ),

        "description":
            row["description"] or "",

        "categories":
            categories,

        "regions":
            regions,

        "access_type":
            access_type,

        "is_paywalled":
            access_type == "paywalled",

        "can_summarize":
            can_summarize,

        "search_score":
            search_score
    }


# ============================================================
# BROWSE ARTICLES
# ============================================================

def get_browse_articles():

    now = datetime.now(
        timezone.utc
    )


    cutoff = (
        now
        - timedelta(
            days=183
        )
    )


    connection = connect_database()


    connection.row_factory = (
        sqlite3.Row
    )


    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            id,
            source,
            title,
            url,
            published,
            published_at,
            description,
            body_text,
            access_type

        FROM articles

        WHERE
            macro_relevant = 1

            AND published_at IS NOT NULL

            AND published_at >= ?

            AND published_at <= ?

        ORDER BY
            published_at DESC,
            id DESC
    """, (
        cutoff.isoformat(),
        now.isoformat()
    ))


    rows = cursor.fetchall()


    articles = [

        build_article(
            cursor,
            row
        )

        for row in rows
    ]


    connection.close()


    return articles


# ============================================================
# SEARCH
# ============================================================

def tokenize_search(
    query
):

    words = re.findall(
        r"[a-zA-Z0-9]+",
        query.lower()
    )


    return list(
        dict.fromkeys(
            words
        )
    )


def count_term(
    text,
    term
):

    if not text:

        return 0


    return text.lower().count(
        term
    )


def calculate_search_score(
    row,
    categories,
    regions,
    terms
):

    title = (
        row["title"] or ""
    ).lower()


    description = (
        row["description"] or ""
    ).lower()


    body = (
        row["body_text"] or ""
    ).lower()


    source = (
        row["source"] or ""
    ).lower()


    category_text = (
        " ".join(
            categories
        ).lower()
    )


    region_text = (
        " ".join(
            regions
        ).lower()
    )


    searchable_text = " ".join([
        title,
        description,
        body,
        source,
        category_text,
        region_text
    ])


    for term in terms:

        if term not in searchable_text:

            return None


    score = 0


    for term in terms:


        score += (
            count_term(
                title,
                term
            )
            * 20
        )


        score += (
            count_term(
                description,
                term
            )
            * 10
        )


        score += (
            count_term(
                category_text,
                term
            )
            * 8
        )


        score += (
            count_term(
                region_text,
                term
            )
            * 8
        )


        score += (
            count_term(
                source,
                term
            )
            * 6
        )


        score += (
            min(
                count_term(
                    body,
                    term
                ),
                5
            )
            * 2
        )


    full_query = " ".join(
        terms
    )


    if full_query in title:

        score += 40


    elif full_query in description:

        score += 20


    return score


def search_articles(
    search_query
):

    terms = tokenize_search(
        search_query
    )


    if not terms:

        return []


    connection = connect_database()


    connection.row_factory = (
        sqlite3.Row
    )


    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            id,
            source,
            title,
            url,
            published,
            published_at,
            description,
            body_text,
            access_type

        FROM articles

        WHERE
            macro_relevant = 1
    """)


    rows = cursor.fetchall()


    results = []


    for row in rows:


        article_id = row["id"]


        categories = (
            get_article_categories(
                cursor,
                article_id
            )
        )


        regions = (
            get_article_regions(
                cursor,
                article_id
            )
        )


        score = (
            calculate_search_score(
                row,
                categories,
                regions,
                terms
            )
        )


        if score is None:

            continue


        article = (
            build_article(
                cursor,
                row,
                search_score=score
            )
        )


        results.append(
            article
        )


    results.sort(
        key=lambda article: (
            article["search_score"],
            article["published_at"]
            or ""
        ),
        reverse=True
    )


    connection.close()


    return results


# ============================================================
# HOME
# ============================================================

@app.route("/")
@limiter.limit("30 per minute")
def home():

    search_query = (
        request.args.get(
            "q",
            ""
        ).strip()[
            :MAX_SEARCH_QUERY_LENGTH
        ]
    )


    if search_query:


        articles = (
            search_articles(
                search_query
            )
        )


        search_mode = True


    else:


        articles = (
            get_browse_articles()
        )


        search_mode = False


    (
        topics,
        regions,
        sources
    ) = get_filter_options()

    daily_brief = get_latest_daily_brief()


    return render_template(

        "index.html",

        articles=articles,

        topics=topics,

        regions=regions,

        sources=sources,

        search_query=search_query,

        search_mode=search_mode,

        daily_brief=daily_brief
    )

# ============================================================
# CALENDAR
# ============================================================

@app.route("/calendar")
def calendar_page():

    create_calendar_database()

    events = get_calendar_events()

    countries = (
        get_calendar_countries()
    )

    return render_template(
        "calendar.html",
        events=events,
        countries=countries
    )
# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=False
    )