import csv
import io
import os
import re
import sqlite3
from datetime import datetime, timezone

import requests


DATABASE_NAME = "Macrodrive.db"

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BEA_API_URL = "https://apps.bea.gov/api/data/"
CENSUS_EITS_BASE = "https://api.census.gov/data/timeseries/eits"

BEA_API_KEY = os.getenv("BEA_API_KEY", "").strip()
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "").strip()

BLS_SERIES = {
    "cpi": "CUUR0000SA0",
    "ppi": "WPUFD4",
    "payrolls": "CES0000000001",
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def connect_database():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def parse_event_datetime(value):
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def shift_month(year, month, offset):
    index = year * 12 + (month - 1) + offset
    return index // 12, index % 12 + 1


def find_month_value(observations, year, month):
    for item in observations:
        if item["year"] == year and item["month"] == month:
            return item["value"]
    return None


def yoy_percent(observations, year, month):
    current = find_month_value(observations, year, month)
    prior = find_month_value(observations, year - 1, month)

    if current is None or prior in (None, 0):
        return None

    return ((current / prior) - 1.0) * 100.0


def monthly_percent_change(observations, year, month):
    current = find_month_value(observations, year, month)
    py, pm = shift_month(year, month, -1)
    previous = find_month_value(observations, py, pm)

    if current is None or previous in (None, 0):
        return None

    return ((current / previous) - 1.0) * 100.0


def monthly_level_change(observations, year, month):
    current = find_month_value(observations, year, month)
    py, pm = shift_month(year, month, -1)
    previous = find_month_value(observations, py, pm)

    if current is None or previous is None:
        return None

    return current - previous


def format_percent(value):
    if value is None:
        return None
    return f"{value:.1f}%"


def format_payroll(value):
    if value is None:
        return None

    rounded = int(round(value))
    return f"+{rounded}K" if rounded > 0 else f"{rounded}K"


def format_thousands(value):
    if value is None:
        return None

    rounded = int(round(value))
    return f"{rounded:,}K"


def format_number(value, decimals=1):
    if value is None:
        return None

    return f"{value:.{decimals}f}"


def update_event(cursor, event_key, previous, actual, unit=""):
    cursor.execute(
        """
        UPDATE calendar_events
        SET previous = ?, actual = ?, unit = ?
        WHERE event_key = ?
        """,
        (previous, actual, unit, event_key),
    )


# ============================================================
# BLS
# ============================================================

def fetch_bls_series(series_ids, start_year, end_year):
    payload = {
        "seriesid": list(series_ids),
        "startyear": str(start_year),
        "endyear": str(end_year),
    }

    try:
        response = requests.post(
            BLS_API_URL,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as error:
        print(f"FAILED to fetch BLS values: {error}")
        return {}

    if data.get("status") != "REQUEST_SUCCEEDED":
        print("BLS API request did not succeed.")
        for message in data.get("message", []):
            print(message)
        return {}

    output = {}

    for series in data.get("Results", {}).get("series", []):
        series_id = series.get("seriesID")
        observations = []

        for item in series.get("data", []):
            period = item.get("period", "")

            if not period.startswith("M") or period == "M13":
                continue

            try:
                observations.append(
                    {
                        "year": int(item["year"]),
                        "month": int(period[1:]),
                        "value": float(item["value"]),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue

        observations.sort(key=lambda item: (item["year"], item["month"]))
        output[series_id] = observations

    return output


def update_bls_values(connection):
    print()
    print("-" * 70)
    print("BLS VALUES")
    print("-" * 70)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT event_key, event_name, scheduled_at
        FROM calendar_events
        WHERE event_name IN (
            'Consumer Price Index (CPI)',
            'Producer Price Index (PPI)',
            'Employment Situation'
        )
        ORDER BY scheduled_at ASC
        """
    )

    events = cursor.fetchall()

    if not events:
        print("No matching BLS events found.")
        return 0

    years = []

    for event in events:
        dt = parse_event_datetime(event["scheduled_at"])
        if dt:
            years.append(dt.year)

    if not years:
        return 0

    data = fetch_bls_series(
        BLS_SERIES.values(),
        min(years) - 2,
        max(years),
    )

    if not data:
        return 0

    now = datetime.now(timezone.utc)
    updated = 0

    for event in events:
        dt = parse_event_datetime(event["scheduled_at"])

        if dt is None:
            continue

        data_year, data_month = shift_month(dt.year, dt.month, -1)

        previous = None
        actual = None

        if event["event_name"] == "Consumer Price Index (CPI)":
            observations = data.get(BLS_SERIES["cpi"], [])

            actual_value = yoy_percent(
                observations,
                data_year,
                data_month,
            )

            py, pm = shift_month(data_year, data_month, -1)
            previous_value = yoy_percent(observations, py, pm)

            previous = format_percent(previous_value)
            actual = format_percent(actual_value)

        elif event["event_name"] == "Producer Price Index (PPI)":
            observations = data.get(BLS_SERIES["ppi"], [])

            actual_value = yoy_percent(
                observations,
                data_year,
                data_month,
            )

            py, pm = shift_month(data_year, data_month, -1)
            previous_value = yoy_percent(observations, py, pm)

            previous = format_percent(previous_value)
            actual = format_percent(actual_value)

        elif event["event_name"] == "Employment Situation":
            observations = data.get(BLS_SERIES["payrolls"], [])

            actual_value = monthly_level_change(
                observations,
                data_year,
                data_month,
            )

            py, pm = shift_month(data_year, data_month, -1)
            previous_value = monthly_level_change(observations, py, pm)

            previous = format_payroll(previous_value)
            actual = format_payroll(actual_value)

        if dt > now:
            actual = None

        if previous is None and actual is None:
            continue

        update_event(
            cursor,
            event["event_key"],
            previous,
            actual,
            "",
        )
        updated += 1

    connection.commit()
    print(f"BLS events updated: {updated}")
    return updated


# ============================================================
# BEA API
# ============================================================

def bea_get_data(table_name, frequency, year):
    if not BEA_API_KEY:
        print("BEA_API_KEY is not set; skipping BEA values.")
        return []

    params = {
        "UserID": BEA_API_KEY,
        "method": "GetData",
        "datasetname": "NIPA",
        "TableName": table_name,
        "Frequency": frequency,
        "Year": str(year),
        "ResultFormat": "JSON",
    }

    try:
        response = requests.get(
            BEA_API_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as error:
        print(f"FAILED to fetch BEA {table_name}: {error}")
        return []

    try:
        return payload["BEAAPI"]["Results"]["Data"]
    except (KeyError, TypeError):
        return []


def clean_bea_number(value):
    if value is None:
        return None

    text = str(value).replace(",", "").strip()

    try:
        return float(text)
    except ValueError:
        return None


def bea_period_sort_key(period):
    match = re.fullmatch(r"(\d{4})Q([1-4])", str(period))
    if match:
        return int(match.group(1)), int(match.group(2))

    match = re.fullmatch(r"(\d{4})M(\d{1,2})", str(period))
    if match:
        return int(match.group(1)), int(match.group(2))

    return 0, 0


def fetch_bea_gdp_growth(years):
    output = {}

    for year in sorted(set(years)):
        rows = bea_get_data("T10101", "Q", year)

        for row in rows:
            description = str(row.get("LineDescription", "")).lower()

            if "gross domestic product" not in description:
                continue

            # Table 1.1.1 is percent change from preceding period.
            value = clean_bea_number(row.get("DataValue"))
            period = row.get("TimePeriod")

            if value is not None and period:
                output[str(period)] = value

    return output


def fetch_bea_pce_price_growth(years):
    output = {}

    # Table 2.3.4: Price Indexes for Personal Consumption Expenditures
    # We use the total PCE line and calculate YoY from monthly index levels
    # when monthly rows are available.
    monthly_levels = []

    for year in sorted(set(years)):
        rows = bea_get_data("T20304", "M", year)

        for row in rows:
            description = str(row.get("LineDescription", "")).strip().lower()

            if description not in (
                "personal consumption expenditures",
                "personal consumption expenditures (pce)",
            ):
                continue

            value = clean_bea_number(row.get("DataValue"))
            period = str(row.get("TimePeriod", ""))

            match = re.fullmatch(r"(\d{4})M(\d{1,2})", period)

            if value is not None and match:
                monthly_levels.append(
                    {
                        "year": int(match.group(1)),
                        "month": int(match.group(2)),
                        "value": value,
                    }
                )

    monthly_levels.sort(key=lambda item: (item["year"], item["month"]))

    for item in monthly_levels:
        value = yoy_percent(
            monthly_levels,
            item["year"],
            item["month"],
        )

        if value is not None:
            output[(item["year"], item["month"])] = value

    return output


def update_bea_values(connection):
    print()
    print("-" * 70)
    print("BEA VALUES")
    print("-" * 70)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT event_key, event_name, scheduled_at
        FROM calendar_events
        WHERE event_name LIKE 'GDP%'
           OR event_name = 'Personal Income & Outlays / PCE'
        ORDER BY scheduled_at ASC
        """
    )

    events = cursor.fetchall()

    if not events:
        print("No matching BEA events found.")
        return 0

    years = []

    for event in events:
        dt = parse_event_datetime(event["scheduled_at"])
        if dt:
            years.extend([dt.year - 1, dt.year])

    gdp = fetch_bea_gdp_growth(years)
    pce = fetch_bea_pce_price_growth(years)

    now = datetime.now(timezone.utc)
    updated = 0

    for event in events:
        dt = parse_event_datetime(event["scheduled_at"])

        if dt is None:
            continue

        previous = None
        actual = None

        if event["event_name"].startswith("GDP"):
            release_quarter = ((dt.month - 1) // 3) + 1
            data_quarter = release_quarter - 1
            data_year = dt.year

            if data_quarter == 0:
                data_quarter = 4
                data_year -= 1

            period = f"{data_year}Q{data_quarter}"

            previous_quarter = data_quarter - 1
            previous_year = data_year

            if previous_quarter == 0:
                previous_quarter = 4
                previous_year -= 1

            previous_period = f"{previous_year}Q{previous_quarter}"

            previous = format_percent(gdp.get(previous_period))
            actual = format_percent(gdp.get(period))

        elif event["event_name"] == "Personal Income & Outlays / PCE":
            data_year, data_month = shift_month(dt.year, dt.month, -1)
            py, pm = shift_month(data_year, data_month, -1)

            previous = format_percent(pce.get((py, pm)))
            actual = format_percent(pce.get((data_year, data_month)))

        if dt > now:
            actual = None

        if previous is None and actual is None:
            continue

        update_event(
            cursor,
            event["event_key"],
            previous,
            actual,
            "",
        )
        updated += 1

    connection.commit()
    print(f"BEA events updated: {updated}")
    return updated


# ============================================================
# CENSUS ECONOMIC INDICATORS API
# ============================================================

def census_get_range(
    dataset,
    start_year,
    start_month,
    end_year,
    end_month,
):
    """
    Fetch one Census EITS dataset for a complete month range.

    Census documents the time predicate format as:
        from+YYYY-MM+to+YYYY-MM

    requests will URL-encode spaces as '+', so passing the value
    "from YYYY-MM to YYYY-MM" produces the documented query form.
    """
    if not CENSUS_API_KEY:
        print(
            "CENSUS_API_KEY is not set; "
            "skipping Census values."
        )
        return []

    url = f"{CENSUS_EITS_BASE}/{dataset}"

    params = {
        "get": (
            "data_type_code,time_slot_id,"
            "seasonally_adj,category_code,"
            "cell_value,error_data"
        ),
        "time": (
            f"from {start_year}-{start_month:02d} "
            f"to {end_year}-{end_month:02d}"
        ),
        "key": CENSUS_API_KEY,
    }

    # The Advance Durable Goods (advm3) dataset requires
    # an explicit United States geography predicate.
    if dataset == "advm3":
        params["for"] = "us:*"

    try:
        response = requests.get(
            url,
            params=params,
            timeout=60,
        )

        if response.status_code != 200:
            # Do not print response.url because it contains the API key.
            print(
                f"FAILED to fetch Census {dataset}: "
                f"HTTP {response.status_code}"
            )

            body = response.text.strip()

            if body:
                print(
                    "  Census response: "
                    + body[:300]
                )

            return []

        rows = response.json()

    except Exception as error:
        print(
            f"FAILED to fetch Census {dataset}: "
            f"{error}"
        )
        return []

    if not rows or len(rows) < 2:
        return []

    headers = rows[0]

    return [
        dict(zip(headers, row))
        for row in rows[1:]
    ]


def census_numeric(row):
    try:
        return float(
            str(
                row.get(
                    "cell_value",
                    "",
                )
            ).replace(",", "")
        )
    except (TypeError, ValueError):
        return None


def parse_census_time(row):
    # Census includes the predicate-only "time" field in returned
    # time-series rows even though it is not requested in get=.
    value = str(
        row.get("time")
        or ""
    )

    match = re.fullmatch(
        r"(\d{4})-(\d{1,2})",
        value,
    )

    if not match:
        return None

    return (
        int(match.group(1)),
        int(match.group(2)),
    )


def group_census_rows(rows):
    grouped = {}

    for row in rows:
        period = parse_census_time(row)

        if period is None:
            continue

        grouped.setdefault(
            period,
            [],
        ).append(row)

    return grouped


def choose_census_value(
    rows,
    preferred_types=(),
    preferred_categories=(),
):
    candidates = []

    preferred_types = {
        item.upper()
        for item in preferred_types
    }

    preferred_categories = {
        item.upper()
        for item in preferred_categories
    }

    for row in rows:
        value = census_numeric(row)

        if value is None:
            continue

        score = 0

        data_type = str(
            row.get(
                "data_type_code",
                "",
            )
        ).upper()

        category = str(
            row.get(
                "category_code",
                "",
            )
        ).upper()

        adjusted = str(
            row.get(
                "seasonally_adj",
                "",
            )
        ).upper()

        error_data = str(
            row.get(
                "error_data",
                "",
            )
        ).lower()

        # Prefer published estimates rather than error/variance rows.
        if error_data in (
            "",
            "no",
            "n",
            "0",
        ):
            score += 5

        if adjusted in (
            "YES",
            "Y",
            "S",
            "SA",
        ):
            score += 10

        if data_type in preferred_types:
            score += 20

        if category in preferred_categories:
            score += 20

        candidates.append(
            (
                score,
                value,
                row,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1]


def census_cached_month_value(
    cache,
    dataset,
    year,
    month,
    event_name,
):
    rows = (
        cache
        .get(dataset, {})
        .get(
            (year, month),
            [],
        )
    )

    if not rows:
        return None

    if event_name == "Retail Sales":
        return choose_census_value(
            rows,
            preferred_types=(
                "TOTAL",
                "SM",
                "MPC",
            ),
            preferred_categories=(
                "44X72",
                "TOTAL",
            ),
        )

    if event_name == "Durable Goods Orders":
        return choose_census_value(
            rows,
            preferred_types=(
                "ORDER",
                "ORDERS",
                "MPC",
            ),
            preferred_categories=(
                "TOTAL",
                "DG",
            ),
        )

    if event_name == "Housing Starts & Building Permits":
        return choose_census_value(
            rows,
            preferred_types=(
                "STARTS",
                "TOTAL",
            ),
            preferred_categories=(
                "TOTAL",
            ),
        )

    if event_name == "New Home Sales":
        return choose_census_value(
            rows,
            preferred_types=(
                "TOTAL",
                "SAAR",
            ),
            preferred_categories=(
                "TOTAL",
            ),
        )

    return None


def update_census_values(connection):
    print()
    print("-" * 70)
    print("CENSUS VALUES")
    print("-" * 70)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            event_key,
            event_name,
            scheduled_at
        FROM calendar_events
        WHERE event_name IN (
            'Retail Sales',
            'Durable Goods Orders',
            'Housing Starts & Building Permits',
            'New Home Sales'
        )
        ORDER BY scheduled_at ASC
        """
    )

    events = cursor.fetchall()

    if not events:
        print(
            "No matching Census events found."
        )
        return 0

    if not CENSUS_API_KEY:
        print(
            "CENSUS_API_KEY is not set; "
            "skipping Census values."
        )
        return 0

    dataset_map = {
        "Retail Sales":
            "marts",

        "Durable Goods Orders":
            "advm3",

        "Housing Starts & Building Permits":
            "resconst",

        "New Home Sales":
            "ressales",
    }

    required_periods = []

    for event in events:
        dt = parse_event_datetime(
            event["scheduled_at"]
        )

        if dt is None:
            continue

        data_year, data_month = shift_month(
            dt.year,
            dt.month,
            -1,
        )

        required_periods.append(
            (
                data_year,
                data_month,
            )
        )

    if not required_periods:
        print(
            "No valid Census event dates found."
        )
        return 0

    first_year, first_month = min(
        required_periods
    )

    last_year, last_month = max(
        required_periods
    )

    # Two extra months are needed for Previous and MoM calculations.
    first_year, first_month = shift_month(
        first_year,
        first_month,
        -2,
    )

    print(
        "Fetching each Census dataset once "
        f"for {first_year}-{first_month:02d} "
        f"through {last_year}-{last_month:02d}..."
    )

    cache = {}

    for dataset in sorted(
        set(
            dataset_map.values()
        )
    ):
        print(
            f"Fetching Census dataset: "
            f"{dataset}..."
        )

        rows = census_get_range(
            dataset,
            first_year,
            first_month,
            last_year,
            last_month,
        )

        cache[dataset] = (
            group_census_rows(
                rows
            )
        )

        print(
            f"  Cached {len(rows)} rows "
            f"across "
            f"{len(cache[dataset])} months."
        )

    now = datetime.now(
        timezone.utc
    )

    updated = 0

    for event in events:
        dt = parse_event_datetime(
            event["scheduled_at"]
        )

        if dt is None:
            continue

        data_year, data_month = shift_month(
            dt.year,
            dt.month,
            -1,
        )

        previous_year, previous_month = shift_month(
            data_year,
            data_month,
            -1,
        )

        dataset = dataset_map[
            event["event_name"]
        ]

        current_level = (
            census_cached_month_value(
                cache,
                dataset,
                data_year,
                data_month,
                event["event_name"],
            )
        )

        previous_level = (
            census_cached_month_value(
                cache,
                dataset,
                previous_year,
                previous_month,
                event["event_name"],
            )
        )

        previous = None
        actual = None

        if event["event_name"] in (
            "Retail Sales",
            "Durable Goods Orders",
        ):
            older_year, older_month = (
                shift_month(
                    previous_year,
                    previous_month,
                    -1,
                )
            )

            older_level = (
                census_cached_month_value(
                    cache,
                    dataset,
                    older_year,
                    older_month,
                    event["event_name"],
                )
            )

            if (
                previous_level is not None
                and
                older_level not in (
                    None,
                    0,
                )
            ):
                previous = format_percent(
                    (
                        (
                            previous_level
                            / older_level
                        )
                        - 1.0
                    )
                    * 100.0
                )

            if (
                current_level is not None
                and
                previous_level not in (
                    None,
                    0,
                )
            ):
                actual = format_percent(
                    (
                        (
                            current_level
                            / previous_level
                        )
                        - 1.0
                    )
                    * 100.0
                )

        else:
            previous = format_thousands(
                previous_level
            )

            actual = format_thousands(
                current_level
            )

        if dt > now:
            actual = None

        if (
            previous is None
            and
            actual is None
        ):
            continue

        update_event(
            cursor,
            event["event_key"],
            previous,
            actual,
            "",
        )

        updated += 1

    connection.commit()

    print(
        f"Census events updated: "
        f"{updated}"
    )

    return updated


# ============================================================
# FEDERAL RESERVE INDUSTRIAL PRODUCTION
# ============================================================

FED_IP_CSV_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv"
    "?id=INDPRO"
)


def fetch_fed_industrial_production():
    try:
        response = requests.get(
            FED_IP_CSV_URL,
            timeout=30,
        )
        response.raise_for_status()
    except Exception as error:
        print(
            f"FAILED to fetch Industrial Production: {error}"
        )
        return []

    observations = []

    try:
        reader = csv.DictReader(
            io.StringIO(response.text)
        )

        for row in reader:
            date_text = (
                row.get("observation_date")
                or row.get("DATE")
                or row.get("Date")
                or ""
            )

            raw_value = row.get("INDPRO", "")

            if not date_text or raw_value in ("", "."):
                continue

            try:
                dt = datetime.strptime(
                    date_text,
                    "%Y-%m-%d",
                )
                value = float(raw_value)
            except ValueError:
                continue

            observations.append(
                {
                    "year": dt.year,
                    "month": dt.month,
                    "value": value,
                }
            )

    except Exception as error:
        print(
            f"Could not parse Industrial Production data: {error}"
        )
        return []

    observations.sort(
        key=lambda item: (
            item["year"],
            item["month"],
        )
    )

    return observations


def update_fed_values(connection):
    print()
    print("-" * 70)
    print("FEDERAL RESERVE VALUES")
    print("-" * 70)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT event_key, event_name, scheduled_at
        FROM calendar_events
        WHERE event_name = 'Industrial Production'
        ORDER BY scheduled_at ASC
        """
    )

    events = cursor.fetchall()

    if not events:
        print("No Industrial Production events found.")
        return 0

    observations = fetch_fed_industrial_production()

    if not observations:
        print("Industrial Production values unavailable.")
        return 0

    now = datetime.now(timezone.utc)
    updated = 0

    for event in events:
        dt = parse_event_datetime(
            event["scheduled_at"]
        )

        if dt is None:
            continue

        data_year, data_month = shift_month(
            dt.year,
            dt.month,
            -1,
        )

        previous_year, previous_month = shift_month(
            data_year,
            data_month,
            -1,
        )

        actual_value = monthly_percent_change(
            observations,
            data_year,
            data_month,
        )

        previous_value = monthly_percent_change(
            observations,
            previous_year,
            previous_month,
        )

        previous = format_percent(previous_value)
        actual = format_percent(actual_value)

        if dt > now:
            actual = None

        if previous is None and actual is None:
            continue

        update_event(
            cursor,
            event["event_key"],
            previous,
            actual,
            "",
        )
        updated += 1

    connection.commit()

    print(
        f"Federal Reserve events updated: {updated}"
    )

    return updated


# ============================================================
# FOMC TARGET RATE VALUES
# ============================================================

FED_FOMC_PRESS_RELEASES = (
    "https://www.federalreserve.gov/newsevents/pressreleases/"
    "{year}-press-fomc.htm"
)
FED_BASE_URL = "https://www.federalreserve.gov"


def parse_fed_fraction(value):
    value = value.strip().replace("‑", "-").replace("–", "-")
    mixed = re.fullmatch(r"(\d+)-(\d+)/(\d+)", value)
    if mixed:
        return float(mixed.group(1)) + float(mixed.group(2)) / float(mixed.group(3))
    fraction = re.fullmatch(r"(\d+)/(\d+)", value)
    if fraction:
        return float(fraction.group(1)) / float(fraction.group(2))
    try:
        return float(value)
    except ValueError:
        return None


def format_rate_number(value):
    if value is None:
        return None
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    return text


def extract_target_range(text):
    normalized = (
        text.replace("‑", "-")
            .replace("–", "-")
            .replace("—", "-")
    )
    pattern = re.compile(
        r"target range for the federal funds rate(?:\s+at|\s+of)?\s+"
        r"(\d+(?:-\d+/\d+|/\d+|(?:\.\d+)?))\s+to\s+"
        r"(\d+(?:-\d+/\d+|/\d+|(?:\.\d+)?))\s+percent",
        re.IGNORECASE,
    )
    match = pattern.search(normalized)
    if not match:
        return None
    lower = parse_fed_fraction(match.group(1))
    upper = parse_fed_fraction(match.group(2))
    if lower is None or upper is None:
        return None
    return f"{format_rate_number(lower)}–{format_rate_number(upper)}%"


def fetch_fomc_rate_history(years):
    history = []

    for year in sorted(set(years)):
        url = FED_FOMC_PRESS_RELEASES.format(year=year)
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except Exception as error:
            print(f"FAILED to fetch FOMC press-release index {year}: {error}")
            continue

        links = re.findall(
            r'href=["\']([^"\']*monetary(\d{8})a\.htm[^"\']*)["\']',
            response.text,
            re.IGNORECASE,
        )

        seen = set()
        for href, date_code in links:
            if date_code in seen:
                continue
            seen.add(date_code)

            statement_url = href
            if statement_url.startswith("/"):
                statement_url = FED_BASE_URL + statement_url
            elif not statement_url.startswith("http"):
                statement_url = FED_BASE_URL + "/" + statement_url.lstrip("/")

            try:
                statement = requests.get(statement_url, timeout=30)
                statement.raise_for_status()
            except Exception:
                continue

            plain = re.sub(r"<[^>]+>", " ", statement.text)
            plain = re.sub(r"\s+", " ", plain)
            rate_range = extract_target_range(plain)
            if rate_range is None:
                continue

            try:
                decision_date = datetime.strptime(date_code, "%Y%m%d").date()
            except ValueError:
                continue

            history.append((decision_date, rate_range))

    history.sort(key=lambda item: item[0])
    return history


def update_fomc_rate_values(connection):
    print()
    print("-" * 70)
    print("FOMC TARGET RATE VALUES")
    print("-" * 70)

    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT event_key, event_name, scheduled_at
        FROM calendar_events
        WHERE event_name LIKE 'FOMC Rate Decision%'
        ORDER BY scheduled_at ASC
        """
    )
    events = cursor.fetchall()
    if not events:
        print("No FOMC Rate Decision events found.")
        return 0

    years = []
    for event in events:
        dt = parse_event_datetime(event["scheduled_at"])
        if dt:
            years.extend([dt.year - 1, dt.year])

    history = fetch_fomc_rate_history(years)
    if not history:
        print("FOMC target-rate history unavailable.")
        return 0

    now = datetime.now(timezone.utc)
    updated = 0

    for event in events:
        dt = parse_event_datetime(event["scheduled_at"])
        if dt is None:
            continue

        event_day = dt.date()
        prior = [item for item in history if item[0] < event_day]
        same_day = [item for item in history if item[0] == event_day]

        previous = prior[-1][1] if prior else None
        actual = same_day[-1][1] if same_day else None

        if dt > now:
            actual = None

        if previous is None and actual is None:
            continue

        update_event(cursor, event["event_key"], previous, actual, "")
        updated += 1

    connection.commit()
    print(f"FOMC rate events updated: {updated}")
    return updated


# ============================================================
# MAIN
# ============================================================

def update_calendar_values():
    print()
    print("=" * 70)
    print("Macrodrive CALENDAR VALUES")
    print("=" * 70)

    if not BEA_API_KEY:
        print("Warning: BEA_API_KEY is not available in this shell.")

    if not CENSUS_API_KEY:
        print("Warning: CENSUS_API_KEY is not available in this shell.")

    connection = connect_database()

    total = 0

    try:
        total += update_bls_values(connection)
        total += update_bea_values(connection)
        total += update_census_values(connection)
        total += update_fed_values(connection)
        total += update_fomc_rate_values(connection)
    finally:
        connection.close()

    print()
    print("=" * 70)
    print("CALENDAR VALUE UPDATE REPORT")
    print("=" * 70)
    print(f"Events updated: {total}")
    print("=" * 70)


if __name__ == "__main__":
    update_calendar_values()
