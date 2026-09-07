import time
import requests
import certifi

from database import (
    create_database,
    get_articles_without_text,
    save_article_text,
    update_article_access
)

from extractor import (
    extract_article_text
)

from accessdetector import (
    detect_access,
    get_source_default
)


MINIMUM_PROVIDED_TEXT_LENGTH = 150


HEADERS = {
    "User-Agent": "Macrodrive/1.0"
}


# ============================================================
# GET PAGE HTML FOR ACCESS DETECTION
# ============================================================

def get_page_html(url):

    try:

        response = requests.get(
            url,
            timeout=15,
            verify=certifi.where(),
            headers=HEADERS
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException:

        return ""


# ============================================================
# METADATA TEXT
# ============================================================

def build_metadata_text(
    title,
    description,
    provided_text
):

    pieces = []


    for value in (
        title,
        description,
        provided_text
    ):

        if not value:
            continue

        value = value.strip()

        if (
            value
            and value not in pieces
        ):

            pieces.append(
                value
            )


    return "\n\n".join(
        pieces
    )


# ============================================================
# PROCESS ARTICLES
# ============================================================

def process_article_text():

    create_database()


    articles = (
        get_articles_without_text()
    )


    print(
        f"\nFound {len(articles)} "
        f"articles without processed text.\n"
    )


    metadata_count = 0
    provided_count = 0
    downloaded_count = 0
    failed_count = 0

    free_count = 0
    paywalled_count = 0
    unknown_count = 0


    for article in articles:


        article_id = article[0]

        source = article[1]

        title = article[2]

        url = article[3]

        provided_text = (
            article[4] or ""
        )

        description = (
            article[5] or ""
        )

        text_mode = (
            article[6] or "full"
        )

        existing_access = (
            article[7] or "unknown"
        )


        print(
            "-" * 70
        )

        print(
            f"ID: {article_id}"
        )

        print(
            f"Source: {source}"
        )

        print(
            f"Title: {title}"
        )

        print(
            f"Text mode: {text_mode}"
        )


        # ----------------------------------------------------
        # METADATA-ONLY SOURCES
        # ----------------------------------------------------

        if (
            text_mode
            == "metadata_only"
        ):


            metadata_text = (
                build_metadata_text(
                    title,
                    description,
                    provided_text
                )
            )


            if metadata_text:

                save_article_text(
                    article_id,
                    metadata_text
                )

                metadata_count += 1


                access = (
                    get_source_default(
                        source
                    )
                )


                update_article_access(
                    article_id,
                    access
                )


                if access == "paywalled":

                    paywalled_count += 1

                elif access == "free":

                    free_count += 1

                else:

                    unknown_count += 1


                print(
                    "Saved metadata only."
                )

                print(
                    f"Access: {access}"
                )


            else:

                failed_count += 1

                print(
                    "No metadata available."
                )


            continue


        # ----------------------------------------------------
        # PROVIDED MODE
        # ----------------------------------------------------

        if (
            text_mode == "provided"
            and provided_text
        ):


            save_article_text(
                article_id,
                provided_text
            )


            provided_count += 1


            access = (
                get_source_default(
                    source
                )
            )


            update_article_access(
                article_id,
                access
            )


            if access == "free":

                free_count += 1

            elif access == "paywalled":

                paywalled_count += 1

            else:

                unknown_count += 1


            print(
                "Saved source-provided text."
            )

            print(
                f"Access: {access}"
            )


            continue


        # ----------------------------------------------------
        # FULL MODE
        #
        # If RSS already supplied substantial text, use it.
        # ----------------------------------------------------

        if (
            len(provided_text)
            >= MINIMUM_PROVIDED_TEXT_LENGTH
        ):


            save_article_text(
                article_id,
                provided_text
            )


            provided_count += 1


            # For known-free sources we can safely set free.
            #
            # Mixed sources remain unknown unless we have
            # page-level evidence.

            access = (
                get_source_default(
                    source
                )
            )


            update_article_access(
                article_id,
                access
            )


            if access == "free":

                free_count += 1

            elif access == "paywalled":

                paywalled_count += 1

            else:

                unknown_count += 1


            print(
                "Using source-provided text."
            )

            print(
                f"Access: {access}"
            )


            continue


        # ----------------------------------------------------
        # DOWNLOAD ACCESSIBLE PAGE
        # ----------------------------------------------------

        print(
            "Downloading webpage..."
        )


        page_html = get_page_html(
            url
        )


        extracted_text = (
            extract_article_text(
                url
            )
        )


        # ----------------------------------------------------
        # DETECT ACCESS
        # ----------------------------------------------------

        access = detect_access(
            source=source,
            page_text=page_html,
            extracted_text=(
                extracted_text or ""
            )
        )


        update_article_access(
            article_id,
            access
        )


        if access == "free":

            free_count += 1

        elif access == "paywalled":

            paywalled_count += 1

        else:

            unknown_count += 1


        print(
            f"Access: {access}"
        )


        # ----------------------------------------------------
        # SAVE EXTRACTED TEXT
        # ----------------------------------------------------

        if extracted_text:


            save_article_text(
                article_id,
                extracted_text
            )


            downloaded_count += 1


            print(
                f"Saved "
                f"{len(extracted_text)} "
                f"characters."
            )


            time.sleep(1)


            continue


        # ----------------------------------------------------
        # DESCRIPTION FALLBACK
        # ----------------------------------------------------

        if description:


            save_article_text(
                article_id,
                description
            )


            provided_count += 1


            print(
                "Extraction failed."
            )

            print(
                "Using description."
            )


            time.sleep(1)


            continue


        # ----------------------------------------------------
        # FAILURE
        # ----------------------------------------------------

        failed_count += 1


        print(
            "No usable text available."
        )


        time.sleep(1)


    # ========================================================
    # REPORT
    # ========================================================

    print()

    print("=" * 70)

    print(
        "TEXT PROCESSING REPORT"
    )

    print("=" * 70)


    print(
        f"Metadata only:       "
        f"{metadata_count}"
    )

    print(
        f"Source-provided:     "
        f"{provided_count}"
    )

    print(
        f"Downloaded webpages: "
        f"{downloaded_count}"
    )

    print(
        f"Failed:              "
        f"{failed_count}"
    )


    print()

    print(
        "ACCESS DETECTION"
    )

    print("-" * 70)


    print(
        f"Free:                 "
        f"{free_count}"
    )

    print(
        f"Paywalled:            "
        f"{paywalled_count}"
    )

    print(
        f"Unknown:              "
        f"{unknown_count}"
    )


    print("=" * 70)


if __name__ == "__main__":

    process_article_text()