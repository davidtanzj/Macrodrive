from regiondetector import detect_regions


test_articles = [

    "China GDP growth slows amid weak exports",

    "Federal Reserve cuts interest rates",

    "ECB keeps interest rates unchanged in euro area",

    "Bank of Japan raises policy rate",

    "India inflation falls unexpectedly",

    "US and China announce new trade agreement"
]


for title in test_articles:

    print("\n========================================")
    print(title)

    regions = detect_regions(title)

    if not regions:

        print("Region: None")
        continue

    for result in regions:

        print(
            f"{result['region']} "
            f"(score: {result['score']})"
        )