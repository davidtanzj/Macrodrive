import hashlib
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import certifi
import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

BLS_BASE_URL = "https://www.bls.gov"

BEA_SCHEDULE_URL = (
    "https://www.bea.gov/news/schedule"
)

CENSUS_CALENDAR_URL = (
    "https://www.census.gov/"
    "economic-indicators/"
    "calendar-listview.html"
)

FED_FOMC_URL = (
    "https://www.federalreserve.gov/"
    "monetarypolicy/fomccalendars.htm"
)

FED_MONTHLY_BASE_URL = (
    "https://www.federalreserve.gov/"
    "newsevents/"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}


EASTERN = ZoneInfo(
    "America/New_York"
)


MONTHS_AHEAD = 6


# ============================================================
# RELEASE RULES
# ============================================================

BLS_RELEASE_RULES = [

    {
        "terms": ["employment situation"],
        "name": "Employment Situation",
        "type": "Jobs & Wages",
        "importance": 3
    },

    {
        "terms": ["consumer price index"],
        "name": "Consumer Price Index (CPI)",
        "type": "Inflation & Prices",
        "importance": 3
    },

    {
        "terms": ["producer price index"],
        "name": "Producer Price Index (PPI)",
        "type": "Inflation & Prices",
        "importance": 2
    },

    {
        "terms": [
            "job openings and labor turnover",
            "jolts"
        ],
        "name": "JOLTS",
        "type": "Jobs & Wages",
        "importance": 2
    },

    {
        "terms": ["employment cost index"],
        "name": "Employment Cost Index",
        "type": "Jobs & Wages",
        "importance": 2
    },

    {
        "terms": [
            "productivity and costs",
            "productivity"
        ],
        "name": "Productivity and Costs",
        "type": "Jobs & Wages",
        "importance": 2
    },

    {
        "terms": [
            "import and export price",
            "import/export price"
        ],
        "name": "Import and Export Prices",
        "type": "Inflation & Prices",
        "importance": 1
    }

]


BEA_RELEASE_RULES = [

    {
        "terms": [
            "gross domestic product",
            "gdp"
        ],
        "name": "Gross Domestic Product (GDP)",
        "type": "Growth & GDP",
        "importance": 3
    },

    {
        "terms": [
            "personal income and outlays"
        ],
        "name": "Personal Income & Outlays / PCE",
        "type": "Inflation & Consumer Spending",
        "importance": 3
    },

    {
        "terms": [
            "international trade in goods and services"
        ],
        "name": "U.S. International Trade",
        "type": "Global Trade",
        "importance": 2
    }

]


CENSUS_RELEASE_RULES = [

    {
        "terms": [
            "advance monthly sales for retail and food services",
            "advance retail sales",
            "retail sales"
        ],
        "name": "Retail Sales",
        "type": "Consumer & Spending",
        "importance": 3
    },

    {
        "terms": [
            "new residential construction",
            "housing starts",
            "building permits"
        ],
        "name": "Housing Starts & Building Permits",
        "type": "Growth & Housing",
        "importance": 2
    },

    {
        "terms": [
            "new residential sales",
            "new home sales"
        ],
        "name": "New Home Sales",
        "type": "Consumer & Housing",
        "importance": 2
    },

    {
        "terms": [
            "manufacturers' shipments, inventories, and orders",
            "durable goods"
        ],
        "name": "Durable Goods Orders",
        "type": "Growth & Investment",
        "importance": 2
    }

]


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_spaces(text):

    if not text:
        return ""

    text = (
        text
        .replace("\xa0", " ")
        .replace("\u202f", " ")
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def add_months(
    year,
    month,
    amount
):

    month_index = (
        year * 12
        + month
        - 1
        + amount
    )

    return (
        month_index // 12,
        month_index % 12 + 1
    )


def match_rule(
    text,
    rules
):

    normalized = (
        normalize_spaces(
            text
        ).lower()
    )

    for rule in rules:

        for term in rule["terms"]:

            if (
                term.lower()
                in normalized
            ):

                return rule

    return None


# ============================================================
# DATE PARSING
# ============================================================

def parse_date(
    text,
    default_year=None
):

    text = normalize_spaces(
        text
    )


    patterns = [

        "%A, %B %d, %Y",
        "%A, %b %d, %Y",

        "%B %d, %Y",
        "%b %d, %Y",

        "%B %d",
        "%b %d"

    ]


    for pattern in patterns:

        try:

            parsed = datetime.strptime(
                text,
                pattern
            )

            if (
                "%Y" not in pattern
                and default_year is not None
            ):

                parsed = parsed.replace(
                    year=default_year
                )

            return parsed.date()

        except ValueError:

            continue


    month_names = (
        "January|February|March|April|"
        "May|June|July|August|September|"
        "October|November|December|"
        "Jan|Feb|Mar|Apr|Jun|Jul|Aug|"
        "Sep|Sept|Oct|Nov|Dec"
    )


    match = re.search(
        rf"({month_names})\s+"
        rf"(\d{{1,2}})"
        rf"(?:,\s*(\d{{4}}))?",
        text,
        re.IGNORECASE
    )


    if not match:

        return None


    month_text = (
        match.group(1)
    )

    day = int(
        match.group(2)
    )

    year = (
        int(match.group(3))
        if match.group(3)
        else default_year
    )


    if year is None:

        return None


    if (
        month_text.lower()
        == "sept"
    ):

        month_text = "Sep"


    parsed_month = None


    for fmt in (
        "%B",
        "%b"
    ):

        try:

            parsed_month = (
                datetime.strptime(
                    month_text,
                    fmt
                ).month
            )

            break

        except ValueError:

            continue


    if parsed_month is None:

        return None


    try:

        return datetime(
            year,
            parsed_month,
            day
        ).date()

    except ValueError:

        return None


# ============================================================
# TIME PARSING
# ============================================================

def parse_time(text):

    text = (
        normalize_spaces(
            text
        )
        .upper()
        .replace("A.M.", "AM")
        .replace("P.M.", "PM")
    )


    match = re.search(
        r"(\d{1,2})"
        r"(?::(\d{2}))?"
        r"\s*(AM|PM)",
        text
    )


    if not match:

        return None


    hour = int(
        match.group(1)
    )

    minute = int(
        match.group(2) or 0
    )

    meridiem = (
        match.group(3)
    )


    if (
        meridiem == "PM"
        and hour != 12
    ):

        hour += 12


    if (
        meridiem == "AM"
        and hour == 12
    ):

        hour = 0


    return (
        hour,
        minute
    )


# ============================================================
# UTC CONVERSION
# ============================================================

def build_utc_datetime(
    release_date,
    release_time
):

    hour, minute = (
        release_time
    )


    eastern_datetime = datetime(

        release_date.year,
        release_date.month,
        release_date.day,

        hour,
        minute,

        tzinfo=EASTERN
    )


    return (
        eastern_datetime
        .astimezone(
            timezone.utc
        )
        .isoformat()
    )


# ============================================================
# EVENT HELPERS
# ============================================================

def build_event_key(
    source,
    event_name,
    scheduled_at
):

    raw = (
        source
        + "|"
        + event_name
        + "|"
        + scheduled_at
    )


    digest = hashlib.sha256(
        raw.encode(
            "utf-8"
        )
    ).hexdigest()[:20]


    return (
        source.lower()
        .replace(" ", "-")
        +
        "-"
        +
        digest
    )


def build_event(
    source_key,
    source_name,
    source_url,
    event_name,
    event_type,
    scheduled_at,
    importance
):

    return {

        "event_key":
            build_event_key(
                source_key,
                event_name,
                scheduled_at
            ),

        "country":
            "United States",

        "region":
            "North America",

        "event_name":
            event_name,

        "event_type":
            event_type,

        "scheduled_at":
            scheduled_at,

        "importance":
            importance,

        "previous":
            None,

        "consensus":
            None,

        "actual":
            None,

        "unit":
            "",

        "source":
            source_name,

        "source_url":
            source_url,

        "status":
            "scheduled"
    }


def deduplicate_events(events):

    unique = {}


    for event in events:

        unique[
            event["event_key"]
        ] = event


    return list(
        unique.values()
    )


# ============================================================
# BLS
# ============================================================

def build_bls_month_url(
    year,
    month
):

    return (
        f"{BLS_BASE_URL}"
        f"/schedule/{year}/"
        f"{month:02d}_sched_list.htm"
    )


def fetch_bls_month(
    year,
    month
):

    url = build_bls_month_url(
        year,
        month
    )


    print(
        f"Fetching BLS schedule "
        f"{year}-{month:02d}..."
    )


    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
            verify=certifi.where()
        )


        if response.status_code == 403:

            print(
                "BLS blocked this runner (HTTP 403). "
                "Keeping existing BLS calendar events."
            )

            return None

        if (
            response.status_code
            == 404
        ):

            print(
                "Schedule not published yet."
            )

            return []


        response.raise_for_status()


    except requests.RequestException as error:

        print(
            f"FAILED: {error}"
        )

        return []


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    events = []


    for row in soup.find_all(
        "tr"
    ):

        cells = row.find_all(
            [
                "td",
                "th"
            ]
        )


        if not cells:

            continue


        cell_texts = [

            normalize_spaces(
                cell.get_text(
                    " ",
                    strip=True
                )
            )

            for cell in cells
        ]


        row_text = (
            " | ".join(
                cell_texts
            )
        )


        rule = match_rule(
            row_text,
            BLS_RELEASE_RULES
        )


        if rule is None:

            continue


        release_date = None


        for cell_text in cell_texts:

            release_date = parse_date(
                cell_text,
                default_year=year
            )

            if release_date:

                break


        if release_date is None:

            continue


        release_time = None


        for cell_text in cell_texts:

            release_time = parse_time(
                cell_text
            )

            if release_time:

                break


        if release_time is None:

            continue


        scheduled_at = (
            build_utc_datetime(
                release_date,
                release_time
            )
        )


        events.append(

            build_event(

                source_key="BLS",

                source_name=(
                    "U.S. Bureau of "
                    "Labor Statistics"
                ),

                source_url=url,

                event_name=
                    rule["name"],

                event_type=
                    rule["type"],

                scheduled_at=
                    scheduled_at,

                importance=
                    rule["importance"]
            )
        )


    return events


def collect_bls():

    print()
    print("-" * 70)
    print("BLS")
    print("-" * 70)


    now = datetime.now(
        timezone.utc
    )


    events = []


    for offset in range(
        MONTHS_AHEAD
    ):

        year, month = add_months(
            now.year,
            now.month,
            offset
        )


        month_events = fetch_bls_month(
            year,
            month
        )

        if month_events is None:
            break

        events.extend(
            month_events
        )


    events = deduplicate_events(
        events
    )


    print(
        f"Found {len(events)} "
        f"relevant BLS events."
    )


    return events


# ============================================================
# FEDERAL RESERVE — FOMC
# ============================================================

def collect_fomc():

    print()
    print("-" * 70)
    print("FEDERAL RESERVE / FOMC")
    print("-" * 70)

    print(
        "Fetching Federal Reserve "
        "FOMC calendar..."
    )


    try:

        response = requests.get(
            FED_FOMC_URL,
            headers=HEADERS,
            timeout=20,
            verify=certifi.where()
        )

        response.raise_for_status()


    except requests.RequestException as error:

        print(
            f"FAILED: {error}"
        )

        return []


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    page_text = normalize_spaces(
        soup.get_text(
            "\n",
            strip=True
        )
    )


    current_year = (
        datetime.now(
            timezone.utc
        ).year
    )


    # --------------------------------------------------------
    # EXTRACT ONLY CURRENT YEAR
    #
    # The Fed currently orders the page:
    #
    # 2026 FOMC Meetings
    # ...
    # 2025 FOMC Meetings
    #
    # 2027 appears later under Future Year,
    # so we deliberately stop at 2025.
    # --------------------------------------------------------

    current_marker = (
        f"{current_year} FOMC Meetings"
    )


    previous_marker = (
        f"{current_year - 1} FOMC Meetings"
    )


    start = page_text.find(
        current_marker
    )


    end = page_text.find(
        previous_marker
    )


    if (
        start == -1
        or
        end == -1
        or
        end <= start
    ):

        print(
            "Could not isolate current-year "
            "FOMC section."
        )

        return []


    section_text = page_text[
        start:end
    ]


    meeting_pattern = re.compile(

        r"(January|February|March|April|"
        r"May|June|July|August|September|"
        r"October|November|December)"
        r"\s+"
        r"(\d{1,2})"
        r"\s*[-–]\s*"
        r"(\d{1,2})"
        r"(\*)?",

        re.IGNORECASE
    )


    matches = list(
        meeting_pattern.finditer(
            section_text
        )
    )


    events = []


    now = datetime.now(
        timezone.utc
    )


    for match in matches:

        month_name = (
            match.group(1)
        )


        decision_day = int(
            match.group(3)
        )


        has_projections = (
            match.group(4)
            is not None
        )


        try:

            month_number = (
                datetime.strptime(
                    month_name,
                    "%B"
                ).month
            )


            decision_date = datetime(
                current_year,
                month_number,
                decision_day
            ).date()


        except ValueError:

            continue


        decision_day_end = datetime(

            decision_date.year,
            decision_date.month,
            decision_date.day,

            23,
            59,

            tzinfo=EASTERN

        ).astimezone(
            timezone.utc
        )


        if decision_day_end < now:

            continue


        # RATE DECISION — 2 PM ET

        decision_at = (
            build_utc_datetime(
                decision_date,
                (
                    14,
                    0
                )
            )
        )


        decision_name = (
            "FOMC Rate Decision"
        )


        if has_projections:

            decision_name += (
                " + Economic Projections"
            )


        events.append(

            build_event(

                source_key="FED",

                source_name="Federal Reserve",

                source_url=
                    FED_FOMC_URL,

                event_name=
                    decision_name,

                event_type=(
                    "Central Banking & Rates"
                ),

                scheduled_at=
                    decision_at,

                importance=3
            )
        )


        # PRESS CONFERENCE — 2:30 PM ET

        press_at = (
            build_utc_datetime(
                decision_date,
                (
                    14,
                    30
                )
            )
        )


        events.append(

            build_event(

                source_key="FED",

                source_name="Federal Reserve",

                source_url=
                    FED_FOMC_URL,

                event_name=(
                    "FOMC Press Conference"
                ),

                event_type=(
                    "Central Banking & Rates"
                ),

                scheduled_at=
                    press_at,

                importance=3
            )
        )


    events = deduplicate_events(
        events
    )


    print(
        f"Found {len(events)} "
        f"upcoming FOMC events."
    )


    return events


# ============================================================
# BEA
# ============================================================

def collect_bea():

    print()
    print("-" * 70)
    print("BEA")
    print("-" * 70)

    print(
        "Fetching BEA release schedule..."
    )


    try:

        response = requests.get(
            BEA_SCHEDULE_URL,
            headers=HEADERS,
            timeout=20,
            verify=certifi.where()
        )

        response.raise_for_status()


    except requests.RequestException as error:

        print(
            f"FAILED: {error}"
        )

        return []


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    events = []


    current_year = (
        datetime.now(
            timezone.utc
        ).year
    )


    for row in soup.find_all(
        "tr"
    ):

        cells = row.find_all(
            [
                "td",
                "th"
            ]
        )


        if not cells:

            continue


        cell_texts = [

            normalize_spaces(
                cell.get_text(
                    " ",
                    strip=True
                )
            )

            for cell in cells
        ]


        row_text = (
            " | ".join(
                cell_texts
            )
        )


        rule = match_rule(
            row_text,
            BEA_RELEASE_RULES
        )


        if rule is None:

            continue


        release_date = None


        for cell_text in cell_texts:

            release_date = parse_date(
                cell_text,
                default_year=current_year
            )

            if release_date:

                break


        if release_date is None:

            continue


        release_time = None


        for cell_text in cell_texts:

            release_time = parse_time(
                cell_text
            )

            if release_time:

                break


        if release_time is None:

            continue


        scheduled_at = (
            build_utc_datetime(
                release_date,
                release_time
            )
        )


        event_name = (
            rule["name"]
        )


        row_lower = (
            row_text.lower()
        )


        if (
            rule["name"]
            == "Gross Domestic Product (GDP)"
        ):

            if (
                "advance estimate"
                in row_lower
            ):

                event_name = (
                    "GDP — Advance Estimate"
                )


            elif (
                "second estimate"
                in row_lower
            ):

                event_name = (
                    "GDP — Second Estimate"
                )


            elif (
                "third estimate"
                in row_lower
            ):

                event_name = (
                    "GDP — Third Estimate"
                )


        events.append(

            build_event(

                source_key="BEA",

                source_name=(
                    "U.S. Bureau of "
                    "Economic Analysis"
                ),

                source_url=
                    BEA_SCHEDULE_URL,

                event_name=
                    event_name,

                event_type=
                    rule["type"],

                scheduled_at=
                    scheduled_at,

                importance=
                    rule["importance"]
            )
        )


    events = deduplicate_events(
        events
    )


    print(
        f"Found {len(events)} "
        f"relevant BEA events."
    )


    return events


# ============================================================
# CENSUS
# ============================================================

def collect_census():

    print()
    print("-" * 70)
    print("CENSUS BUREAU")
    print("-" * 70)

    print(
        "Fetching Census economic "
        "indicator calendar..."
    )


    try:

        response = requests.get(
            CENSUS_CALENDAR_URL,
            headers=HEADERS,
            timeout=20,
            verify=certifi.where()
        )

        response.raise_for_status()


    except requests.RequestException as error:

        print(
            f"FAILED: {error}"
        )

        return []


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    events = []


    current_year = (
        datetime.now(
            timezone.utc
        ).year
    )


    for row in soup.find_all(
        "tr"
    ):

        cells = row.find_all(
            [
                "td",
                "th"
            ]
        )


        if not cells:

            continue


        cell_texts = [

            normalize_spaces(
                cell.get_text(
                    " ",
                    strip=True
                )
            )

            for cell in cells
        ]


        row_text = (
            " | ".join(
                cell_texts
            )
        )


        rule = match_rule(
            row_text,
            CENSUS_RELEASE_RULES
        )


        if rule is None:

            continue


        release_date = None


        for cell_text in cell_texts:

            release_date = parse_date(
                cell_text,
                default_year=current_year
            )

            if release_date:

                break


        if release_date is None:

            continue


        release_time = None


        for cell_text in cell_texts:

            release_time = parse_time(
                cell_text
            )

            if release_time:

                break


        if release_time is None:

            continue


        scheduled_at = (
            build_utc_datetime(
                release_date,
                release_time
            )
        )


        events.append(

            build_event(

                source_key="CENSUS",

                source_name=(
                    "U.S. Census Bureau"
                ),

                source_url=
                    CENSUS_CALENDAR_URL,

                event_name=
                    rule["name"],

                event_type=
                    rule["type"],

                scheduled_at=
                    scheduled_at,

                importance=
                    rule["importance"]
            )
        )


    events = deduplicate_events(
        events
    )


    print(
        f"Found {len(events)} "
        f"relevant Census events."
    )


    return events


# ============================================================
# FED MONTHLY CALENDAR
# ============================================================

def build_fed_month_url(
    year,
    month
):

    month_name = datetime(
        year,
        month,
        1
    ).strftime(
        "%B"
    ).lower()


    return (
        f"{FED_MONTHLY_BASE_URL}"
        f"{year}-{month_name}.htm"
    )


def collect_fed_monthly():

    print()
    print("-" * 70)

    print(
        "FEDERAL RESERVE MONTHLY CALENDAR"
    )

    print("-" * 70)


    now = datetime.now(
        timezone.utc
    )


    events = []


    # These are the exact event labels
    # used on the Fed monthly calendar.

    target_rules = [

        {
            "match": "FOMC Minutes",
            "name": "FOMC Minutes",
            "type": "Central Banking & Rates",
            "importance": 3
        },

        {
            "match": "Beige Book",
            "name": "Federal Reserve Beige Book",
            "type": "Central Banking & Rates",
            "importance": 2
        },

        {
            "match": (
                "Industrial Production "
                "and Capacity Utilization"
            ),
            "name": "Industrial Production",
            "type": "Growth & Production",
            "importance": 2
        }

    ]


    for offset in range(
        MONTHS_AHEAD
    ):

        year, month = add_months(
            now.year,
            now.month,
            offset
        )


        url = build_fed_month_url(
            year,
            month
        )


        print(
            f"Fetching Fed calendar "
            f"{year}-{month:02d}..."
        )


        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=20,
                verify=certifi.where()
            )


            if (
                response.status_code
                == 404
            ):

                print(
                    "Schedule not published yet."
                )

                continue


            response.raise_for_status()


        except requests.RequestException as error:

            print(
                f"FAILED: {error}"
            )

            continue


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # ----------------------------------------------------
        # IMPORTANT:
        #
        # The Fed monthly page is displayed as:
        #
        # TIME
        # EVENT
        # DESCRIPTION (sometimes)
        # RELEASE DAY
        #
        # We therefore use the page's stripped text
        # sequence rather than looking for table rows.
        # ----------------------------------------------------

        strings = [

            normalize_spaces(
                text
            )

            for text in soup.stripped_strings

            if normalize_spaces(
                text
            )

        ]


        for index, text in enumerate(
            strings
        ):


            matched_rule = None


            for rule in target_rules:

                if (
                    rule["match"].lower()
                    in text.lower()
                ):

                    matched_rule = rule

                    break


            if matched_rule is None:

                continue


            # ------------------------------------------------
            # FIND NEAREST TIME BEFORE EVENT
            # ------------------------------------------------

            release_time = None


            for previous_index in range(
                index - 1,
                max(
                    -1,
                    index - 6
                ),
                -1
            ):

                release_time = parse_time(
                    strings[
                        previous_index
                    ]
                )


                if release_time:

                    break


            if release_time is None:

                continue


            # ------------------------------------------------
            # FIND RELEASE DAY AFTER EVENT
            #
            # Fed page usually has:
            #
            # FOMC Minutes
            # Meeting of September 15-16
            # 7
            #
            # so scan several strings forward.
            # ------------------------------------------------

            release_day = None


            for next_index in range(
                index + 1,
                min(
                    len(strings),
                    index + 8
                )
            ):

                candidate = (
                    strings[
                        next_index
                    ]
                    .strip()
                )


                if re.fullmatch(
                    r"\d{1,2}",
                    candidate
                ):

                    day_value = int(
                        candidate
                    )


                    if (
                        1
                        <= day_value
                        <= 31
                    ):

                        release_day = (
                            day_value
                        )

                        break


            if release_day is None:

                continue


            try:

                release_date = datetime(
                    year,
                    month,
                    release_day
                ).date()

            except ValueError:

                continue


            scheduled_at = (
                build_utc_datetime(
                    release_date,
                    release_time
                )
            )


            events.append(

                build_event(

                    source_key="FED",

                    source_name=(
                        "Federal Reserve"
                    ),

                    source_url=url,

                    event_name=
                        matched_rule[
                            "name"
                        ],

                    event_type=
                        matched_rule[
                            "type"
                        ],

                    scheduled_at=
                        scheduled_at,

                    importance=
                        matched_rule[
                            "importance"
                        ]
                )
            )


    events = deduplicate_events(
        events
    )


    print(
        f"Found {len(events)} "
        f"additional Fed events."
    )


    return events


# ============================================================
# COLLECT EVERYTHING
# ============================================================

def collect():

    print()
    print("=" * 70)

    print(
        "UNITED STATES MACRO CALENDAR"
    )

    print("=" * 70)


    events = []


    events.extend(
        collect_bls()
    )


    events.extend(
        collect_fomc()
    )


    events.extend(
        collect_bea()
    )


    events.extend(
        collect_census()
    )


    events.extend(
        collect_fed_monthly()
    )


    events = deduplicate_events(
        events
    )


    events.sort(
        key=lambda event:
            event["scheduled_at"]
    )


    print()
    print("=" * 70)

    print(
        "UNITED STATES CALENDAR REPORT"
    )

    print("=" * 70)


    print(
        f"Total events: "
        f"{len(events)}"
    )


    print("=" * 70)


    return events