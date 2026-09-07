from classifier import classify_article
from relevance import calculate_relevance


TEST_ARTICLES = [

    {
        "title":
            "Federal Reserve cuts interest rates "
            "as inflation falls",

        "body":
            "The Federal Open Market Committee "
            "reduced the federal funds rate as "
            "inflation pressures continued to ease."
    },

    {
        "title":
            "Federal Reserve Board issues "
            "enforcement action with former employee",

        "body":
            "The Federal Reserve announced an "
            "enforcement action involving a former "
            "employee of a commercial bank."
    },

    {
        "title":
            "Oil prices rise as geopolitical "
            "tensions threaten supply",

        "body":
            "Crude oil markets rose amid concerns "
            "about energy supplies and geopolitical "
            "tensions."
    },

    {
        "title":
            "China GDP growth slows amid weak exports",

        "body":
            "Economic growth slowed as exports "
            "weakened and manufacturing activity "
            "lost momentum."
    },

    {
        "title":
            "Apple announces new iPhone",

        "body":
            "Apple introduced its latest smartphone "
            "at an event in California."
    }
]


for article in TEST_ARTICLES:

    title = article["title"]
    body = article["body"]

    print()
    print("=" * 70)

    print(title)

    relevance = calculate_relevance(
        title,
        body
    )

    print(
        f"Relevant: "
        f"{relevance['relevant']}"
    )

    print(
        f"Relevance score: "
        f"{relevance['score']}"
    )

    if not relevance["relevant"]:

        continue

    results = classify_article(
        title,
        body
    )

    if not results:

        print(
            "No topic detected."
        )

        continue

    print("Topics:")

    for result in results:

        print(
            f"  {result['category']} "
            f"(score: {result['score']})"
        )