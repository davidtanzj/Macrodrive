import re


# ============================================================
# ACCESS STATUS VALUES
# ============================================================

FREE = "free"
PAYWALLED = "paywalled"
UNKNOWN = "unknown"


# ============================================================
# KNOWN SOURCE DEFAULTS
# ============================================================

KNOWN_FREE_SOURCES = {
    "Federal Reserve",
    "EIA",
    "BIS Research",
    "BIS Central Bank Speeches",
    "BIS Press Releases",
    "World Bank",
    "IMF Blog"
}


KNOWN_PAYWALLED_SOURCES = {
    "Bloomberg"
}


# ============================================================
# PAYWALL SIGNALS
# ============================================================

GENERIC_PAYWALL_SIGNALS = [

    "subscribe to continue reading",

    "subscribe to read",

    "subscription required",

    "subscriber only",

    "subscribers only",

    "for subscribers",

    "subscriber exclusive",

    "premium content",

    "unlock this article"
]


BUSINESS_TIMES_PAYWALL_SIGNALS = [

    "subscriber",

    "subscriber-only",

    "subscriber only"
]


# ============================================================
# NORMALIZE
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# DETECT EXPLICIT PAYWALL
# ============================================================

def contains_paywall_signal(
    text,
    signals
):

    normalized = normalize_text(
        text
    )

    for signal in signals:

        if signal in normalized:

            return True

    return False


# ============================================================
# SOURCE DEFAULT
# ============================================================

def get_source_default(
    source
):

    if source in KNOWN_FREE_SOURCES:

        return FREE

    if source in KNOWN_PAYWALLED_SOURCES:

        return PAYWALLED

    return UNKNOWN


# ============================================================
# ARTICLE-LEVEL DETECTION
# ============================================================

def detect_access(
    source,
    page_text="",
    extracted_text=""
):

    # --------------------------------------------------------
    # SOURCES KNOWN TO BE FREE
    # --------------------------------------------------------

    if source in KNOWN_FREE_SOURCES:

        return FREE


    # --------------------------------------------------------
    # BLOOMBERG
    #
    # Macrodrive intentionally uses metadata-only access.
    # --------------------------------------------------------

    if source in KNOWN_PAYWALLED_SOURCES:

        return PAYWALLED


    # --------------------------------------------------------
    # BUSINESS TIMES
    # --------------------------------------------------------

    if source == "Business Times":

        if contains_paywall_signal(
            page_text,
            BUSINESS_TIMES_PAYWALL_SIGNALS
        ):

            return PAYWALLED

        # If we successfully extracted substantial article
        # text and did not detect the subscriber marker,
        # treat the article as accessible.

        if (
            extracted_text
            and len(
                extracted_text.strip()
            ) >= 500
        ):

            return FREE

        return UNKNOWN


    # --------------------------------------------------------
    # OTHER MIXED / UNKNOWN SOURCES
    # --------------------------------------------------------

    if contains_paywall_signal(
        page_text,
        GENERIC_PAYWALL_SIGNALS
    ):

        return PAYWALLED


    # Successful substantial extraction is evidence that
    # the content was publicly accessible to our normal
    # request at processing time.

    if (
        extracted_text
        and len(
            extracted_text.strip()
        ) >= 500
    ):

        return FREE


    return UNKNOWN