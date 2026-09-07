import requests
import certifi


HEADERS = {
    "User-Agent": "Macrodrive/1.0"
}


def extract_cdata(value):

    if isinstance(value, str):

        return value.strip()

    if isinstance(value, dict):

        text = value.get(
            "cdata!",
            ""
        )

        if isinstance(text, str):

            return text.strip()

    return ""


def collect(source):

    name = source["name"]
    api_url = source["url"]

    max_articles = source.get(
        "max_articles",
        20
    )

    articles = []

    print(
        f"\nFetching {name}..."
    )

    try:

        params = {

            "format":
                "json",

            "rows":
                max_articles,

            "fct": (
                "displayconttype_exact,"
                "topic_exact,"
                "lang_exact,"
                "count_exact,"
                "countcode_exact,"
                "admreg_exact"
            ),

            "src":
                "cq55",

            "apilang":
                "en",

            "lang_exact":
                "English",

            "os":
                0
        }

        response = requests.get(
            api_url,
            params=params,
            timeout=20,
            verify=certifi.where(),
            headers=HEADERS
        )

        response.raise_for_status()

        data = response.json()

        documents = data.get(
            "documents",
            {}
        )

        if isinstance(
            documents,
            dict
        ):

            document_list = list(
                documents.values()
            )

        elif isinstance(
            documents,
            list
        ):

            document_list = documents

        else:

            document_list = []

        print(
            f"World Bank returned "
            f"{len(document_list)} documents."
        )

        for document in document_list:

            if not isinstance(
                document,
                dict
            ):

                continue

            # --------------------------------
            # TITLE
            # --------------------------------

            title = extract_cdata(
                document.get(
                    "title",
                    ""
                )
            )

            # --------------------------------
            # URL
            # --------------------------------

            article_url = (
                document.get(
                    "url",
                    ""
                )
            )

            if not isinstance(
                article_url,
                str
            ):

                article_url = ""

            article_url = (
                article_url.strip()
            )

            if article_url.startswith(
                "http://www.worldbank.org"
            ):

                article_url = (
                    article_url.replace(
                        "http://",
                        "https://",
                        1
                    )
                )

            # --------------------------------
            # DATE
            # --------------------------------

            published = (
                document.get(
                    "lnchdt",
                    "Unknown"
                )
            )

            if not isinstance(
                published,
                str
            ):

                published = str(
                    published
                )

            # --------------------------------
            # DESCRIPTION
            # --------------------------------

            description = extract_cdata(
                document.get(
                    "descr",
                    ""
                )
            )

            # --------------------------------
            # PROVIDED TEXT
            # --------------------------------

            provided_text = (
                extract_cdata(
                    document.get(
                        "content",
                        ""
                    )
                )
            )

            content_1000 = (
                extract_cdata(
                    document.get(
                        "content_1000",
                        ""
                    )
                )
            )

            if (
                len(content_1000)
                > len(provided_text)
            ):

                provided_text = (
                    content_1000
                )

            if (
                description
                and description
                not in provided_text
            ):

                provided_text = (
                    description
                    + "\n\n"
                    + provided_text
                ).strip()

            # --------------------------------
            # VALIDATION
            # --------------------------------

            if not title:
                continue

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

            if (
                len(articles)
                >= max_articles
            ):

                break

        print(
            f"Processing "
            f"{len(articles)} items."
        )

    except requests.RequestException as error:

        print(
            f"FAILED to fetch {name}"
        )

        print(
            f"Reason: {error}"
        )

    except ValueError as error:

        print(
            f"FAILED to parse "
            f"{name} JSON response"
        )

        print(
            f"Reason: {error}"
        )

    return articles