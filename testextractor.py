from extractor import extract_article_text


url = (
    "https://www.federalreserve.gov/"
    "newsevents/pressreleases/"
    "monetary20260819a.htm"
)


text = extract_article_text(url)


print("\n========================================")
print("EXTRACTED ARTICLE TEXT")
print("========================================\n")


if text:

    print(text[:3000])

    print("\n========================================")
    print(f"Characters extracted: {len(text)}")

else:

    print("No article text could be extracted.")