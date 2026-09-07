from datetime import timezone
from email.utils import parsedate_to_datetime

from dateutil import parser


def normalize_date(date_string):

    if not date_string:
        return None

    if date_string == "Unknown":
        return None

    # --------------------------------------------------------
    # TRY RSS / EMAIL-STYLE DATE
    #
    # Example:
    # Sun, 06 Sep 2026 16:30:00 +0800
    # --------------------------------------------------------

    try:

        dt = parsedate_to_datetime(
            date_string
        )

        if dt.tzinfo is None:

            dt = dt.replace(
                tzinfo=timezone.utc
            )

        dt = dt.astimezone(
            timezone.utc
        )

        return dt.isoformat()

    except (
        TypeError,
        ValueError,
        OverflowError
    ):

        pass

    # --------------------------------------------------------
    # TRY GENERAL DATE PARSER
    #
    # Handles things such as:
    #
    # 2026-09-06T12:00:00Z
    # September 6, 2026
    # 2026-09-06
    # --------------------------------------------------------

    try:

        dt = parser.parse(
            date_string
        )

        if dt.tzinfo is None:

            dt = dt.replace(
                tzinfo=timezone.utc
            )

        dt = dt.astimezone(
            timezone.utc
        )

        return dt.isoformat()

    except (
        TypeError,
        ValueError,
        OverflowError
    ):

        return None