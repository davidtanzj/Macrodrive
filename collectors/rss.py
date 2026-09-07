import re
import html

import feedparser
import requests
import certifi


HEADERS = {
    "User-Agent": "Macrodrive/1.0"
}


# ============================================================
# CLEAN RSS TEXT
# ============================================================

def clean_html_text(text):

    if not text:
        return ""

    # Decode things such as &amp;
    text = html.unescape(text)

    # Remove HTML tags
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Collapse whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# COLLECT RSS SOURCE
# ============================================================

def collect(source):

    name = source["name"]
    feed_url = source["url"]

    max_articles = source.get(
        "max_articles",
        20
    )

    articles = []

    print(
        f"\nFetching {name}..."
    )

    try:

        response = requests.get(
            feed_url,
            timeout=15,
            verify=certifi.where(),
            headers=HEADERS
        )

        response.raise_for_status()

        feed = feedparser.parse(
            response.content
        )

        if feed.bozo:

            print(
                f"Feed warning: "
                f"{feed.bozo_exception}"
            )

        entries = (
            feed.entries[:max_articles]
        )

        for entry in entries:

            title = clean_html_text(
                entry.get(
                    "title",
                    "No title"
                )
            )

            article_url = entry.get(
                "link",
                ""
            ).strip()

            published = entry.get(
                "published",
                entry.get(
                    "updated",
                    "Unknown"
                )
            )

            # ----------------------------------------
            # RSS DESCRIPTION / SUMMARY
            # ----------------------------------------

            description = clean_html_text(
                entry.get(
                    "summary",
                    entry.get(
                        "description",
                        ""
                    )
                )
            )

            # Some RSS feeds expose richer content
            # under the content field.
            provided_text = ""

            content = entry.get(
                "content",
                []
            )

            if (
                isinstance(content, list)
                and len(content) > 0
            ):

                first_content = content[0]

                if isinstance(
                    first_content,
                    dict
                ):

                    provided_text = (
                        clean_html_text(
                            first_content.get(
                                "value",
                                ""
                            )
                        )
                    )

            # If full RSS content isn't available,
            # use the description.
            if not provided_text:

                provided_text = (
                    description
                )

            if not article_url:
                continue

            articles.append({

                "source":
                    name,

                "title":
                    title,

                "url":
                    article_url,

                "published":
                    published,

                "description":
                    description,

                "provided_text":
                    provided_text
            })

        print(
            f"Found {len(feed.entries)} "
            f"items in feed."
        )

        print(
            f"Processing "
            f"{len(articles)} "
            f"most recent items."
        )

    except requests.RequestException as error:

        print(
            f"FAILED to fetch {name}"
        )

        print(
            f"Reason: {error}"
        )

    return articles