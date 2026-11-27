import os
import json
import datetime
from google import genai
from google.genai import types
from google.oauth2 import service_account
from googleapiclient.discovery import build
import build_seo

MODELS_TO_TRY = [
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite"
]


def get_gsc_country_data():
    gsc_json_str = os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
    site_url = os.environ.get("SITE_URL")

    if not gsc_json_str or not site_url:
        print("GSC secrets not found; using fallback sample telemetry.")
        return [
            {"country": "USA", "clicks": 42, "impressions": 1150, "ctr": 0.036, "position": 14.2},
            {"country": "GBR", "clicks": 19, "impressions": 610, "ctr": 0.031, "position": 16.8},
            {"country": "DEU", "clicks": 11, "impressions": 420, "ctr": 0.026, "position": 18.5},
            {"country": "ARE", "clicks": 8, "impressions": 290, "ctr": 0.027, "position": 15.1}
        ]

    try:
        creds_info = json.loads(gsc_json_str)
        credentials = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        service = build("searchconsole", "v1", credentials=credentials)

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=28)

        request = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["country"],
            "rowLimit": 10
        }
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get("rows", [])

        if not rows:
            print(f"Connected to GSC for {site_url}, but 0 rows returned yet (awaiting indexing). Using baseline telemetry.")
            return [
                {"country": "USA", "clicks": 0, "impressions": 0, "ctr": 0.0, "position": 0.0},
                {"country": "GBR", "clicks": 0, "impressions": 0, "ctr": 0.0, "position": 0.0},
                {"country": "DEU", "clicks": 0, "impressions": 0, "ctr": 0.0, "position": 0.0},
                {"country": "ARE", "clicks": 0, "impressions": 0, "ctr": 0.0, "position": 0.0}
            ]

        telemetry = []
        for row in rows:
            telemetry.append({
                "country": row["keys"][0].upper(),
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0.0), 4),
                "position": round(row.get("position", 0.0), 1)
            })
        print(f"Successfully fetched {len(telemetry)} country rows from GSC for {site_url}.")
        return telemetry

    except Exception as e:
        print(f"GSC API Error ({e}); falling back to baseline telemetry.")
        return [
            {"country": "USA", "clicks": 0, "impressions": 0, "ctr": 0.0, "position": 0.0}
        ]


def run_optimization():
    with open("data.json", "r", encoding="utf-8") as f:
        current_data = json.load(f)

    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not set; skipping AI copy step and running static SEO build.")
        build_seo.build_all()
        return

    client = genai.Client()

    protected_products = {
        p["id"]: {
            "retail_usd": p["retail_usd"],
            "retail_url": p.get("retail_url"),
            "index_usd": p["index_usd"],
            "direct_usd": p.get("direct_usd"),
            "ebay_url": p["ebay_url"],
            "direct_url": p.get("direct_url"),
            "vibes": p.get("vibes", []),
            "image_url": p.get("image_url")
        }
        for p in current_data.get("products", [])
    }

    telemetry = get_gsc_country_data()
    today_str = datetime.date.today().isoformat()

    prompt = f"""
You are an autonomous SEO and geo-arbitrage optimization agent for PerfumeIndex, an online fragrance price comparison index.

Analyze the 28-day Google Search Console country performance telemetry and the current site configuration (`data.json`):

GSC Country Telemetry:
{json.dumps(telemetry, indent=2)}

Current data.json:
{json.dumps(current_data, indent=2)}

Your tasks:
1. Determine the highest-opportunity `default_country` code from the supported keys in `countries` (e.g., "US", "UK", "EU", "IL", "CA", "AU") based on clicks and impressions. If all clicks are 0, keep "US".
2. Refine `seo_title`, `seo_intro`, and `vat_note` inside each entry of `countries` to maximize organic search CTR and buyer trust for local shoppers comparing official retail prices against verified discounter/eBay prices.
3. Update `badge` labels on products (e.g., "Top Arbitrage Deal", "Best Seller", "High Savings") to highlight strong discounts, and refine `notes` if needed for clarity.
4. Set `last_optimized` to "{today_str}".

STRICT RULES:
- Return ONLY valid JSON matching the exact schema of `current_data`.
- Do NOT alter `base_url`, `id`, `brand`, `name`, `size`, `gender`, `vibes`, `image_url`, `retail_usd`, `retail_url`, `index_usd`, `direct_usd`, `ebay_url`, `direct_url`, `currency`, `symbol`, or `rate_to_usd`.
"""

    updated_data = None
    for model_name in MODELS_TO_TRY:
        try:
            print(f"Trying model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            updated_data = json.loads(response.text)
            print(f"Success with model: {model_name}")
            break
        except Exception as e:
            print(f"Skipping {model_name} ({e})")

    if not updated_data:
        print("All candidate Gemini models skipped; proceeding with existing data.json.")
        build_seo.build_all()
        return

    if current_data.get("base_url"):
        updated_data["base_url"] = current_data["base_url"]

    for product in updated_data.get("products", []):
        pid = product.get("id")
        if pid in protected_products:
            snap = protected_products[pid]
            product["retail_usd"] = snap["retail_usd"]
            if snap["retail_url"] is not None:
                product["retail_url"] = snap["retail_url"]
            product["index_usd"] = snap["index_usd"]
            if snap["direct_usd"] is not None:
                product["direct_usd"] = snap["direct_usd"]
            product["ebay_url"] = snap["ebay_url"]
            if snap["direct_url"] is not None:
                product["direct_url"] = snap["direct_url"]
            product["vibes"] = snap["vibes"]
            if snap["image_url"] is not None:
                product["image_url"] = snap["image_url"]

    updated_data["last_optimized"] = today_str

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)

    build_seo.build_all()
    print("PerfumeIndex optimization & programmatic SEO build completed successfully.")


if __name__ == "__main__":
    run_optimization()
