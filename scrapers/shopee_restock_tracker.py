"""
Shopee Restock Tracker
Monitors a Shopee product and alerts when it comes back in stock.

Usage:
  python3 shopee_restock_tracker.py

To run every hour automatically (Linux/Mac):
  watch -n 3600 python3 shopee_restock_tracker.py

Note: Shopee protects its API with login sessions.
This tracker works by detecting changes in the page HTML
such as "Sold Out", stock numbers, and price data.
"""

from scrapling.fetchers import Fetcher
import json, os, re, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ── Config ──────────────────────────────────────────
PRODUCT_URL    = "https://shopee.ph/product/258376387/49059376697"
TARGET_VARIANT = "FMC Plus (DJI RC 2)"   # The specific variant to track
SAVE_FILE      = "shopee_restock_status.json"
HISTORY_FILE   = "shopee_restock_history.json"

# Email config
EMAIL_SENDER   = "sediboi390@gmail.com"
EMAIL_PASSWORD = "zsdwrlbrvjqjlthe"   # App password
EMAIL_RECEIVER = "sediboi390@gmail.com"
# ────────────────────────────────────────────────────

def check_stock():
    print(f"🛍️  Checking Shopee product...")
    print(f"🔗 {PRODUCT_URL}\n")

    page = Fetcher.get(
        PRODUCT_URL,
        stealthy_headers=True,
        follow_redirects=True
    )
    html = page.html_content

    # ── Extract product name ──
    name_match = re.search(r'"name"\s*:\s*"([^"]{3,120})"', html)
    name = name_match.group(1) if name_match else "Unknown Product"

    # ── Detect variant-specific stock ──
    # Look for the variant name near a stock/soldout indicator
    variant_section = re.search(
        rf'.{{0,500}}{re.escape(TARGET_VARIANT)}.{{0,500}}',
        html, re.IGNORECASE | re.DOTALL
    )

    if variant_section:
        vsec = variant_section.group(0)
        variant_sold_out = bool(re.search(r'sold.out|out.of.stock|"stock"\s*:\s*0', vsec, re.IGNORECASE))
        variant_in_stock = bool(re.search(r'"stock"\s*:\s*[1-9]\d*', vsec))
        variant_found = True
    else:
        # Variant name not in static HTML (JS rendered) — fall back to page-level check
        variant_sold_out = bool(re.search(r'soldout|sold.out|out.of.stock', html, re.IGNORECASE))
        variant_in_stock = bool(re.search(r'"stock"\s*:\s*[1-9]\d*', html))
        variant_found = False

    # ── Detect sold out indicators ──
    sold_out_signals = [
        variant_sold_out,
        '"stock":0' in html,
        '"stock": 0' in html,
    ]

    # ── Detect in-stock indicators ──
    in_stock_signals = [
        variant_in_stock,
        bool(re.search(r'add.to.cart|buy.now', html, re.IGNORECASE)),
    ]

    # ── Extract any price found ──
    price_raw = re.search(r'"price"\s*:\s*(\d{6,})', html)
    price = int(price_raw.group(1)) / 100000 if price_raw else 0

    price_min_raw = re.search(r'"price_min"\s*:\s*(\d{6,})', html)
    price_min = int(price_min_raw.group(1)) / 100000 if price_min_raw else price

    price_max_raw = re.search(r'"price_max"\s*:\s*(\d{6,})', html)
    price_max = int(price_max_raw.group(1)) / 100000 if price_max_raw else price

    # ── Extract stock number ──
    stock_raw = re.search(r'"stock"\s*:\s*([1-9]\d*)', html)
    stock = int(stock_raw.group(1)) if stock_raw else 0

    # ── Determine status ──
    if any(sold_out_signals):
        in_stock = False
    elif any(in_stock_signals):
        in_stock = True
    else:
        in_stock = None  # unknown

    return {
        'name':          name,
        'variant':       TARGET_VARIANT,
        'variant_found': variant_found,
        'stock':         stock,
        'price_min':     f"₱{price_min:,.2f}" if price_min > 0 else "See Shopee",
        'price_max':     f"₱{price_max:,.2f}" if price_max > 0 else "See Shopee",
        'in_stock':      in_stock,
        'url':           PRODUCT_URL,
        'checked_at':    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def save_and_compare(result):
    # Load previous status
    prev = None
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            prev = json.load(f)

    # Save current
    with open(SAVE_FILE, 'w') as f:
        json.dump(result, f, indent=2)

    # Append to history
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    history.append(result)
    if len(history) > 100:
        history = history[-100:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

    # Detect restock
    if prev and not prev.get('in_stock') and result.get('in_stock'):
        return 'RESTOCKED'
    elif prev and prev.get('in_stock') and not result.get('in_stock'):
        return 'OUT_OF_STOCK'
    elif not prev:
        return 'FIRST_CHECK'
    return 'NO_CHANGE'


def send_email_alert(product_name, variant, url):
    print("📧 Sending email alert...")
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 Shopee Restock Alert — {product_name} ({variant})"
        msg['From']    = EMAIL_SENDER
        msg['To']      = EMAIL_RECEIVER

        text = f"""
🚨 RESTOCK ALERT!

✅ {product_name} — {variant} is BACK IN STOCK on Shopee!

🛒 Buy now: {url}
🕐 Detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
Sent by your Shopee Restock Tracker 🤖
        """.strip()

        html = f"""
<html><body style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:20px">
  <div style="background:#ee4d2d;color:#fff;padding:20px;border-radius:10px;text-align:center">
    <h1>🚨 RESTOCK ALERT!</h1>
  </div>
  <div style="padding:20px;border:1px solid #eee;border-radius:10px;margin-top:16px">
    <h2 style="color:#ee4d2d">✅ Back in Stock!</h2>
    <p><strong>{product_name}</strong></p>
    <p>Variant: <strong style="color:#ee4d2d">{variant}</strong> is now available!</p>
    <a href="{url}" style="display:inline-block;background:#ee4d2d;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;margin-top:10px">
      🛒 Buy Now on Shopee
    </a>
    <p style="color:#888;font-size:12px;margin-top:20px">
      Detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
  </div>
</body></html>
        """.strip()

        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(f"✅ Email sent to {EMAIL_RECEIVER}!")
    except Exception as e:
        print(f"❌ Email failed: {e}")


def print_result(result, change):
    print("=" * 50)
    print(f"📦 Product : {result['name']}")
    print(f"🎨 Variant : {result['variant']}")
    if not result.get('variant_found'):
        print(f"   ⚠️  Variant not found in static HTML (JS-rendered)")
        print(f"   ℹ️  Tracking page-level stock as fallback")
    print(f"💰 Price   : {result['price_min']}", end="")
    if result.get('price_max') != result.get('price_min'):
        print(f" – {result['price_max']}")
    else:
        print()
    print(f"📊 Stock   : {result['stock']} units")
    print(f"✅ Status  : {'IN STOCK 🟢' if result['in_stock'] else 'OUT OF STOCK 🔴'}")
    print(f"🕐 Checked : {result['checked_at']}")
    print("=" * 50)

    if change == 'RESTOCKED':
        print("\n🚨🚨🚨 RESTOCK ALERT! 🚨🚨🚨")
        print(f"✅ '{result['name']}' is BACK IN STOCK!")
        print(f"🛒 Buy now: {result['url']}")
        send_email_alert(result['name'], result['variant'], result['url'])
    elif change == 'OUT_OF_STOCK':
        print("\n⚠️  Product just went OUT OF STOCK.")
    elif change == 'FIRST_CHECK':
        print("\n📝 First check recorded. Run again to track changes.")
    else:
        print("\n✅ No change since last check.")

    print(f"\n💾 Status saved to {SAVE_FILE}")
    print(f"📜 History saved to {HISTORY_FILE}")


if __name__ == '__main__':
    result = check_stock()
    if result:
        change = save_and_compare(result)
        print_result(result, change)
    else:
        print("❌ Could not retrieve product data.")
