from sources import SOURCES


FAILURES = []


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        FAILURES.append(label)


def main():
    print("=" * 60)
    print("test_sources.py")
    print("=" * 60)

    check("SOURCES is a non-empty list", isinstance(SOURCES, list) and len(SOURCES) > 0)

    required_keys = {"name", "type", "url", "enabled"}

    for source in SOURCES:
        check(
            f"{source.get('name')} has required keys",
            required_keys <= set(source.keys()),
        )
        check(
            f"{source.get('name')} url is http(s)",
            str(source.get("url", "")).startswith("http"),
        )

    # --- No duplicate feed URLs (would double-collect) ----------------
    urls = [source["url"] for source in SOURCES]
    check("no duplicate feed URLs", len(urls) == len(set(urls)))

    # --- New Asian sources present ------------------------------------
    names = {source["name"] for source in SOURCES}
    expected_new = {
        "Nikkei Asia",
        "Mint",
        "Economic Times",
        "Yonhap",
        "Bank of Japan",
        "Reserve Bank of India",
    }
    check("all new Asian sources present", expected_new <= names)

    # --- New sources carry the region tag -----------------------------
    asian = [s for s in SOURCES if s["name"] in expected_new]
    check(
        "all new Asian sources tagged region=Asia",
        all(s.get("region") == "Asia" for s in asian),
    )

    # --- New sources are enabled --------------------------------------
    check(
        "all new Asian sources enabled",
        all(s.get("enabled") is True for s in asian),
    )

    # --- Every source has a valid type --------------------------------
    valid_types = {"rss", "worldbank_api", "imf_blog"}
    for source in SOURCES:
        check(
            f"{source['name']} type is valid",
            source.get("type") in valid_types,
        )

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} checks failed")
        for failure in FAILURES:
            print(f"  - {failure}")
        raise SystemExit(1)

    print(f"PASSED: all checks passed ({len(SOURCES)} sources)")


if __name__ == "__main__":
    main()
