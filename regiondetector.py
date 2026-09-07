import re


REGIONS = {

    "United States": [
        "united states", "u.s.", "u.s", "us economy",
        "american economy", "federal reserve", "fomc", "fed",
        "treasury", "treasuries", "white house", "wall street",
    ],

    "China": [
        "china", "chinese", "beijing", "pboc",
        "people's bank of china", "renminbi", "yuan",
    ],

    "Eurozone": [
        "eurozone", "euro area", "european central bank", "ecb",
        "euro", "bund", "bunds", "brussels",
        "germany", "german", "france", "french", "italy", "italian",
        "spain", "spanish", "netherlands", "dutch",
    ],

    "United Kingdom": [
        "united kingdom", "u.k.", "uk economy", "britain",
        "british", "bank of england", "boe", "sterling", "gilts",
    ],

    "Japan": [
        "japan", "japanese", "bank of japan", "boj", "yen", "tokyo",
    ],

    "India": [
        "india", "indian", "reserve bank of india", "rbi",
    ],

    "Southeast Asia": [
        "southeast asia", "asean",
        "singapore", "singaporean", "singapore dollar", "mas",
        "thailand", "thai", "baht", "bank of thailand",
        "indonesia", "indonesian", "rupiah", "bank indonesia",
        "malaysia", "malaysian", "ringgit", "bank negara",
        "vietnam", "vietnamese", "dong",
        "philippines", "philippine", "peso", "bangko sentral",
        "myanmar", "burma", "cambodia", "cambodian",
        "laos", "brunei",
    ],

    "South Korea": [
        "south korea", "korean economy", "bank of korea",
        "seoul", "won",
    ],

    "Australia & New Zealand": [
        "australia", "australian", "reserve bank of australia", "rba",
        "new zealand", "reserve bank of new zealand", "rbnz",
    ],

    "Middle East": [
        "middle east", "gulf states", "gulf countries",
        "saudi arabia", "saudi", "uae", "united arab emirates",
        "dubai", "abu dhabi", "riyadh", "israeli", "iranian",
        "qatar", "israel", "iran", "iraq", "kuwait", "oman", "bahrain",
    ],

    "Canada": [
        "canada", "canadian", "bank of canada",
    ],

    "Latin America": [
        "latin america", "latin american",
        "brazil", "brazilian", "mexico", "mexican",
        "venezuela", "venezuelan", "bolivia", "bolivian", "ecuador", "ecuadorian",
        "uruguay", "uruguayan", "paraguay", "paraguayan",
        "argentina", "argentine", "chile", "chilean",
        "colombia", "colombian", "peru", "peruvian",
    ],

    "Africa": [
        "africa", "african", "south africa", "nigeria", "nigerian",
        "egypt", "egyptian", "kenya", "kenyan",
    ],
}


def phrase_in_text(phrase, text):

    if not text:
        return False

    pattern = r"\b" + re.escape(phrase) + r"\b"

    return re.search(
        pattern,
        text,
        re.IGNORECASE
    ) is not None


def detect_regions(title, body_text=""):

    # Bare uppercase "US" is a common financial-news abbreviation.
    # Only expand uppercase US so the English pronoun "us" is not misread.
    if re.search(r"\bUS\b", title or ""):
        title = (title or "") + " united states"

    # Geography in the headline/opening is much more likely to describe
    # the subject of the article than an incidental country mention later.
    opening = body_text[:900]
    deep_body = body_text[900:]

    results = []

    for region, keywords in REGIONS.items():

        title_matches = []
        opening_matches = []
        body_matches = []

        for keyword in keywords:

            if phrase_in_text(keyword, title):
                title_matches.append(keyword)

            if phrase_in_text(keyword, opening):
                opening_matches.append(keyword)

            if phrase_in_text(keyword, deep_body):
                body_matches.append(keyword)

        score = (
            len(title_matches) * 6
            + len(opening_matches) * 3
            + len(body_matches)
        )

        # Require important evidence. A lone incidental deep-body mention
        # is not enough to attach a geographical filter.
        important_matches = (
            len(title_matches)
            + len(opening_matches)
        )

        if important_matches > 0 or score >= 3:

            results.append({
                "region": region,
                "score": score,
                "title_matches": title_matches,
                "opening_matches": opening_matches,
                "body_matches": body_matches,
            })

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    if not results:
        return []

    # Keep the primary geography and other regions only when evidence is
    # reasonably close. This prevents a passing reference from becoming
    # an unrelated filter.
    best_score = results[0]["score"]

    return [
        result
        for result in results
        if result["score"] >= max(3, best_score * 0.5)
    ]
