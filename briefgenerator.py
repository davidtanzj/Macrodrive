import json
import os
import time

from google import genai
from google.genai import errors
from google.genai import types
from pydantic import BaseModel, Field

from trendengine import (
    analyze_trends,
    representative_articles,
)

from database import (
    create_database,
    save_daily_brief,
)


MODEL = "gemini-3.6-flash"


class BriefSection(BaseModel):
    title: str = Field(
        description="Short descriptive section heading."
    )
    text: str = Field(
        description="One concise paragraph grounded only in supplied evidence."
    )


class DailyBrief(BaseModel):
    headline: str = Field(
        description="One concise headline summarizing the day's dominant macro themes."
    )
    teaser: str = Field(
        description="A 40-60 word homepage teaser summarizing what matters today."
    )
    sections: list[BriefSection] = Field(
        description="Exactly three sections, one for each supplied trending topic."
    )
    what_to_watch: list[str] = Field(
        description="Two to four concise items to watch based only on supplied evidence."
    )


def build_evidence(report):
    evidence = {
        "lookback_hours": 24,
        "articles_analyzed": report["article_count"],
        "distinct_sources": report["source_count"],
        "top_regions": [
            {
                "name": region["name"],
                "articles": region["article_count"],
                "sources": region["source_count"],
                "trend_score": region["score"],
            }
            for region in report["regions"]
        ],
        "top_topics": [],
    }

    used_article_ids = set()
    now = report["generated_at"]

    for topic in report["topics"]:
        selected = representative_articles(
            topic,
            now,
            excluded_article_ids=used_article_ids,
        )

        used_article_ids.update(
            article["id"]
            for article in selected
        )

        evidence["top_topics"].append({
            "name": topic["name"],
            "articles": topic["article_count"],
            "sources": topic["source_count"],
            "trend_score": topic["score"],
            "representative_stories": [
                {
                    "source": article["source"],
                    "title": article["title"],
                    "description": article["description"][:500],
                }
                for article in selected
            ],
        })

    return evidence


def build_prompt(evidence):
    evidence_json = json.dumps(
        evidence,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
You are writing the MacroDrive Daily Brief, a concise global
macroeconomic and financial-markets briefing.

Use ONLY the evidence supplied below. Do not use outside knowledge.
Do not invent prices, market moves, causes, forecasts, quotations,
events, or facts that are not supported by the evidence.

The trend rankings were calculated by MacroDrive before this request.
Do not change which three topics are trending.

Writing requirements:
- Professional, neutral financial-news tone.
- Focus on why the supplied developments matter for macro and markets.
- Avoid sensationalism and unsupported causal claims.
- Distinguish reported developments from expectations.
- Do not mention that you are an AI.
- Do not cite or fabricate sources beyond the supplied source names.
- Headline: concise, informative, no clickbait.
- Teaser: 35-45 words and useful when shown by itself.
- Do not intensify language beyond the evidence. Words such as "surge",
  "plunge", "soar", "collapse", "sharp" or "dramatic" may only be used
  when the supplied headline or description explicitly supports them.
- Sections: exactly 3, corresponding in order to the 3 trending topics.
- Each section: roughly 80-120 words.
- what_to_watch: 2-4 short items. These must come from the supplied
  evidence. If the evidence does not support a forward-looking event,
  phrase the item as a development/theme to monitor rather than
  inventing an economic-calendar event.

MACRODRIVE EVIDENCE:
{evidence_json}
""".strip()


def generate_brief():
    api_key = os.environ.get(
        "GEMINI_API_KEY",
        "",
    ).strip()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set."
        )

    report = analyze_trends()

    if len(report["topics"]) < 3:
        raise RuntimeError(
            "Not enough trend data to generate a daily brief."
        )

    evidence = build_evidence(report)
    prompt = build_prompt(evidence)

    client = genai.Client(
        api_key=api_key
    )

    retry_delays = [0, 20, 60]

    response = None

    for attempt, delay in enumerate(
        retry_delays,
        start=1
    ):
        if delay:
            print(
                f"Gemini temporarily unavailable. "
                f"Waiting {delay} seconds before "
                f"attempt {attempt}...",
                flush=True,
            )
            time.sleep(delay)

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DailyBrief,
                    temperature=0.2,
                    max_output_tokens=4096,
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=512
                    )
                ),
            )
            break

        except (errors.ClientError, errors.ServerError) as error:
            status_code = getattr(
                error,
                "code",
                None,
            )

            if status_code is None:
                status_code = getattr(
                    error,
                    "status_code",
                    None,
                )

            retryable = (
                status_code in (429, 500, 502, 503, 504)
                or "503" in str(error)
                or "429" in str(error)
            )

            if (
                not retryable
                or attempt == len(retry_delays)
            ):
                raise

            print(
                f"Gemini request attempt {attempt} "
                f"failed temporarily: {error}",
                flush=True,
            )

    if response is None:
        raise RuntimeError(
            "Gemini did not return a response."
        )

    if response.parsed is not None:
        result = response.parsed
    else:
        result = DailyBrief.model_validate_json(
            response.text
        )

    return result, evidence


def save_generated_brief():
    create_database()

    result, evidence = generate_brief()

    generated_at = (
        __import__("datetime")
        .datetime.now(
            __import__("datetime").timezone.utc
        )
    )

    payload = {
        "brief_date": generated_at.date().isoformat(),
        "headline": result.headline,
        "teaser": result.teaser,
        "sections": [
            {
                "title": section.title,
                "text": section.text,
            }
            for section in result.sections
        ],
        "what_to_watch": list(result.what_to_watch),
        "trending_topics": [
            topic["name"]
            for topic in evidence["top_topics"]
        ],
        "trending_regions": [
            region["name"]
            for region in evidence["top_regions"]
        ],
        "articles_analyzed": evidence["articles_analyzed"],
        "sources_analyzed": evidence["distinct_sources"],
        "generated_at": generated_at.isoformat(),
    }

    save_daily_brief(payload)

    print(
        f"Saved MacroDrive Daily Brief for "
        f"{payload['brief_date']}",
        flush=True,
    )

    print()
    print(payload["headline"])
    print(payload["teaser"])


def print_brief():
    result, evidence = generate_brief()

    print()
    print("=" * 72)
    print("MACRODRIVE GEMINI DAILY BRIEF — TEST")
    print("=" * 72)
    print()
    print(result.headline)
    print()
    print("TEASER")
    print("-" * 72)
    print(result.teaser)

    for section in result.sections:
        print()
        print(section.title.upper())
        print("-" * 72)
        print(section.text)

    print()
    print("WHAT TO WATCH")
    print("-" * 72)

    for item in result.what_to_watch:
        print(f"- {item}")

    print()
    print("INPUT SUMMARY")
    print("-" * 72)
    print(
        f"Articles analysed: "
        f"{evidence['articles_analyzed']}"
    )
    print(
        f"Distinct sources: "
        f"{evidence['distinct_sources']}"
    )
    print(
        "Trending topics: "
        + ", ".join(
            topic["name"]
            for topic in evidence["top_topics"]
        )
    )
    print("=" * 72)


if __name__ == "__main__":
    import sys

    if "--save" in sys.argv:
        save_generated_brief()
    else:
        print_brief()
