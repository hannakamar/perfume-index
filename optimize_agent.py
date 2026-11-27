import os
import json
from datetime import datetime, timezone
from google import genai
from google.genai import types

# Optional: Google Search Console API integration
# Requires GSC_SERVICE_ACCOUNT_JSON and SITE_URL secrets in GitHub Actions
def fetch_country_traffic():
    gsc_creds = os.getenv("GSC_SERVICE_ACCOUNT_JSON")
    site_url = os.getenv("SITE_URL")

    if gsc_creds and site_url:
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            creds_dict = json.loads(gsc_creds)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
            )
            service = build("searchconsole", "v1", credentials=creds)

            request = {
                "startDate": "2026-11-01",
                "endDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "dimensions": ["country"],
                "rowLimit": 15
            }
            response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            rows = response.get("rows", [])
            return [
                {
                    "country_iso3": r["keys"][0],
                    "clicks": r["clicks"],
                    "impressions": r["impressions"],
                    "ctr": round(r["ctr"] * 100, 2)
                }
                for r in rows
            ]
        except Exception as e:
            print(f"GSC fetch warning: {e}")

    # Fallback sample telemetry until GSC collects its first 7 days of data
    return [
        {"country_iso3": "USA", "clicks": 42, "impressions": 1200, "ctr": 3.5},
        {"country_iso3": "GBR", "clicks": 28, "impressions": 640, "ctr": 4.38},
        {"country_iso3": "DEU", "clicks": 19, "impressions": 510, "ctr": 3.72},
        {"country_iso3": "ARE", "clicks": 14, "impressions": 300, "ctr": 4.67}
    ]

def run_optimizer():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable.")

    with open("data.json", "r", encoding="utf-8") as f:
        current_data = json.load(f)

    # Snapshot locked fields so the AI cannot alter prices or payment URLs
    locked_products = [
        {
            "id": p["id"],
            "retail_usd": p["retail_usd"],
            "index_usd": p["index_usd"],
            "direct_usd": p["direct_usd"],
            "ebay_url": p["ebay_url"],
            "direct_url": p["direct_url"],
        }
        for p in current_data["products"]
    ]

    traffic_stats = fetch_country_traffic()
    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are the autonomous SEO & conversion optimization agent for PerfumeIndex.
    Analyze the latest country-level search traffic and update `data.json` to maximize clicks and conversions from top-performing countries.

    TRAFFIC TELEMETRY BY COUNTRY:
    {json.dumps(traffic_stats, indent=2)}

    CURRENT SITE DATA:
    {json.dumps(current_data, indent=2)}

    STRICT RULES:
    1. Identify the top 3 countries by clicks and CTR. Set `default_country` to the #1 highest-performing country code (2-letter ISO code like US, GB, DE, AE, IL).
    2. For countries with rising clicks/impressions, refine their `seo_title` and `seo_intro` to include high-intent local search terms for "men perfume", "women perfume", and local price comparisons in that country's primary language.
    3. If a country in the traffic telemetry has strong impressions/clicks and is missing from `countries`, add it with accurate currency symbol, approximate USD exchange rate, local VAT note, and localized SEO copy.
    4. NEVER modify `retail_usd`, `index_usd`, `direct_usd`, `ebay_url`, or `direct_url` on any product. You may only refine `badge` or `notes` text for clarity.
    5. Update `last_optimized` to "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}" and append a concise summary of what you changed to `agent_metadata.optimization_log`.
    6. Return ONLY valid JSON matching the exact structure of `data.json`.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3
        )
    )

    updated_data = json.loads(response.text)

    # Enforce hard guardrail on prices & payment URLs
    locked_map = {item["id"]: item for item in locked_products}
    for prod in updated_data.get("products", []):
        if prod["id"] in locked_map:
            prod.update(locked_map[prod["id"]])

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)

    print("PerfumeIndex optimization completed successfully.")

if __name__ == "__main__":
    run_optimizer()
