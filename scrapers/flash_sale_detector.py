"""
Flash Sale Detector — Shopee & Lazada
Monitors product prices and alerts when a significant price drop is detected.

Install:  pip install requests --user
Run:      python3 flash_sale_detector.py
"""

import requests, json, os, re, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ── Config ──────────────────────────────────────────
SALE_THRESHOLD = 10  # Alert when price drops by this % or more

# Email
EMAIL_SENDER   = "sediboi390@gmail.com"
EMAIL_PASSWORD = "zsdwrlbrvjqjlthe"
EMAIL_RECEIVER = "sediboi390@gmail.com"

# Pushbullet
PUSHBULLET_TOKEN = "o.agbesjAzlZdQFUVWmgS35YqPh9EHlotu"

SAVE_FILE    = "flash_sale_status.json"
HISTORY_FILE = "flash_sale_history.json"

# ── Products to track ─────────────────────────────
# Add as many products as you want!
# Format: { 'name': ..., 'url': ..., 'platform': 'shopee' or 'lazada' }
PRODUCTS = [
    # Add your Shopee products here
    # {
    #     'name': 'DJI RC 2',
    #     'url': 'https://shopee.ph/product/258376387/49059376697',
    #     'platform': 'shopee'
    # },

    # Add your Lazada products here
    # {
    #     'name': 'DJI RC 2',
    #     'url': 'https://www.lazada.com.ph/products/...',
    #     'platform': 'lazada'
    # },
]
# ────────────────────────────────────────────────────

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
}


def get_shopee_price(url):
    """Scrape price from Shopee product page"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        html = resp.text

        # Extract prices
        price_min = re.search(r'"price_min"\s*:\s*(\d{6,})', html)
        price_max = re.search(r'"price_max"\s*:\s*(\d{6,})', html)
        price     = re.search(r'"price"\s*:\s*(\d{6,})', html)

        if price_min:
            return int(price_min.group(1)) / 100000
        elif price:
            return int(price.group(1)) / 100000

        # Try finding price in HTML text
        price_text = re.search(r'₱\s*([\d,]+(?:\.\d+)?)', html)
        if price_text:
            return float(price_text.group(1).replace(',', ''))

    except Exception as e:
        print(f"  ⚠️  Shopee fetch error: {e}")
    return None


def get_lazada_price(url):
    """Scrape price from Lazada product page"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        html = resp.text

        # Try JSON data
        price_match = re.search(r'"price"\s*:\s*"?([\d.]+)"?', html)
        if price_match:
            return float(price_match.group(1))

        # Try original price
        orig = re.search(r'"originalPrice"\s*:\s*"?([\d.]+)"?', html)
        if orig:
            return float(orig.group(1))

        # Try HTML price text
        price_text = re.search(r'₱\s*([\d,]+(?:\.\d+)?)', html)
        if price_text:
            return float(price_text.group(1).replace(',', ''))

    except Exception as e:
        print(f"  ⚠️  Lazada fetch error: {e}")
    return None


def check_prices():
    results = []

    for product in PRODUCTS:
        name     = product['name']
        url      = product['url']
        platform = product['platform'].lower()

        print(f"\n🔍 Checking: {name} ({platform.capitalize()})")
        print(f"   🔗 {url}")

        price = None
        if platform == 'shopee':
            price = get_shopee_price(url)
        elif platform == 'lazada':
            price = get_lazada_price(url)

        if price:
            print(f"   💰 Current price: ₱{price:,.2f}")
        else:
            print(f"   ⚠️  Could not fetch price")

        results.append({
            'name':       name,
            'url':        url,
            'platform':   platform,
            'price':      price,
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return results


def load_previous():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE) as f:
        data = json.load(f)
    return {p['url']: p for p in data}


def save_results(results):
    with open(SAVE_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    history.append({'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'results': results})
    if len(history) > 200:
        history = history[-200:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def detect_sales(results, previous):
    sales = []
    for r in results:
        if not r['price']:
            continue
        prev = previous.get(r['url'])
        if not prev or not prev.get('price'):
            continue
        old_price = prev['price']
        new_price = r['price']
        drop_pct  = ((old_price - new_price) / old_price) * 100

        if drop_pct >= SALE_THRESHOLD:
            sales.append({
                **r,
                'old_price': old_price,
                'new_price': new_price,
                'drop_pct':  round(drop_pct, 1),
                'savings':   round(old_price - new_price, 2)
            })
    return sales


def send_pushbullet(title, body, url):
    try:
        requests.post(
            'https://api.pushbullet.com/v2/pushes',
            headers={'Access-Token': PUSHBULLET_TOKEN, 'Content-Type': 'application/json'},
            json={'type': 'link', 'title': title, 'body': body, 'url': url},
            timeout=10
        )
        print("   📱 Pushbullet sent!")
    except Exception as e:
        print(f"   ❌ Pushbullet failed: {e}")


def send_email(sales):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔥 Flash Sale Alert! {len(sales)} deal(s) found!"
        msg['From']    = EMAIL_SENDER
        msg['To']      = EMAIL_RECEIVER

        body = "\n\n".join([
            f"🔥 {s['name']} ({s['platform'].capitalize()})\n"
            f"   Was:    ₱{s['old_price']:,.2f}\n"
            f"   Now:    ₱{s['new_price']:,.2f}\n"
            f"   Save:   ₱{s['savings']:,.2f} ({s['drop_pct']}% off!)\n"
            f"   Link:   {s['url']}"
            for s in sales
        ])

        html_items = "".join([f"""
        <div style="border:1px solid #eee;border-radius:10px;padding:16px;margin-bottom:12px">
            <h3 style="color:#f57224;margin:0">{s['name']} — {s['platform'].capitalize()}</h3>
            <p style="margin:8px 0"><del style="color:#888">₱{s['old_price']:,.2f}</del>
            → <strong style="color:#f57224;font-size:1.2em">₱{s['new_price']:,.2f}</strong></p>
            <p style="color:#2a9d6b;font-weight:600">Save ₱{s['savings']:,.2f} ({s['drop_pct']}% OFF!)</p>
            <a href="{s['url']}" style="display:inline-block;background:#f57224;color:#fff;padding:8px 18px;border-radius:8px;text-decoration:none;font-weight:bold">🛒 Buy Now</a>
        </div>""" for s in sales])

        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:560px;margin:auto;padding:20px">
  <div style="background:#f57224;color:#fff;padding:20px;border-radius:10px;text-align:center">
    <h1>🔥 Flash Sale Alert!</h1>
    <p>{len(sales)} deal(s) detected!</p>
  </div>
  <div style="margin-top:16px">{html_items}</div>
  <p style="color:#888;font-size:12px;text-align:center">Detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body></html>"""

        msg.attach(MIMEText(body, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(EMAIL_SENDER, EMAIL_PASSWORD)
            s.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("   📧 Email sent!")
    except Exception as e:
        print(f"   ❌ Email failed: {e}")


def main():
    print("🔥 Flash Sale Detector — Shopee & Lazada")
    print(f"⚡ Alert threshold: {SALE_THRESHOLD}% price drop")
    print(f"📦 Tracking {len(PRODUCTS)} product(s)\n")

    if not PRODUCTS:
        print("⚠️  No products configured yet!")
        print("📝 Add your products to the PRODUCTS list in this script.")
        print("\nExample:")
        print("  {'name': 'DJI RC 2', 'url': 'https://shopee.ph/product/...', 'platform': 'shopee'}")
        return

    previous = load_previous()
    results  = check_prices()
    sales    = detect_sales(results, previous)

    save_results(results)

    print(f"\n{'='*50}")
    if sales:
        print(f"🔥 {len(sales)} FLASH SALE(S) DETECTED!\n")
        for s in sales:
            print(f"  🎯 {s['name']} ({s['platform'].capitalize()})")
            print(f"     Was:  ₱{s['old_price']:,.2f}")
            print(f"     Now:  ₱{s['new_price']:,.2f}")
            print(f"     Save: ₱{s['savings']:,.2f} ({s['drop_pct']}% OFF!)")
            print(f"     🛒 {s['url']}\n")
            send_pushbullet(
                f"🔥 Flash Sale! {s['name']} {s['drop_pct']}% OFF!",
                f"Was ₱{s['old_price']:,.2f} → Now ₱{s['new_price']:,.2f} (Save ₱{s['savings']:,.2f})",
                s['url']
            )
        send_email(sales)
    else:
        print("✅ No flash sales detected.")
        print(f"   Checked {len(results)} product(s)")

    print(f"\n💾 Saved to {SAVE_FILE}")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
