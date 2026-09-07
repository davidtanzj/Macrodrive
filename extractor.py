import requests
import certifi
import trafilatura


def extract_article_text(url):

    try:

        response = requests.get(
            url,
            timeout=15,
            verify=certifi.where(),
            headers={
                "User-Agent": "Macrodrive/1.0"
            }
        )

        response.raise_for_status()

        # Let Requests determine the most likely encoding
        response.encoding = response.apparent_encoding

        text = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False
        )

        if text is None:
            return ""

        return text.strip()

    except requests.RequestException as error:

        print(f"Failed to download article: {error}")

        return ""