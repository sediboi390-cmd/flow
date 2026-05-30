"""
Shopee Restock Tracker — PythonAnywhere Compatible
Uses only: requests, smtplib, urllib (all built-in or pip installable)
NO Playwright, NO Scrapling, NO browser needed!

Install:  pip install requests --user
Run:      python3 shopee_restock_tracker.py
"""

import requests, json, os, re, smtplib, sys, subprocess, threading, urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ── Config ──────────────────────────────────────────
PRODUCT_URL    = "https://shopee.ph/product/258376387/49059376697"
TARGET_VARIANT = "FMC Plus (DJI RC 2)"
SAVE_FILE      = "shopee_restock_status.json"
HISTORY_FILE   = "shopee_restock_history.json"

# Email
EMAIL_SENDER   = "sediboi390@gmail.com"
EMAIL_PASSWORD = "zsdwrlbrvjqjlthe"
EMAIL_RECEIVER = "sediboi390@gmail.com"

# Pushbullet
PUSHBULLET_TOKEN = "o.agbesjAzlZdQFUVWmgS35YqPh9EHlotu"
# ────────────────────────────────────────────────────

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
}

def check_stock():
    print(f"🛍️  Checking Shopee product...")
    print(f"🔗 {PRODUCT_URL}\n")

    try:
        resp = requests.get(PRODUCT_URL, headers=HEADERS, timeout=15, allow_redirects=True)
        html = resp.text
        print(f"✅ Status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Failed to fetch page: {e}")
        return None

    # Extract product name
    name_match = re.search(r'"name"\s*:\s*"([^"]{3,120})"', html)
    name = name_match.group(1) if name_match else "6.6 Festive skin 2026"

    # Detect sold out
    sold_out = (
        bool(re.search(r'soldout|sold.out|out.of.stock', html, re.IGNORECASE)) or
        '"stock":0' in html or '"stock": 0' in html
    )

    # Detect in stock
    in_stock_signal = bool(re.search(r'"stock"\s*:\s*([1-9]\d*)', html))

    # Price
    price_raw = re.search(r'"price_min"\s*:\s*(\d{6,})', html)
    price = int(price_raw.group(1)) / 100000 if price_raw else 0

    # Stock count
    stock_raw = re.search(r'"stock"\s*:\s*([1-9]\d*)', html)
    stock = int(stock_raw.group(1)) if stock_raw else 0

    if sold_out:
        in_stock = False
    elif in_stock_signal:
        in_stock = True
    else:
        in_stock = None

    return {
        'name':       name,
        'variant':    TARGET_VARIANT,
        'stock':      stock,
        'price':      f"₱{price:,.2f}" if price > 0 else "See Shopee",
        'in_stock':   in_stock,
        'url':        PRODUCT_URL,
        'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def save_and_compare(result):
    prev = None
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            prev = json.load(f)

    with open(SAVE_FILE, 'w') as f:
        json.dump(result, f, indent=2)

    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    history.append(result)
    if len(history) > 100:
        history = history[-100:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

    if prev and not prev.get('in_stock') and result.get('in_stock'):
        return 'RESTOCKED'
    elif not prev:
        return 'FIRST_CHECK'
    return 'NO_CHANGE'


def send_pushbullet_alert(product_name, variant, url):
    print("📱 Sending Pushbullet notification...")
    try:
        resp = requests.post(
            'https://api.pushbullet.com/v2/pushes',
            headers={
                'Access-Token': PUSHBULLET_TOKEN,
                'Content-Type': 'application/json'
            },
            json={
                "type":  "link",
                "title": f"🚨 Shopee Restock! {product_name}",
                "body":  f"✅ {variant} is BACK IN STOCK!\nTap to buy now!",
                "url":   url
            },
            timeout=10
        )
        if resp.status_code == 200:
            print("✅ Pushbullet notification sent!")
        else:
            print(f"⚠️ Pushbullet error: {resp.status_code}")
    except Exception as e:
        print(f"❌ Pushbullet failed: {e}")


def send_email_alert(product_name, variant, url):
    print("📧 Sending email alert...")
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 Shopee Restock — {product_name} ({variant})"
        msg['From']    = EMAIL_SENDER
        msg['To']      = EMAIL_RECEIVER

        text = f"🚨 RESTOCK ALERT!\n\n✅ {product_name} — {variant} is BACK IN STOCK!\n\n🛒 {url}\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:20px">
  <div style="background:#ee4d2d;color:#fff;padding:20px;border-radius:10px;text-align:center"><h1>🚨 RESTOCK ALERT!</h1></div>
  <div style="padding:20px;border:1px solid #eee;border-radius:10px;margin-top:16px">
    <h2 style="color:#ee4d2d">✅ Back in Stock!</h2>
    <p><strong>{product_name}</strong><br>Variant: <strong style="color:#ee4d2d">{variant}</strong></p>
    <a href="{url}" style="display:inline-block;background:#ee4d2d;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;margin-top:10px">🛒 Buy Now on Shopee</a>
    <p style="color:#888;font-size:12px;margin-top:20px">Detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
  </div>
</body></html>"""

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
    print(f"💰 Price   : {result['price']}")
    print(f"📊 Stock   : {result['stock']} units")
    print(f"✅ Status  : {'IN STOCK 🟢' if result['in_stock'] else 'OUT OF STOCK 🔴'}")
    print(f"🕐 Checked : {result['checked_at']}")
    print("=" * 50)

    if change == 'RESTOCKED':
        print("\n🚨🚨🚨 RESTOCK ALERT! 🚨🚨🚨")
        print(f"✅ {result['name']} — {result['variant']} is BACK IN STOCK!")
        print(f"🛒 Buy now: {result['url']}")
        send_pushbullet_alert(result['name'], result['variant'], result['url'])
        send_email_alert(result['name'], result['variant'], result['url'])
    elif change == 'FIRST_CHECK':
        print("\n📝 First check recorded. Tracker is running!")
    else:
        print("\n✅ No change since last check.")

    print(f"\n💾 Saved to {SAVE_FILE}")


if __name__ == '__main__':
    result = check_stock()
    if result:
        change = save_and_compare(result)
        print_result(result, change)
    else:
        print("❌ Could not retrieve product data.")
