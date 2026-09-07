import re


# ============================================================
# Macrodrive TOPIC CLASSIFIER V2.1
# ============================================================

CATEGORY_RULES = {

    "Central Banking & Rates": {

        "threshold": 8,

        "strong": [
            "fed",
            "raise rates",
            "raising rates",
            "rate hike",
            "rate hikes",
            "rate cut",
            "rate cuts",
            "cut rates",
            "lower rates",
            "monetary policy",
            "interest rate",
            "interest rates",
            "policy rate",
            "policy rates",
            "federal funds rate",
            "discount rate",
            "deposit rate",
            "quantitative easing",
            "quantitative tightening",
            "balance sheet reduction",
            "restrictive monetary policy",
            "accommodative monetary policy"
        ],

        "medium": [
            "fomc",
            "federal open market committee",
            "hawkish",
            "dovish",
            "policy easing",
            "policy tightening",
            "interest-rate policy"
        ],

        "weak": []
    },


    "Government Debt & Tax": {

        "threshold": 7,

        "strong": [
            "government debt",
            "public debt",
            "national debt",
            "sovereign debt",
            "budget deficit",
            "budget surplus",
            "fiscal deficit",
            "fiscal policy",
            "budget", "budget deficit", "fiscal deficit", "government spending", "public spending", "tax cuts", "tax rises", "public debt",
            "debt ceiling",
            "government borrowing"
        ],

        "medium": [
            "government spending",
            "tax increase",
            "tax increases",
            "tax cut",
            "tax cuts",
            "fiscal stimulus",
            "fiscal consolidation",
            "government budget"
        ],

        "weak": [
            "stimulus",
            "deficit",
            "taxation"
        ]
    },


    "Inflation & Prices": {

        "threshold": 7,

        "strong": [
            "consumer price index",
            "producer price index",
            "inflation rate",
            "core inflation",
            "headline inflation",
            "price stability",
            "price pressures",
            "inflation expectations"
        ],

        "medium": [
            "inflation",
            "cpi", "consumer prices", "producer prices", "pce inflation", "core inflation", "headline inflation", "price pressures", "disinflation", "deflation",
            "consumer prices",
            "producer prices",
            "deflation",
            "disinflation",
            "price growth"
        ],

        "weak": [
            "cpi",
            "ppi",
            "pce"
        ]
    },


    "Growth & GDP": {

        "threshold": 7,

        "strong": [
            "gross domestic product",
            "gdp growth",
            "economic growth",
            "gdp", "growth", "recession", "slowdown", "contraction", "expansion", "pmi", "industrial production", "retail sales", "business activity",
            "economic contraction",
            "economic expansion",
            "economic slowdown",
            "economic recovery",
            "industrial production"
        ],

        "medium": [
            "gdp",
            "recession",
            "economic activity",
            "manufacturing activity",
            "services activity",
            "purchasing managers index"
        ],

        "weak": [
            "pmi"
        ]
    },


    "Jobs & Wages": {

        "threshold": 7,

        "strong": [
            "nonfarm payrolls",
            "unemployment rate",
            "labor market",
            "labour market",
            "wage growth",
            "jobless claims",
            "employment growth"
        ],

        "medium": [
            "unemployment",
            "employment",
            "jobs", "job market", "labour market", "labor market", "payrolls", "nonfarm payrolls", "unemployment", "wages", "wage growth", "jobless claims",
            "payrolls",
            "wages",
            "job growth"
        ],

        "weak": [
            "hiring",
            "layoffs"
        ]
    },


    "Global Trade & Geopolitics": {

        "threshold": 8,

        "strong": [
            "trade war",
            "trade deficit",
            "trade surplus",
            "trade agreement",
            "trade tensions",
            "economic sanctions",
            "export controls",
            "trade restrictions",
            "geopolitical tensions"
        ],

        "medium": [
            "tariffs",
            "tariff",
            "sanctions",
            "exports",
            "imports",
            "geopolitical risk"
        ],

        "weak": [
            "trade",
            "tariff", "tariffs", "trade war", "trade deal", "export controls", "exports", "imports", "trade deficit", "trade surplus", "supply chains",
            "geopolitical"
        ]
    },


    "Currencies & FX": {

        "threshold": 7,

        "strong": [
            "foreign exchange",
            "fx", "currency", "currencies", "exchange rate", "exchange rates", "currency intervention", "devaluation", "appreciation", "depreciation",
            "sterling", "pound", "yen", "yuan", "renminbi", "dollar", "euro", "baht",
            "exchange rate",
            "exchange rates",
            "currency market",
            "currency markets",
            "foreign-exchange market"
        ],

        "medium": [
            "dollar index",
            "currency depreciation",
            "currency appreciation",
            "yen depreciation",
            "yuan depreciation",
            "euro depreciation",
            "currency intervention"
        ],

        "weak": [
            "forex"
        ]
    },


    "Commodities & Energy": {

        "threshold": 7,

        "strong": [
            "crude oil",
            "oil", "energy prices", "petroleum", "natural gas", "lng", "copper", "gold", "iron ore", "coal", "metals", "commodity prices",
            "brent", "wti", "opec", "opec+",
            "oil prices",
            "natural gas",
            "iron ore",
            "commodity prices",
            "energy prices",
            "oil production",
            "gas production"
        ],

        "medium": [
            "brent",
            "wti",
            "opec",
            "copper",
            "gold",
            "silver",
            "coal",
            "lng",
            "uranium"
        ],

        "weak": [
            "oil",
            "commodities"
        ]
    },


    "Fixed Income & Credit": {

        "threshold": 8,

        "strong": [
            "bond",
            "bonds",
            "yield",
            "yields",
            "bond market",
            "bond markets",
            "treasury yields",
            "treasury yield",
            "treasuries", "treasury yields", "bond sell-off", "bond selloff",
            "gilts", "bunds",
            "yield curve",
            "government bonds",
            "corporate bonds",
            "financial markets",
            "bond yields"
        ],

        "medium": [
            "equity markets",
            "stock market",
            "market volatility",
            "sovereign bonds"
        ],

        "weak": [
            "equities"
        ]
    },


    "Macro & Markets": {

        "threshold": 6,

        "strong": [
            "economic outlook",
            "macroeconomic",
            "global economy",
            "economic policy",
            "financial conditions",
            "market outlook"
        ],

        "medium": [
            "economy",
            "economic",
            "markets",
            "market",
            "growth outlook",
            "business cycle"
        ],

        "weak": []
    },


    "Economic Theory": {

        "threshold": 12,

        "strong": [
            "economic theory",
            "economic model",
            "economic models",
            "macroeconomic model",
            "macroeconomic models",
            "economic research",
            "research paper",
            "working paper"
        ],

        "medium": [
            "keynesian",
            "monetarism",
            "economic methodology"
        ],

        "weak": []
    }
}


# ============================================================
# SCORING WEIGHTS
# ============================================================

# Importance of the keyword itself
TERM_WEIGHTS = {
    "strong": 4,
    "medium": 2,
    "weak": 1
}


# Importance based on where the keyword appears
SECTION_WEIGHTS = {
    "title": 4,
    "opening": 2,
    "body": 1
}


# If a category appears ONLY in the deep article body,
# it must meet a higher threshold.
BODY_ONLY_THRESHOLD_MULTIPLIER = 2


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def phrase_in_text(phrase, text):

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


def split_article(body_text):

    if not body_text:
        return "", ""

    # The first 700 characters are treated as
    # the important opening section.
    opening = body_text[:700]

    # Everything afterwards is the deeper body.
    body = body_text[700:]

    return opening, body


def score_section(
    text,
    rules,
    section_name
):

    score = 0
    matches = []

    section_multiplier = (
        SECTION_WEIGHTS[section_name]
    )

    for strength in [
        "strong",
        "medium",
        "weak"
    ]:

        keywords = rules.get(
            strength,
            []
        )

        base_weight = (
            TERM_WEIGHTS[strength]
        )

        for keyword in keywords:

            if phrase_in_text(
                keyword,
                text
            ):

                points = (
                    base_weight
                    * section_multiplier
                )

                score += points

                matches.append({
                    "keyword": keyword,
                    "strength": strength,
                    "section": section_name,
                    "points": points
                })

    return score, matches


# ============================================================
# CONCEPT COMBINATION BONUSES
# ============================================================

def central_bank_bonus(
    title,
    opening,
    body
):

    full_text = (
        title
        + " "
        + opening
        + " "
        + body
    )

    institution_terms = [
        "federal reserve",
        "fed",
        "ecb",
        "european central bank",
        "bank of england",
        "bank of japan",
        "pboc",
        "people's bank of china",
        "central bank",
            "central bankers", "monetary policy", "interest rates", "policy rates", "benchmark rate", "basis points", "hawkish", "dovish", "tightening cycle", "easing cycle",
            "fed", "rate hike", "rate hikes", "raise rates", "raising rates",
            "higher rates", "rate cut", "rate cuts", "cut rates", "lower rates",
            "policy tightening", "policy easing",
        "central banks"
    ]

    policy_terms = [
        "monetary policy",
        "interest rate",
        "interest rates",
        "policy rate",
        "rate cut",
        "rate hike",
        "federal funds rate",
        "discount rate",
        "quantitative easing",
        "quantitative tightening",
        "fomc"
    ]

    institution_found = any(
        phrase_in_text(
            term,
            full_text
        )
        for term in institution_terms
    )

    policy_found = any(
        phrase_in_text(
            term,
            full_text
        )
        for term in policy_terms
    )

    if (
        institution_found
        and policy_found
    ):
        return 6

    return 0


def trade_bonus(
    title,
    opening,
    body
):

    important_text = (
        title
        + " "
        + opening
    )

    trade_terms = [
        "exports",
        "imports",
        "tariff",
        "tariffs",
        "trade",
        "sanctions"
    ]

    matches = sum(
        phrase_in_text(
            term,
            important_text
        )
        for term in trade_terms
    )

    if matches >= 2:
        return 4

    return 0


def category_bonus(
    category,
    title,
    opening,
    body
):

    if category == "Central Banking & Rates":

        return central_bank_bonus(
            title,
            opening,
            body
        )

    if category == (
        "Global Trade & Geopolitics"
    ):

        return trade_bonus(
            title,
            opening,
            body
        )

    return 0


# ============================================================
# MAIN CLASSIFIER
# ============================================================

def classify_article(
    title,
    body_text=""
):

    opening, body = split_article(
        body_text
    )

    results = []

    for category, rules in (
        CATEGORY_RULES.items()
    ):

        # ------------------------------------
        # Score headline
        # ------------------------------------

        title_score, title_matches = (
            score_section(
                title,
                rules,
                "title"
            )
        )

        # ------------------------------------
        # Score opening
        # ------------------------------------

        opening_score, opening_matches = (
            score_section(
                opening,
                rules,
                "opening"
            )
        )

        # ------------------------------------
        # Score deep article body
        # ------------------------------------

        body_score, body_matches = (
            score_section(
                body,
                rules,
                "body"
            )
        )

        # ------------------------------------
        # Concept bonus
        # ------------------------------------

        bonus = category_bonus(
            category,
            title,
            opening,
            body
        )

        # ------------------------------------
        # Calculate total score
        # ------------------------------------

        final_score = (
            title_score
            + opening_score
            + body_score
            + bonus
        )

        normal_threshold = (
            rules["threshold"]
        )

        # ------------------------------------
        # Determine importance of evidence
        # ------------------------------------

        important_evidence = (
            len(title_matches)
            + len(opening_matches)
        )

        # If this topic appears only deep in the
        # article body, require much more evidence.
        if important_evidence == 0:

            effective_threshold = (
                normal_threshold
                * BODY_ONLY_THRESHOLD_MULTIPLIER
            )

        else:

            effective_threshold = (
                normal_threshold
            )

        # ------------------------------------
        # Save valid classification
        # ------------------------------------

        if (
            final_score
            >= effective_threshold
        ):

            results.append({

                "category":
                    category,

                "score":
                    final_score,

                "threshold":
                    effective_threshold,

                "normal_threshold":
                    normal_threshold,

                "body_only":
                    important_evidence == 0,

                "bonus":
                    bonus,

                "title_matches":
                    title_matches,

                "opening_matches":
                    opening_matches,

                "body_matches":
                    body_matches
            })

    # Highest confidence topics first
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results