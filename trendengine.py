from collections import defaultdict
from datetime import datetime, timezone, timedelta

from db import connect_database


LOOKBACK_HOURS = 24
TOP_TOPIC_COUNT = 3
TOP_REGION_COUNT = 3
REPRESENTATIVE_ARTICLES_PER_TOPIC = 3


def parse_timestamp(value):
    if not value:
        return None

    try:
        dt = datetime.fromisoformat(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc)

    except (TypeError, ValueError):
        return None


def recency_weight(published_at, now):
    age_hours = max(
        0.0,
        (now - published_at).total_seconds() / 3600
    )

    # Recent stories receive a modest boost without overwhelming
    # frequency and source diversity.
    return max(
        0.25,
        1.0 - (age_hours / (LOOKBACK_HOURS * 1.35))
    )


def load_recent_articles():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=LOOKBACK_HOURS)

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            source,
            title,
            url,
            published_at,
            description,
            relevance_score
        FROM articles
        WHERE macro_relevant = 1
          AND published_at IS NOT NULL
          AND published_at >= ?
          AND published_at <= ?
        ORDER BY published_at DESC, id DESC
    """, (
        cutoff.isoformat(),
        now.isoformat()
    ))

    rows = cursor.fetchall()

    articles = []

    for row in rows:
        article_id = row[0]

        cursor.execute("""
            SELECT
                categories.name,
                article_categories.score
            FROM article_categories
            JOIN categories
                ON categories.id =
                   article_categories.category_id
            WHERE article_categories.article_id = ?
            ORDER BY article_categories.score DESC
        """, (article_id,))

        topics = [
            {
                "name": topic_row[0],
                "score": topic_row[1] or 0
            }
            for topic_row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT
                regions.name,
                article_regions.score
            FROM article_regions
            JOIN regions
                ON regions.id =
                   article_regions.region_id
            WHERE article_regions.article_id = ?
            ORDER BY article_regions.score DESC
        """, (article_id,))

        regions = [
            {
                "name": region_row[0],
                "score": region_row[1] or 0
            }
            for region_row in cursor.fetchall()
        ]

        published_at = parse_timestamp(row[4])

        if not published_at:
            continue

        articles.append({
            "id": article_id,
            "source": row[1],
            "title": row[2],
            "url": row[3],
            "published_at": published_at,
            "description": row[5] or "",
            "relevance_score": row[6] or 0,
            "topics": topics,
            "regions": regions
        })

    connection.close()

    return articles, now


def build_rankings(articles, now):
    topic_data = defaultdict(
        lambda: {
            "articles": [],
            "sources": set(),
            "raw_score": 0.0
        }
    )

    region_data = defaultdict(
        lambda: {
            "articles": [],
            "sources": set(),
            "raw_score": 0.0
        }
    )

    for article in articles:
        recency = recency_weight(
            article["published_at"],
            now
        )

        # Keep relevance useful but bounded so one unusually high
        # relevance score cannot dominate an entire daily trend.
        relevance = min(
            max(article["relevance_score"], 0),
            30
        )

        relevance_factor = 1.0 + (
            relevance / 60.0
        )

        for topic in article["topics"]:
            item = topic_data[topic["name"]]
            item["articles"].append(article)
            item["sources"].add(article["source"])

            classifier_factor = 1.0 + min(
                max(topic["score"], 0),
                40
            ) / 100.0

            item["raw_score"] += (
                recency
                * relevance_factor
                * classifier_factor
            )

        for region in article["regions"]:
            item = region_data[region["name"]]
            item["articles"].append(article)
            item["sources"].add(article["source"])

            region_factor = 1.0 + min(
                max(region["score"], 0),
                30
            ) / 100.0

            item["raw_score"] += (
                recency
                * relevance_factor
                * region_factor
            )

    def finalize(data):
        results = []

        for name, item in data.items():
            article_count = len(item["articles"])
            source_count = len(item["sources"])

            # Source diversity matters: a theme covered by five
            # publications should outrank one driven by a single feed.
            diversity_bonus = 1.0 + min(
                source_count,
                8
            ) * 0.12

            final_score = (
                item["raw_score"]
                * diversity_bonus
            )

            results.append({
                "name": name,
                "score": round(final_score, 2),
                "article_count": article_count,
                "source_count": source_count,
                "articles": item["articles"]
            })

        results.sort(
            key=lambda item: (
                item["score"],
                item["source_count"],
                item["article_count"]
            ),
            reverse=True
        )

        return results

    return (
        finalize(topic_data),
        finalize(region_data)
    )


def representative_articles(topic, now):
    ranked = []

    for article in topic["articles"]:
        recency = recency_weight(
            article["published_at"],
            now
        )

        relevance = min(
            max(article["relevance_score"], 0),
            30
        )

        score = (
            recency
            * (1.0 + relevance / 30.0)
        )

        ranked.append(
            (score, article)
        )

    ranked.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected = []
    used_sources = set()

    # First pass prioritizes source diversity.
    for _, article in ranked:
        if article["source"] in used_sources:
            continue

        selected.append(article)
        used_sources.add(article["source"])

        if len(selected) >= REPRESENTATIVE_ARTICLES_PER_TOPIC:
            return selected

    # Fill remaining slots if the trend has fewer distinct sources.
    selected_ids = {
        article["id"]
        for article in selected
    }

    for _, article in ranked:
        if article["id"] in selected_ids:
            continue

        selected.append(article)

        if len(selected) >= REPRESENTATIVE_ARTICLES_PER_TOPIC:
            break

    return selected


def analyze_trends():
    articles, now = load_recent_articles()

    topics, regions = build_rankings(
        articles,
        now
    )

    return {
        "generated_at": now,
        "article_count": len(articles),
        "source_count": len({
            article["source"]
            for article in articles
        }),
        "topics": topics[:TOP_TOPIC_COUNT],
        "regions": regions[:TOP_REGION_COUNT]
    }


def print_report():
    report = analyze_trends()

    print()
    print("=" * 72)
    print("MACRODRIVE DAILY TREND ANALYSIS")
    print("=" * 72)
    print(
        f"Lookback: {LOOKBACK_HOURS} hours"
    )
    print(
        f"Macro articles analysed: "
        f"{report['article_count']}"
    )
    print(
        f"Distinct sources: "
        f"{report['source_count']}"
    )

    print()
    print("TOP TOPICS")
    print("-" * 72)

    if not report["topics"]:
        print("No topic trends found.")

    for index, topic in enumerate(
        report["topics"],
        start=1
    ):
        print(
            f"{index}. {topic['name']}"
        )
        print(
            f"   Trend score: "
            f"{topic['score']}"
        )
        print(
            f"   Articles: "
            f"{topic['article_count']} | "
            f"Sources: "
            f"{topic['source_count']}"
        )

    print()
    print("TOP REGIONS")
    print("-" * 72)

    if not report["regions"]:
        print("No region trends found.")

    for index, region in enumerate(
        report["regions"],
        start=1
    ):
        print(
            f"{index}. {region['name']} | "
            f"score {region['score']} | "
            f"{region['article_count']} articles | "
            f"{region['source_count']} sources"
        )

    print()
    print("REPRESENTATIVE HEADLINES")
    print("=" * 72)

    now = report["generated_at"]

    for topic in report["topics"]:
        print()
        print(topic["name"])
        print("-" * len(topic["name"]))

        selected = representative_articles(
            topic,
            now
        )

        for article in selected:
            print(
                f"- [{article['source']}] "
                f"{article['title']}"
            )

            if article["description"]:
                description = (
                    article["description"]
                    .replace("\n", " ")
                    .strip()
                )

                if len(description) > 220:
                    description = (
                        description[:217]
                        + "..."
                    )

                print(
                    f"  {description}"
                )

    print()
    print("=" * 72)


if __name__ == "__main__":
    print_report()
