import sys

import feedparser
import requests
import certifi


def test_feed(url):

    print()
    print("=" * 70)
    print("Macrodrive RSS TESTER")
    print("=" * 70)

    print(f"URL: {url}")

    try:

        response = requests.get(
            url,
            timeout=15,
            verify=certifi.where(),
            headers={
                "User-Agent": "Macrodrive/1.0"
            }
        )

        print(
            f"HTTP status: "
            f"{response.status_code}"
        )

        response.raise_for_status()

        feed = feedparser.parse(
            response.content
        )

        print(
            f"Feed title: "
            f"{feed.feed.get('title', 'Unknown')}"
        )

        print(
            f"Entries found: "
            f"{len(feed.entries)}"
        )

        if feed.bozo:

            print(
                f"Feed warning: "
                f"{feed.bozo_exception}"
            )

        print()
        print("FIRST 5 ENTRIES")
        print("-" * 70)

        for entry in feed.entries[:5]:

            print()

            print(
                f"Title: "
                f"{entry.get('title', 'No title')}"
            )

            print(
                f"URL: "
                f"{entry.get('link', '')}"
            )

            print(
                f"Published: "
                f"{entry.get('published', entry.get('updated', 'Unknown'))}"
            )

    except requests.RequestException as error:

        print()
        print(
            f"REQUEST FAILED: {error}"
        )


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "python testfeed.py <RSS URL>"
        )

    else:

        test_feed(
            sys.argv[1]
        )