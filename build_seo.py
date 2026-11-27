import os
import re
import json
import html
import datetime

VIBE_META = {
    "feeling fresh": {
        "slug": "feeling-fresh",
        "gender": "Women",
        "title": "Best Fresh Women's Perfumes for Hot Weather (2026 Price Index)",
        "h1": "Feeling Fresh — Cooling Women's Perfumes for Hot Weather",
        "desc": "Compare official retail vs. verified discounter prices on crisp, cooling women's perfumes built for warm and hot weather.",
        "accent": "#38bdf8",
        "bg": "#07131a",
        "surface": "rgba(12, 29, 39, 0.9)",
        "guide": "Hot-weather women's fragrances rely on high-clarity citrus (yuzu, Sicilian orange, Calabrian bergamot) paired with airy florals like peony, magnolia, and white musk so the scent stays crisp and refreshing rather than heavy in high humidity."
    },
    "sexy nights": {
        "slug": "sexy-nights",
        "gender": "Women",
        "title": "Best Sexy Night Perfumes for Women — Date Night & Evening Price Index",
        "h1": "Sexy Nights — Magnetic Evening & Date-Night Perfumes for Women",
        "desc": "Compare official retail vs. verified deals on seductive, long-lasting women's evening perfumes with vanilla, amber, and white florals.",
        "accent": "#f97316",
        "bg": "#14080c",
        "surface": "rgba(31, 13, 19, 0.9)",
        "guide": "Evening and date-night women's fragrances anchor sweet gourmand notes (Madagascar vanilla, roasted tonka bean, cacao) with warm amber and tuberose for an intoxicating scent trail that projects in cool night air."
    },
    "9 to 5 energy": {
        "slug": "9-to-5-energy",
        "gender": "Women",
        "title": "Best All-Day Office & Everyday Perfumes for Women (9 to 5 Energy)",
        "h1": "9 to 5 Energy — All-Day Signature Perfumes for Women",
        "desc": "Compare official retail vs. verified deals on polished, long-lasting all-day women's fragrances that transition from desk to dinner.",
        "accent": "#10b981",
        "bg": "#071410",
        "surface": "rgba(12, 31, 25, 0.9)",
        "guide": "All-day signature scents balance clean citrus-floral openings with structured patchouli, lavender, and white musk bases so they project confidence for 8+ hours without overwhelming a boardroom."
    },
    "24/7 fresh": {
        "slug": "24-7-fresh",
        "gender": "Men",
        "title": "Best Daily Fresh Men's Colognes for Cool Weather (24/7 Fresh Index)",
        "h1": "24/7 Fresh — Versatile Daily Men's Fragrances",
        "desc": "Compare official retail vs. verified discounter prices on crisp, clean daily men's colognes with bergamot, mint, and cedarwood.",
        "accent": "#38bdf8",
        "bg": "#07121c",
        "surface": "rgba(12, 26, 41, 0.9)",
        "guide": "A true 24/7 daily men's fragrance combines sharp citrus-aromatic top notes (grapefruit, bergamot, mint) with dry woody ambroxan and cedar so it works effortlessly in cool mornings, at the gym, and at the office."
    },
    "main character": {
        "slug": "main-character",
        "gender": "Men",
        "title": "Best Bold Men's Perfumes for Day or Night (Main Character Index)",
        "h1": "Main Character — Bold Day-to-Night Perfumes for Men",
        "desc": "Compare official retail vs. verified deals on bold, compliment-getting men's fragrances engineered for standout projection day or night.",
        "accent": "#eab308",
        "bg": "#120f08",
        "surface": "rgba(28, 23, 13, 0.9)",
        "guide": "Main-character fragrances pair high-impact openings (pineapple, Sichuan pepper, spicy cardamom) with tenacious smoky birch, patchouli, and ambergris bases so your presence registers the moment you walk in."
    },
    "alpha male": {
        "slug": "alpha-male",
        "gender": "Men",
        "title": "Best Night & Clubbing Perfumes for Men (Alpha Male Price Index)",
        "h1": "Alpha Male — High-Projection Night Perfumes for Men",
        "desc": "Compare official retail vs. verified deals on dark, spicy, high-longevity men's night colognes built for after-hours dominance.",
        "accent": "#ef4444",
        "bg": "#140907",
        "surface": "rgba(31, 15, 12, 0.9)",
        "guide": "Built specifically for nights out and cold weather, these formulations push warm cinnamon, toffee, chestnut, saffron, and amberwood for 10+ hours of heavy sillage."
    }
}

BRAND_AUTH_GUIDES = {
    "Dior": "Check the bottom of the glass bottle and outer box for a 4-character alphanumeric batch code (e.g., 3A01) laser-etched into the glass—never printed on a removable sticker. The inside of the magnetic cap features the signature Dior bee emblem.",
    "Chanel": "Verify the 4-digit batch code laser-engraved on the back lower glass of the bottle (not just the box). Authentic Chanel atomizers sit flush with the collar and feature a crisp double-C logo on top of the magnetic cap.",
    "Yves Saint Laurent": "Locate the 6-character batch code (e.g., 38X401) etched near the bottom rear edge of the glass bottle and printed on the bottom of the cellophane-sealed carton. The metallic YSL Cassandre hardware wraps cleanly into the glass recesses.",
    "Versace": "Confirm the batch code stamped on the bottom of the box matches the code etched on the base of the bottle. Authentic Versace boxes include a reflective Medusa hologram seal and crisp embossed Greek-key borders.",
    "Giorgio Armani": "Check for the 6-character L'Oréal group batch code (e.g., 38W902) etched onto the bottom glass and stamped on the box base. The wrapped ring around the atomizer neck is solid metal with tight tolerances.",
    "Creed": "Inspect the bottom of the flacon for the etched lot number (starting with F or A on modern batches) matching the bottom of the box. Authentic Creed sprayers reveal a white plastic stem underneath when the atomizer head is lifted off.",
    "Maison Francis Kurkdjian": "Verify the 5-character batch code laser-engraved on the bottom of the glass flacon and box. On authentic Baccarat Rouge 540 bottles, the 'J' in Francis Kurkdjian features a distinctive curved hook and the gold neck collar has sharp chamfered edges.",
    "Carolina Herrera": "Check the batch code engraved on the base of the stiletto heel/bottle and the bottom of the velvet-textured box. The gold spray trigger mechanism moves smoothly without loose rattle.",
    "Calvin Klein": "Verify the 4-digit Coty batch code printed on the bottom of the box and etched onto the glass base, alongside clear regulatory text on the rear label."
}


def parse_ml(size_str):
    m = re.search(r"(\d+(?:\.\d+)?)\s*ml", size_str or "", re.I)
    return float(m.group(1)) if m else 100.0


def slugify_vibe(vibe_name):
    meta = VIBE_META.get(vibe_name.lower())
    if meta:
        return meta["slug"]
    return re.sub(r"[^a-z0-9]+", "-", vibe_name.lower()).strip("-")


def normalize_img_src(img_url, prefix=""):
    clean = (img_url or "").lstrip("./")
    return f"{prefix}{clean}"


def build_card_html(p, img_prefix=""):
    pid = html.escape(p["id"])
    brand = html.escape(p["brand"])
    name = html.escape(p["name"])
    size = html.escape(p["size"])
    gender = html.escape(p["gender"])
    notes = html.escape(p["notes"])
    badge = html.escape(p.get("badge") or "")
    vibes = p.get("vibes") or []
    img_src = html.escape(normalize_img_src(p.get("image_url", ""), img_prefix))

    has_direct = p.get("direct_url") and p["direct_url"] != "#direct-checkout-coming-soon" and p.get("direct_usd")
    best_price = min(p["index_usd"], p["direct_usd"]) if has_direct else p["index_usd"]
    discount_pct = round(((p["retail_usd"] - best_price) / p["retail_usd"]) * 100)

    sep = "&" if "?" in p["ebay_url"] else "?"
    ebay_url = html.escape(f"{p['ebay_url']}{sep}ref=perfumeindex_US_{p['id']}")
    retail_url = html.escape(p.get("retail_url") or "")

    retail_verify = (
        f'<a href="{retail_url}" target="_blank" rel="nofollow noopener" class="verify-link">Verify ↗</a>'
        if retail_url else ""
    )
    direct_btn = (
        f'<a href="{html.escape(p["direct_url"])}" target="_blank" rel="noopener" class="btn btn-direct">Direct ${p["direct_usd"]}</a>'
        if has_direct else ""
    )
    vibe_badges = ""
    if vibes:
        links = "".join(
            f'<a href="/vibe/{slugify_vibe(v)}.html" class="vibe-tag" style="text-decoration:none;">{html.escape(v)}</a>'
            for v in vibes
        )
        vibe_badges = f'<div class="vibe-tags">{links}</div>'

    badge_html = f'<span class="card-badge">{badge}</span>' if badge else ""

    return f"""
      <article class="card" data-gender="{gender}" data-vibe="{html.escape(','.join(vibes))}">
        <a href="/perfume/{pid}.html" class="stage-wrapper" style="text-decoration:none; color:inherit; display:block;" aria-label="View {brand} {name} price breakdown and authenticity guide">
          <div class="ivory-frame">
            <div class="gold-inner-border"></div>
            {badge_html}
            <span class="card-savings">Save {discount_pct}%</span>
            <img src="{img_src}" alt="{brand} {name} {size} bottle" class="bottle-img" loading="lazy" />
          </div>
        </a>
        <div class="card-body">
          <div>
            <div class="card-brand">{brand}</div>
            <h2 class="card-title"><a href="/perfume/{pid}.html" style="color:inherit; text-decoration:none;">{name}</a></h2>
            <div class="card-meta">{size} • {gender}</div>
            <div class="card-meta" style="margin-top:4px;">{notes}</div>
            {vibe_badges}
          </div>
          <div class="price-box">
            <div class="price-row">
              <span style="color:var(--muted);">Official Retail:</span>
              <div>
                <span class="retail-price">${p['retail_usd']}</span>
                {retail_verify}
              </div>
            </div>
            <div class="price-row">
              <span style="color:var(--muted);">Verified Deal:</span>
              <span class="index-price">${p['index_usd']}</span>
            </div>
          </div>
          <div class="card-actions">
            <a href="{ebay_url}" target="_blank" rel="noopener" class="btn btn-ebay">Buy on eBay (${p['index_usd']})</a>
            {direct_btn}
          </div>
        </div>
      </article>"""


def build_table_row_html(p):
    pid = html.escape(p["id"])
    brand = html.escape(p["brand"])
    name = html.escape(p["name"])
    size = html.escape(p["size"])
    gender = html.escape(p["gender"])
    notes = html.escape(p["notes"])
    img_src = html.escape(normalize_img_src(p.get("image_url", ""), "/"))
    sep = "&" if "?" in p["ebay_url"] else "?"
    ebay_url = html.escape(f"{p['ebay_url']}{sep}ref=perfumeindex_US_{p['id']}")
    retail_url = html.escape(p.get("retail_url") or "")
    retail_verify = (
        f'<a href="{retail_url}" target="_blank" rel="nofollow noopener" class="verify-link">Official ↗</a>'
        if retail_url else ""
    )
    return f"""
      <tr>
        <td><a href="/perfume/{pid}.html"><img src="{img_src}" alt="{name}" class="thumb-mini" /></a></td>
        <td>
          <div style="font-weight:700;"><a href="/perfume/{pid}.html" style="color:inherit; text-decoration:none;">{brand} — {name}</a></div>
          <div style="font-size:0.8rem; color:var(--muted);">{gender} • {notes}</div>
        </td>
        <td>{size}</td>
        <td><span class="retail-price">${p['retail_usd']}</span> {retail_verify}</td>
        <td><span class="index-price">${p['index_usd']}</span></td>
        <td>
          <div style="display:flex; gap:8px;">
            <a href="{ebay_url}" target="_blank" rel="noopener" class="btn btn-ebay">eBay (${p['index_usd']})</a>
          </div>
        </td>
      </tr>"""


def build_home_schema(data, base_url):
    items = []
    for idx, p in enumerate(data["products"], start=1):
        items.append({
            "@type": "ListItem",
            "position": idx,
            "url": f"{base_url}/perfume/{p['id']}.html",
            "name": f"{p['brand']} {p['name']} ({p['size']})",
            "item": {
                "@type": "Product",
                "name": f"{p['brand']} {p['name']} {p['size']}",
                "brand": {"@type": "Brand", "name": p["brand"]},
                "image": f"{base_url}/{p['image_url'].lstrip('./')}",
                "offers": {
                    "@type": "AggregateOffer",
                    "priceCurrency": "USD",
                    "lowPrice": str(p["index_usd"]),
                    "highPrice": str(p["retail_usd"]),
                    "offerCount": "2",
                    "availability": "https://schema.org/InStock"
                }
            }
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "PerfumeIndex Authentic Designer & Niche Fragrance Price Index",
        "numberOfItems": len(items),
        "itemListElement": items
    }
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def build_perfume_page(p, all_products, base_url, last_optimized):
    pid = p["id"]
    brand = html.escape(p["brand"])
    name = html.escape(p["name"])
    size = html.escape(p["size"])
    gender = html.escape(p["gender"])
    notes = html.escape(p["notes"])
    img_abs = f"{base_url}/{p['image_url'].lstrip('./')}"
    img_rel = f"/{p['image_url'].lstrip('./')}"
    page_url = f"{base_url}/perfume/{pid}.html"

    ml = parse_ml(p["size"])
    retail_per_ml = round(p["retail_usd"] / ml, 2)
    deal_per_ml = round(p["index_usd"] / ml, 2)
    savings_usd = p["retail_usd"] - p["index_usd"]
    discount_pct = round((savings_usd / p["retail_usd"]) * 100)

    sep = "&" if "?" in p["ebay_url"] else "?"
    ebay_url = html.escape(f"{p['ebay_url']}{sep}ref=perfumeindex_seo_{pid}")
    retail_url = html.escape(p.get("retail_url") or "")

    auth_tip = BRAND_AUTH_GUIDES.get(
        p["brand"],
        "Inspect the bottom of the glass flacon and outer cellophane-sealed carton to verify that the laser-etched batch code matches on both."
    )

    note_list = [n.strip() for n in p["notes"].split(",") if n.strip()]
    notes_pills = "".join(
        f'<span style="background:rgba(229,184,105,0.14); border:1px solid rgba(229,184,105,0.35); color:#e5b869; padding:5px 12px; border-radius:999px; font-size:0.85rem; font-weight:600;">{html.escape(n)}</span>'
        for n in note_list
    )

    vibe_links = "".join(
        f'<a href="/vibe/{slugify_vibe(v)}.html" style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.16); color:#faf8f5; padding:6px 14px; border-radius:999px; font-size:0.85rem; text-decoration:none; text-transform:lowercase;">{html.escape(v)} →</a>'
        for v in (p.get("vibes") or [])
    )

    related = [
        other for other in all_products
        if other["id"] != pid and (other["gender"] == p["gender"] or set(other.get("vibes", [])) & set(p.get("vibes", [])))
    ][:3]

    related_html = "".join(
        f'''<a href="/perfume/{html.escape(r['id'])}.html" style="background:#121216; border:1px solid #262630; border-radius:14px; padding:16px; text-decoration:none; color:#faf8f5; display:flex; align-items:center; gap:14px;">
          <img src="/{html.escape(r['image_url'].lstrip('./'))}" alt="{html.escape(r['name'])}" style="width:54px; height:64px; object-fit:contain; background:#faf8f5; border-radius:8px; padding:4px;" />
          <div>
            <div style="font-size:0.75rem; color:#e5b869; font-weight:700; text-transform:uppercase;">{html.escape(r['brand'])}</div>
            <div style="font-weight:700; font-size:0.98rem;">{html.escape(r['name'])}</div>
            <div style="font-size:0.82rem; color:#10b981; font-weight:700;">${r['index_usd']} <span style="color:#a1a1aa; text-decoration:line-through; font-weight:400;">${r['retail_usd']}</span></div>
          </div>
        </a>'''
        for r in related
    )

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": f"{p['gender']} Perfumes", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 3, "name": f"{p['brand']} {p['name']}", "item": page_url}
                ]
            },
            {
                "@type": "Product",
                "name": f"{p['brand']} {p['name']} ({p['size']})",
                "image": [img_abs],
                "description": f"Compare official retail (${p['retail_usd']}) vs. verified sealed discounter pricing (${p['index_usd']}) for {p['brand']} {p['name']} {p['size']}. Notes: {p['notes']}.",
                "brand": {"@type": "Brand", "name": p["brand"]},
                "category": f"{p['gender']}'s Fragrance",
                "offers": {
                    "@type": "AggregateOffer",
                    "url": page_url,
                    "priceCurrency": "USD",
                    "lowPrice": str(p["index_usd"]),
                    "highPrice": str(p["retail_usd"]),
                    "offerCount": "2",
                    "availability": "https://schema.org/InStock"
                }
            }
        ]
    }

    title_tag = f"{p['brand']} {p['name']} ({p['size']}) Price Index — Retail ${p['retail_usd']} vs. Verified ${p['index_usd']}"
    meta_desc = f"Save {discount_pct}% (${savings_usd} off) on 100% authentic, factory-sealed {p['brand']} {p['name']} {p['size']}. Compare official retail (${p['retail_usd']}) vs. verified deals (${p['index_usd']})."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title_tag)}</title>
  <meta name="description" content="{html.escape(meta_desc)}" />
  <link rel="canonical" href="{html.escape(page_url)}" />
  <meta property="og:title" content="{html.escape(title_tag)}" />
  <meta property="og:description" content="{html.escape(meta_desc)}" />
  <meta property="og:image" content="{html.escape(img_abs)}" />
  <meta property="og:url" content="{html.escape(page_url)}" />
  <meta property="og:type" content="product" />
  <script type="application/ld+json">
{json.dumps(schema, indent=2)}
  </script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif; background: #09090b; color: #faf8f5; line-height: 1.6; }}
    .container {{ max-width: 1040px; margin: 0 auto; padding: 0 20px; }}
    header {{ border-bottom: 1px solid #262630; padding: 16px 0; background: rgba(9,9,11,0.92); }}
    .nav {{ display: flex; justify-content: space-between; align-items: center; }}
    .brand {{ font-weight: 800; font-size: 1.3rem; color: #faf8f5; text-decoration: none; }}
    .brand span {{ color: #e5b869; }}
    .crumb {{ font-size: 0.84rem; color: #a1a1aa; margin: 20px 0; }}
    .crumb a {{ color: #e5b869; text-decoration: none; }}
    .hero-grid {{ display: grid; grid-template-columns: 1fr 1.2fr; gap: 32px; align-items: start; margin-bottom: 36px; }}
    @media (max-width: 768px) {{ .hero-grid {{ grid-template-columns: 1fr; }} }}
    .bottle-stage {{ background: radial-gradient(circle at 50% 42%, #ffffff 0%, #faf8f5 78%, #efeae1 100%); border-radius: 18px; padding: 34px; display: flex; align-items: center; justify-content: center; position: relative; border: 2px solid #e5b869; }}
    .bottle-stage img {{ max-height: 310px; max-width: 80%; object-fit: contain; mix-blend-mode: multiply; }}
    .save-pill {{ position: absolute; top: 14px; left: 14px; background: #10b981; color: #09090b; font-weight: 800; font-size: 0.8rem; padding: 4px 12px; border-radius: 999px; }}
    .panel {{ background: #121216; border: 1px solid #262630; border-radius: 16px; padding: 22px; margin-bottom: 20px; }}
    .price-compare {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin: 18px 0; }}
    .p-box {{ background: #09090b; border: 1px solid #262630; border-radius: 12px; padding: 14px; }}
    .cta-btn {{ display: block; width: 100%; text-align: center; background: #e5b869; color: #09090b; font-weight: 800; padding: 14px 20px; border-radius: 10px; text-decoration: none; font-size: 1rem; }}
    .cta-btn:hover {{ opacity: 0.9; }}
    .section-h2 {{ font-size: 1.25rem; font-weight: 800; margin-bottom: 10px; color: #e5b869; }}
    .related-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
    footer {{ border-top: 1px solid #262630; padding: 28px 0 40px; margin-top: 44px; color: #a1a1aa; font-size: 0.84rem; }}
  </style>
</head>
<body>
  <header>
    <div class="container nav">
      <a href="/" class="brand">Perfume<span>Index</span></a>
      <a href="/" style="color:#e5b869; font-size:0.88rem; font-weight:700; text-decoration:none;">← Full Price Index</a>
    </div>
  </header>

  <main class="container">
    <nav class="crumb" aria-label="Breadcrumb">
      <a href="/">Home</a> / <span>{gender}</span> / <span>{brand} {name}</span>
    </nav>

    <section class="hero-grid">
      <div class="bottle-stage">
        <span class="save-pill">Save {discount_pct}% (${savings_usd} Off)</span>
        <img src="{html.escape(img_rel)}" alt="{brand} {name} {size} authentic bottle" />
      </div>

      <div>
        <div style="color:#e5b869; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; font-size:0.84rem;">{brand}</div>
        <h1 style="font-size:clamp(1.7rem, 3.2vw, 2.35rem); font-weight:800; line-height:1.2; margin:4px 0 8px;">{name} ({size})</h1>
        <p style="color:#a1a1aa; font-size:0.95rem;">{gender} • Factory-Sealed Retail Box • Updated {html.escape(last_optimized)}</p>

        <div class="price-compare">
          <div class="p-box">
            <div style="font-size:0.78rem; color:#a1a1aa; text-transform:uppercase;">Official Retail MSRP</div>
            <div style="font-size:1.45rem; font-weight:700; color:#a1a1aa; text-decoration:line-through; margin-top:2px;">${p['retail_usd']}</div>
            <div style="font-size:0.8rem; color:#a1a1aa;">${retail_per_ml}/ml • <a href="{retail_url}" target="_blank" rel="nofollow noopener" style="color:#e5b869;">Verify MSRP ↗</a></div>
          </div>
          <div class="p-box" style="border-color:#10b981;">
            <div style="font-size:0.78rem; color:#10b981; text-transform:uppercase; font-weight:700;">PerfumeIndex Verified Deal</div>
            <div style="font-size:1.65rem; font-weight:800; color:#faf8f5; margin-top:2px;">${p['index_usd']}</div>
            <div style="font-size:0.8rem; color:#10b981;">${deal_per_ml}/ml (Save ${round(retail_per_ml - deal_per_ml, 2)}/ml)</div>
          </div>
        </div>

        <a href="{ebay_url}" target="_blank" rel="noopener" class="cta-btn">Check Verified Sealed Listings on eBay (${p['index_usd']}) ↗</a>
        <p style="font-size:0.8rem; color:#a1a1aa; margin-top:10px; text-align:center;">100% factory-sealed retail boxes backed by eBay Money Back Guarantee.</p>
      </div>
    </section>

    <section class="panel">
      <h2 class="section-h2">Key Fragrance Notes &amp; Scent Profile</h2>
      <p style="color:#d4d4d8; margin-bottom:14px;">{brand} {name} is built around the following primary aromatic accords:</p>
      <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px;">{notes_pills}</div>
      <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
        <span style="font-size:0.84rem; color:#a1a1aa;">Best matched vibes:</span>
        {vibe_links}
      </div>
    </section>

    <section class="panel">
      <h2 class="section-h2">How to Verify {brand} Authenticity &amp; Batch Codes</h2>
      <p style="color:#d4d4d8; margin-bottom:10px;">{html.escape(auth_tip)}</p>
      <p style="color:#a1a1aa; font-size:0.88rem;">Always avoid unsealed "tester" bottles without caps or listings shipped from unverified drop-ship locations with stock-only photos.</p>
    </section>

    <section style="margin-top:32px;">
      <h2 class="section-h2">Compare Similar Verified Fragrances</h2>
      <div class="related-grid">{related_html}</div>
    </section>
  </main>

  <footer>
    <div class="container">© 2026 PerfumeIndex. Independent Fragrance Price Index &amp; Authenticity Guide.</div>
  </footer>
  <script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "62a49852409e4a2faf39b4fe379b7759"}}'></script>
</body>
</html>"""


def build_vibe_page(vibe_name, meta, matching_products, base_url, last_optimized):
    slug = meta["slug"]
    page_url = f"{base_url}/vibe/{slug}.html"
    cards_html = "\n".join(build_card_html(p, img_prefix="/") for p in matching_products)

    other_vibes_html = "".join(
        f'<a href="/vibe/{m["slug"]}.html" style="padding:7px 14px; border-radius:999px; border:1px solid rgba(255,255,255,0.16); color:#faf8f5; text-decoration:none; font-size:0.84rem; text-transform:lowercase;">{html.escape(v)} ({m["gender"]})</a>'
        for v, m in VIBE_META.items() if v != vibe_name
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": meta["title"],
        "description": meta["desc"],
        "url": page_url,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(matching_products),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": idx,
                    "url": f"{base_url}/perfume/{p['id']}.html",
                    "name": f"{p['brand']} {p['name']} ({p['size']})"
                }
                for idx, p in enumerate(matching_products, start=1)
            ]
        }
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(meta['title'])}</title>
  <meta name="description" content="{html.escape(meta['desc'])}" />
  <link rel="canonical" href="{html.escape(page_url)}" />
  <script type="application/ld+json">
{json.dumps(schema, indent=2)}
  </script>
  <style>
    :root {{
      --bg: {meta['bg']};
      --surface: {meta['surface']};
      --border: rgba(255,255,255,0.14);
      --text: #faf8f5;
      --ivory: #faf8f5;
      --muted: #b4b4be;
      --accent: {meta['accent']};
      --accent-soft: rgba(255,255,255,0.08);
      --green: #10b981;
      --green-soft: rgba(16,185,129,0.16);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif; background: var(--bg); color: var(--text); line-height: 1.55; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    header {{ border-bottom: 1px solid var(--border); padding: 16px 0; background: rgba(9,9,11,0.85); }}
    .nav {{ display: flex; justify-content: space-between; align-items: center; }}
    .brand {{ font-weight: 800; font-size: 1.3rem; color: var(--text); text-decoration: none; }}
    .brand span {{ color: var(--accent); }}
    .hero {{ padding: 40px 0 24px; text-align: center; }}
    .pill {{ display: inline-block; background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent); padding: 4px 14px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; margin-bottom: 12px; }}
    .hero h1 {{ font-size: clamp(1.7rem, 3.6vw, 2.5rem); font-weight: 800; margin-bottom: 12px; }}
    .hero p {{ max-width: 720px; margin: 0 auto; color: #e4e4e7; }}
    .guide-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 18px 22px; margin: 0 auto 28px; max-width: 860px; font-size: 0.92rem; color: #d4d4d8; }}
    .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 28px; }}
    .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 18px; display: flex; flex-direction: column; overflow: hidden; }}
    .stage-wrapper {{ padding: 20px 20px 10px; }}
    .ivory-frame {{ position: relative; height: 260px; background: radial-gradient(circle at 50% 42%, #ffffff 0%, #faf8f5 78%, #efeae1 100%); border-radius: 14px; display: flex; align-items: center; justify-content: center; }}
    .gold-inner-border {{ position: absolute; inset: 12px; border: 1.5px solid var(--accent); border-radius: 8px; pointer-events: none; }}
    .bottle-img {{ max-height: 205px; max-width: 72%; object-fit: contain; mix-blend-mode: multiply; }}
    .card-badge {{ position: absolute; top: 10px; right: 10px; background: #09090b; color: var(--accent); border: 1px solid var(--accent); font-size: 0.7rem; font-weight: 700; padding: 3px 9px; border-radius: 999px; }}
    .card-savings {{ position: absolute; bottom: 10px; left: 10px; background: var(--green); color: #09090b; font-size: 0.72rem; font-weight: 800; padding: 3px 9px; border-radius: 999px; }}
    .card-body {{ padding: 16px 20px 20px; display: flex; flex-direction: column; flex: 1; gap: 12px; }}
    .card-brand {{ font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); font-weight: 700; }}
    .card-title {{ font-size: 1.14rem; font-weight: 800; }}
    .card-meta {{ font-size: 0.82rem; color: var(--muted); }}
    .vibe-tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }}
    .vibe-tag {{ font-size: 0.72rem; color: var(--accent); background: var(--accent-soft); border: 1px solid rgba(255,255,255,0.14); padding: 2px 8px; border-radius: 999px; }}
    .price-box {{ background: rgba(9,9,11,0.78); border: 1px solid var(--border); border-radius: 10px; padding: 12px; margin-top: auto; }}
    .price-row {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }}
    .price-row + .price-row {{ margin-top: 6px; padding-top: 6px; border-top: 1px dashed var(--border); }}
    .retail-price {{ color: var(--muted); text-decoration: line-through; }}
    .verify-link {{ font-size: 0.76rem; color: var(--accent); margin-left: 6px; }}
    .index-price {{ font-weight: 800; font-size: 1.15rem; }}
    .card-actions {{ display: flex; gap: 8px; }}
    .btn {{ flex: 1; display: inline-flex; align-items: center; justify-content: center; padding: 10px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; text-decoration: none; background: var(--accent); color: #09090b; }}
    footer {{ border-top: 1px solid var(--border); padding: 28px 0 40px; margin-top: 48px; color: var(--muted); font-size: 0.84rem; }}
  </style>
</head>
<body>
  <header>
    <div class="container nav">
      <a href="/" class="brand">Perfume<span>Index</span></a>
      <a href="/" style="color:var(--accent); font-size:0.88rem; font-weight:700; text-decoration:none;">← Interactive Vibe Finder</a>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <span class="pill">{html.escape(meta['gender'])} Vibe Collection • Updated {html.escape(last_optimized)}</span>
      <h1>{html.escape(meta['h1'])}</h1>
      <p>{html.escape(meta['desc'])}</p>
    </section>

    <div class="guide-box">
      <strong style="color:var(--accent);">Scent Profile Guide:</strong> {html.escape(meta['guide'])}
    </div>

    <section class="product-grid">
      {cards_html}
    </section>

    <section style="margin-top:40px; text-align:center;">
      <div style="font-size:0.86rem; color:var(--muted); margin-bottom:12px;">Explore other fragrance vibes:</div>
      <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:8px;">{other_vibes_html}</div>
    </section>
  </main>

  <footer>
    <div class="container">© 2026 PerfumeIndex. 100% Factory-Sealed Designer &amp; Niche Fragrances.</div>
  </footer>
  <script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "62a49852409e4a2faf39b4fe379b7759"}}'></script>
</body>
</html>"""


def build_all():
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    base_url = (os.environ.get("SITE_BASE_URL") or data.get("base_url") or "https://perfume-index.pages.dev").rstrip("/")
    last_optimized = data.get("last_optimized") or datetime.date.today().isoformat()
    products = data.get("products", [])

    os.makedirs("perfume", exist_ok=True)
    os.makedirs("vibe", exist_ok=True)

    # 1. Generate standalone product pages
    for p in products:
        page_html = build_perfume_page(p, products, base_url, last_optimized)
        with open(os.path.join("perfume", f"{p['id']}.html"), "w", encoding="utf-8") as f:
            f.write(page_html)

    # 2. Generate standalone vibe pages
    for vibe_name, meta in VIBE_META.items():
        matching = [
            p for p in products
            if vibe_name in [v.lower() for v in (p.get("vibes") or [])]
            and (p["gender"].lower() == meta["gender"].lower() or p["gender"].lower() == "unisex")
        ]
        vibe_html = build_vibe_page(vibe_name, meta, matching, base_url, last_optimized)
        with open(os.path.join("vibe", f"{meta['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(vibe_html)

    # 3. Pre-render index.html with static cards, table rows & JSON-LD schema
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            idx_html = f.read()

        ssr_cards = "\n".join(build_card_html(p, img_prefix="./") for p in products)
        ssr_rows = "\n".join(build_table_row_html(p) for p in products)
        ssr_schema = build_home_schema(data, base_url)

        idx_html = re.sub(
            r"<!-- SSR_SCHEMA_START -->.*?<!-- SSR_SCHEMA_END -->",
            f"<!-- SSR_SCHEMA_START -->\n  {ssr_schema}\n  <!-- SSR_SCHEMA_END -->",
            idx_html,
            flags=re.S
        )
        idx_html = re.sub(
            r"<!-- SSR_GRID_START -->.*?<!-- SSR_GRID_END -->",
            f"<!-- SSR_GRID_START -->\n{ssr_cards}\n    <!-- SSR_GRID_END -->",
            idx_html,
            flags=re.S
        )
        idx_html = re.sub(
            r"<!-- SSR_TABLE_START -->.*?<!-- SSR_TABLE_END -->",
            f"<!-- SSR_TABLE_START -->\n{ssr_rows}\n        <!-- SSR_TABLE_END -->",
            idx_html,
            flags=re.S
        )
        idx_html = re.sub(
            r'<link rel="canonical" href="[^"]*"\s*/?>',
            f'<link rel="canonical" href="{base_url}/" />',
            idx_html
        )

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(idx_html)

    # 4. Generate sitemap.xml & robots.txt
    urls = [
        (f"{base_url}/", "daily", "1.0")
    ]
    for meta in VIBE_META.values():
        urls.append((f"{base_url}/vibe/{meta['slug']}.html", "weekly", "0.85"))
    for p in products:
        urls.append((f"{base_url}/perfume/{p['id']}.html", "daily", "0.9"))

    url_entries = "\n".join(
        f"""  <url>
    <loc>{html.escape(loc)}</loc>
    <lastmod>{html.escape(last_optimized)}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>"""
        for loc, freq, prio in urls
    )

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_entries}
</urlset>
"""
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {base_url}/sitemap.xml
"""
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_txt)

    print(f"SEO build complete: {len(products)} product pages, {len(VIBE_META)} vibe pages, sitemap.xml & robots.txt updated.")


if __name__ == "__main__":
    build_all()
