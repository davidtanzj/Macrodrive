import re


REGIONS = {

    "United States": [
        "united states",
        "u.s.",
        "u.s",
        "us economy",
        "american economy",
        "washington"
    ],

    "China": [
        "china",
        "chinese",
        "beijing",
        "pboc",
        "renminbi",
        "yuan"
    ],

    "Eurozone": [
        "eurozone",
        "euro area",
        "european central bank",
        "ecb"
    ],

    "United Kingdom": [
        "united kingdom",
        "u.k.",
        "uk economy",
        "britain",
        "british",
        "bank of england"
    ],

    "Japan": [
        "japan",
        "japanese",
        "bank of japan",
        "boj"
    ],

    "India": [
        "india",
        "indian",
        "reserve bank of india",
        "rbi"
    ],

    "Southeast Asia": [
        "southeast asia",
        "asean"
    ],

    "Middle East": [
        "middle east",
        "gulf states",
        "gulf countries"
    ],

    "Latin America": [
        "latin america",
        "latin american"
    ],

    "Africa": [
        "africa",
        "african"
    ]
}


def phrase_in_text(phrase, text):

    pattern = r"\b" + re.escape(phrase) + r"\b"

    return re.search(
        pattern,
        text,
        re.IGNORECASE
    ) is not None


def detect_regions(title, body_text=""):

    results = []

    for region, keywords in REGIONS.items():

        title_matches = []
        body_matches = []

        for keyword in keywords:

            if phrase_in_text(keyword, title):
                title_matches.append(keyword)

            if phrase_in_text(keyword, body_text):
                body_matches.append(keyword)

        # Title evidence gets priority
        score = (
            len(title_matches) * 3
            + len(body_matches)
        )

        if score > 0:

            results.append({
                "region": region,
                "score": score,
                "title_matches": title_matches,
                "body_matches": body_matches
            })

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    return results