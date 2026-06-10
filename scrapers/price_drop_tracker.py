"""
Price Drop Alert Tracker — Shopee & Lazada
Monitors products and alerts when price drops to/below your target.

Install:  pip install requests --user
Run:      python price_drop_tracker.py
"""

import requests, json, os, re, smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ── Config ──────────────────────────────────────────
WATCHLIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "price_watchlist.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "price_history.json")

# Email
EMAIL_SENDER = "sediboi390@gmail.com"
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


MAX_PRODUCTS = 5


def validate_product(product):
    """Validate a product entry. Returns (is_valid, error_message)."""
    name = product.get('name', '')
    url = product.get('url', '')
    store = product.get('store', '')
    enabled = product.get('enabled')

    if not name or not isinstance(name, str) or not name.strip():
        return False, "name is empty or missing"
    if not url or not isinstance(url, str):
        return False, "url is empty or missing"
    if 'shopee' not in url.lower() and 'lazada' not in url.lower():
        return False, "url must contain 'shopee' or 'lazada'"
    if store not in ('shopee', 'lazada'):
        return False, f"store must be 'shopee' or 'lazada', got '{store}'"
    if not isinstance(enabled, bool):
        return False, "enabled must be true or false"

    # Must have either target_price OR variants (or both for backward compat)
    has_target = isinstance(product.get('target_price'), (int, float)) and product.get('target_price', 0) > 0
    has_variants = isinstance(product.get('variants'), list) and len(product.get('variants', [])) > 0

    if not has_target and not has_variants:
        return False, "must have target_price (number > 0) or variants (non-empty list)"

    # Validate variants if present
    if has_variants:
        for i, v in enumerate(product['variants']):
            if not isinstance(v, dict):
                return False, f"variant #{i+1} must be an object"
            if not v.get('name'):
                return False, f"variant #{i+1} missing name"
            if not isinstance(v.get('target_price'), (int, float)) or v['target_price'] <= 0:
                return False, f"variant #{i+1} '{v.get('name')}' has invalid target_price"

    return True, ""


def load_watchlist():
    """Load watchlist from JSON file."""
    if not os.path.exists(WATCHLIST_FILE):
        # Create default watchlist
        default = {
            "products": [
                {
                    "name": "Example Product",
                    "url": "https://shopee.ph/product/123/456",
                    "target_price": 5000,
                    "store": "shopee",
                    "enabled": False
                }
            ]
        }
        with open(WATCHLIST_FILE, 'w') as f:
            json.dump(default, f, indent=2)
        print(f"📝 Created watchlist at: {WATCHLIST_FILE}")
        print("   Edit it to add your products!")
        return default
    
    with open(WATCHLIST_FILE) as f:
        data = json.load(f)

    # Validate and warn about invalid products
    products = data.get('products', [])
    valid_products = []
    for i, p in enumerate(products):
        is_valid, err = validate_product(p)
        if is_valid:
            valid_products.append(p)
        else:
            print(f"⚠️  Product #{i+1} '{p.get('name', '?')}' skipped: {err}")

    # Enforce max products limit
    if len(valid_products) > MAX_PRODUCTS:
        print(f"⚠️  Watchlist has {len(valid_products)} products, max is {MAX_PRODUCTS}. Only first {MAX_PRODUCTS} will be checked.")
        valid_products = valid_products[:MAX_PRODUCTS]

    data['products'] = valid_products
    return data


def load_history():
    """Load price history."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}


def save_history(history):
    """Save price history."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def detect_store(url):
    """Detect if URL is Shopee or Lazada."""
    if 'shopee' in url.lower():
        return 'shopee'
    elif 'lazada' in url.lower():
        return 'lazada'
    return 'unknown'


def fetch_shopee_price(url):
    """Fetch current price and variant prices from Shopee."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        html = resp.text

        # Extract product name
        name_match = re.search(r'"name"\s*:\s*"([^"]{3,120})"', html)
        name = name_match.group(1) if name_match else None

        # Extract overall price (Shopee stores price in cents)
        price_match = re.search(r'"price_min"\s*:\s*(\d{6,})', html)
        if price_match:
            price = int(price_match.group(1)) / 100000
        else:
            price_match2 = re.search(r'"price"\s*:\s*(\d{6,})', html)
            if price_match2:
                price = int(price_match2.group(1)) / 100000
            else:
                price = None

        # Discount/sale detection
        discount_match = re.search(r'"raw_discount"\s*:\s*(\d+)', html)
        discount = int(discount_match.group(1)) if discount_match else 0

        # Extract variant prices from "models" array
        variants = {}
        # Pattern: "models":[{"name":"Variant Name","price":12345600000,...},...]
        models_match = re.search(r'"models"\s*:\s*\[([^\]]+)\]', html)
        if models_match:
            models_str = models_match.group(1)
            # Extract each model's name and price
            model_entries = re.findall(
                r'"name"\s*:\s*"([^"]+)"[^}]*?"price"\s*:\s*(\d{6,})',
                models_str
            )
            for vname, vprice in model_entries:
                variants[vname] = int(vprice) / 100000

            # Also try reverse order (price before name)
            if not variants:
                model_entries2 = re.findall(
                    r'"price"\s*:\s*(\d{6,})[^}]*?"name"\s*:\s*"([^"]+)"',
                    models_str
                )
                for vprice, vname in model_entries2:
                    variants[vname] = int(vprice) / 100000

        return {
            'name': name,
            'price': price,
            'discount': discount,
            'variants': variants,
            'status': 'ok'
        }
    except Exception as e:
        return {'name': None, 'price': None, 'discount': 0, 'variants': {}, 'status': f'error: {e}'}


def fetch_lazada_price(url):
    """Fetch current price and variant prices from Lazada."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        html = resp.text

        # Extract product name
        name_match = re.search(r'"name"\s*:\s*"([^"]{3,200})"', html)
        if not name_match:
            name_match = re.search(r'<title>([^<]+)</title>', html)
        name = name_match.group(1) if name_match else None

        # Extract price - Lazada uses different patterns
        price = None
        
        # Pattern 1: priceCurrency and price
        price_match = re.search(r'"price"\s*:\s*"?(\d+\.?\d*)"?', html)
        if price_match:
            price = float(price_match.group(1))
        
        # Pattern 2: salePrice
        if not price:
            sale_match = re.search(r'"salePrice"\s*:\s*"?(\d+\.?\d*)"?', html)
            if sale_match:
                price = float(sale_match.group(1))

        # Pattern 3: price in structured data
        if not price:
            price_match3 = re.search(r'₱\s*([\d,]+\.?\d*)', html)
            if price_match3:
                price = float(price_match3.group(1).replace(',', ''))

        # Discount detection
        discount_match = re.search(r'-(\d+)%', html)
        discount = int(discount_match.group(1)) if discount_match else 0

        # Extract variant prices from skuInfos or skuBase
        variants = {}
        sku_entries = re.findall(
            r'"name"\s*:\s*"([^"]+)"[^}]*?"price"\s*:\s*"?(\d+\.?\d*)"?',
            html
        )
        for vname, vprice in sku_entries:
            try:
                v_price = float(vprice)
                if 100 < v_price < 1000000:  # Reasonable price range in PHP
                    variants[vname] = v_price
            except ValueError:
                pass

        return {
            'name': name,
            'price': price,
            'discount': discount,
            'variants': variants,
            'status': 'ok'
        }
    except Exception as e:
        return {'name': None, 'price': None, 'discount': 0, 'variants': {}, 'status': f'error: {e}'}


def check_price(product):
    """Check price for a single product."""
    url = product['url']
    store = product.get('store') or detect_store(url)

    if store == 'shopee':
        return fetch_shopee_price(url)
    elif store == 'lazada':
        return fetch_lazada_price(url)
    else:
        return {'name': None, 'price': None, 'discount': 0, 'status': 'unknown store'}


def send_pushbullet_alert(product_name, current_price, target_price, url, discount):
    """Send Pushbullet notification for price drop."""
    print("  📱 Sending Pushbullet alert...")
    try:
        body = f"💰 ₱{current_price:,.2f} (target was ₱{target_price:,.2f})"
        if discount > 0:
            body += f"\n🏷️ {discount}% OFF!"
        body += "\nTap to buy now!"

        resp = requests.post(
            'https://api.pushbullet.com/v2/pushes',
            headers={
                'Access-Token': PUSHBULLET_TOKEN,
                'Content-Type': 'application/json'
            },
            json={
                "type": "link",
                "title": f"🚨 Price Drop! {product_name}",
                "body": body,
                "url": url
            },
            timeout=10
        )
        if resp.status_code == 200:
            print("  ✅ Pushbullet sent!")
        else:
            print(f"  ⚠️ Pushbullet error: {resp.status_code}")
    except Exception as e:
        print(f"  ❌ Pushbullet failed: {e}")


def send_email_alert(product_name, current_price, target_price, url, discount, store):
    """Send email alert for price drop."""
    print("  📧 Sending email alert...")
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 Price Drop! {product_name} — ₱{current_price:,.2f}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        discount_text = f" ({discount}% OFF!)" if discount > 0 else ""
        savings = target_price - current_price

        text = f"""🚨 PRICE DROP ALERT!

📦 {product_name}
💰 Current Price: ₱{current_price:,.2f}{discount_text}
🎯 Your Target: ₱{target_price:,.2f}
💵 You Save: ₱{savings:,.2f}
🏪 Store: {store.title()}

🛒 Buy now: {url}

⏰ Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:20px">
  <div style="background:linear-gradient(135deg,#ff6b35,#f7c948);color:#fff;padding:20px;border-radius:12px;text-align:center">
    <h1 style="margin:0">🚨 PRICE DROP!</h1>
  </div>
  <div style="padding:20px;border:1px solid #eee;border-radius:12px;margin-top:16px">
    <h2 style="color:#333;margin-top:0">{product_name}</h2>
    <div style="background:#f0fff0;border:2px solid #2a9d6b;border-radius:8px;padding:16px;margin:12px 0">
      <p style="margin:0;font-size:1.5rem;font-weight:bold;color:#2a9d6b">₱{current_price:,.2f}</p>
      <p style="margin:4px 0 0;color:#666">Target: ₱{target_price:,.2f} • You save ₱{savings:,.2f}{discount_text}</p>
    </div>
    <p style="color:#666">🏪 Store: <strong>{store.title()}</strong></p>
    <a href="{url}" style="display:inline-block;background:#ff6b35;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:bold;margin-top:10px;font-size:1.1rem">🛒 Buy Now</a>
    <p style="color:#999;font-size:12px;margin-top:20px">Detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
  </div>
</body></html>"""

        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("  ✅ Email sent!")
    except Exception as e:
        print(f"  ❌ Email failed: {e}")


def run_tracker():
    """Main tracking loop — checks all products once, with variant support."""
    print("=" * 55)
    print("💰 Price Drop Tracker — Shopee & Lazada")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    watchlist = load_watchlist()
    history = load_history()
    products = watchlist.get('products', [])

    enabled_products = [p for p in products if p.get('enabled', True)]

    if not enabled_products:
        print("\n⚠️  No enabled products in watchlist!")
        print(f"   Edit: {WATCHLIST_FILE}")
        return

    print(f"\n📋 Checking {len(enabled_products)} product(s)...\n")

    alerts_sent = 0

    for i, product in enumerate(enabled_products, 1):
        name = product.get('name', 'Unknown')
        url = product['url']
        store = product.get('store') or detect_store(url)
        variants = product.get('variants', [])
        # Backward compat: if no variants, use top-level target_price
        has_variants = isinstance(variants, list) and len(variants) > 0

        print(f"[{i}/{len(enabled_products)}] {name}")
        print(f"    🏪 {store.title()}")

        if has_variants:
            print(f"    📦 Tracking {len(variants)} variant(s)")
        else:
            target = product.get('target_price', 0)
            print(f"    🎯 Target: ₱{target:,.2f}")

        result = check_price(product)

        if result['status'] != 'ok':
            print(f"    ❌ Could not fetch page ({result['status']})")
            print()
            continue

        actual_name = result['name'] or name
        discount = result['discount']
        fetched_variants = result.get('variants', {})

        # --- Variant-aware price checking ---
        if has_variants:
            for variant in variants:
                vname = variant['name']
                vtarget = variant['target_price']

                # Try to find this variant's price in the fetched data
                vprice = None

                # Exact match
                if vname in fetched_variants:
                    vprice = fetched_variants[vname]
                else:
                    # Fuzzy match: check if variant name is contained in any fetched variant
                    for fetched_name, fetched_price in fetched_variants.items():
                        if vname.lower() in fetched_name.lower() or fetched_name.lower() in vname.lower():
                            vprice = fetched_price
                            break

                # If no variant-specific price found, use overall price
                if vprice is None:
                    vprice = result.get('price')

                if vprice is None:
                    print(f"      [{vname}] ❌ Price not found")
                    continue

                # Update history per variant
                history_key = f"{url}##{vname}"
                if history_key not in history:
                    history[history_key] = []
                history[history_key].append({
                    'price': vprice,
                    'discount': discount,
                    'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                if len(history[history_key]) > 200:
                    history[history_key] = history[history_key][-200:]

                # Check against target
                if vprice <= vtarget:
                    print(f"      [{vname}] ₱{vprice:,.2f} ✅ BELOW TARGET (₱{vtarget:,.2f})!")
                    if discount > 0:
                        print(f"        🏷️  {discount}% discount active!")
                    alert_name = f"{actual_name} — {vname}"
                    send_pushbullet_alert(alert_name, vprice, vtarget, url, discount)
                    send_email_alert(alert_name, vprice, vtarget, url, discount, store)
                    alerts_sent += 1
                else:
                    diff = vprice - vtarget
                    print(f"      [{vname}] ₱{vprice:,.2f} — ₱{diff:,.2f} above target (₱{vtarget:,.2f})")

        else:
            # Legacy single-target mode
            target = product.get('target_price', 0)
            current_price = result.get('price')

            if current_price is None:
                print(f"    ❌ Could not fetch price")
                print()
                continue

            # Update history
            product_key = url
            if product_key not in history:
                history[product_key] = []
            history[product_key].append({
                'price': current_price,
                'discount': discount,
                'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            if len(history[product_key]) > 200:
                history[product_key] = history[product_key][-200:]

            # Check against target
            if current_price <= target:
                print(f"    💰 Price: ₱{current_price:,.2f} ✅ BELOW TARGET!")
                if discount > 0:
                    print(f"    🏷️  {discount}% discount active!")
                send_pushbullet_alert(actual_name, current_price, target, url, discount)
                send_email_alert(actual_name, current_price, target, url, discount, store)
                alerts_sent += 1
            else:
                diff = current_price - target
                print(f"    💰 Price: ₱{current_price:,.2f} — ₱{diff:,.2f} above target")
                if discount > 0:
                    print(f"    🏷️  {discount}% discount (still above target)")

        print()

    save_history(history)

    print("-" * 55)
    if alerts_sent > 0:
        print(f"🚨 {alerts_sent} alert(s) sent!")
    else:
        print("✅ No price drops detected. Will check again next run.")
    print(f"💾 History saved to: {HISTORY_FILE}")
    print()


if __name__ == '__main__':
    try:
        run_tracker()
    except KeyboardInterrupt:
        print("\n⛔ Cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
