import re


# ============================================================
# Macrodrive MACRO RELEVANCE FILTER
# ============================================================


HIGH_RELEVANCE_TERMS = [

    "monetary policy",
    "interest rate",
    "interest rates",
    "inflation",
    "consumer price index",
    "producer price index",
    "gdp",
    "gross domestic product",
    "economic growth",
    "recession",
    "unemployment",
    "employment",
    "labor market",
    "labour market",
    "wage growth",
    "fiscal policy",
    "government debt",
    "budget deficit",
    "trade war",
    "tariffs",
    "foreign exchange",
    "exchange rate",
    "crude oil",
    "natural gas",
    "bond market",
    "treasury yields",
    "economic outlook"
]


MEDIUM_RELEVANCE_TERMS = [

    "fomc",
    "central bank",
    "federal reserve",
    "ecb",
    "economic activity",
    "exports",
    "imports",
    "trade",
    "currency",
    "oil",
    "energy",
    "commodities",
    "bonds",
    "financial markets",
    "economic research"
]


# These phrases strongly suggest that a story is operational,
# regulatory or administrative rather than macroeconomic.

IRRELEVANT_TITLE_TERMS = [

    "enforcement action",
    "enforcement actions",

    "approval of application",
    "approval of the application",

    "former employee",

    "bank examination",

    "operating normally",

    "is closed",

    "during weekend",

    "holiday",

    "list of eligible marketable assets",

    "list of monetary financial institutions"
]


def phrase_in_text(
    phrase,
    text
):

    if not text:
        return False

    pattern = (
        r"\b"
        + re.escape(phrase)
        + r"\b"
    )

    return (
        re.search(
            pattern,
            text,
            re.IGNORECASE
        )
        is not None
    )


def calculate_relevance(
    title,
    body_text=""
):

    title_lower = title.lower()

    # ----------------------------------------
    # Strong exclusion rules
    # ----------------------------------------

    for term in IRRELEVANT_TITLE_TERMS:

        if phrase_in_text(
            term,
            title_lower
        ):

            return {
                "relevant": False,
                "score": 0,
                "reason":
                    f"Excluded by title rule: {term}"
            }

    # ----------------------------------------
    # Split body
    # ----------------------------------------

    opening = body_text[:700]

    body = body_text[700:]

    score = 0

    matches = []

    # ----------------------------------------
    # High relevance concepts
    # ----------------------------------------

    for term in HIGH_RELEVANCE_TERMS:

        if phrase_in_text(
            term,
            title
        ):

            score += 8

            matches.append(
                f"title: {term}"
            )

        elif phrase_in_text(
            term,
            opening
        ):

            score += 4

            matches.append(
                f"opening: {term}"
            )

        elif phrase_in_text(
            term,
            body
        ):

            score += 1

            matches.append(
                f"body: {term}"
            )

    # ----------------------------------------
    # Medium relevance concepts
    # ----------------------------------------

    for term in MEDIUM_RELEVANCE_TERMS:

        if phrase_in_text(
            term,
            title
        ):

            score += 4

            matches.append(
                f"title: {term}"
            )

        elif phrase_in_text(
            term,
            opening
        ):

            score += 2

            matches.append(
                f"opening: {term}"
            )

        elif phrase_in_text(
            term,
            body
        ):

            score += 1

            matches.append(
                f"body: {term}"
            )

    # Require meaningful evidence
    relevant = score >= 6

    return {
        "relevant": relevant,
        "score": score,
        "matches": matches
    }