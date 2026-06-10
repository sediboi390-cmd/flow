"""
Price Drop Alert Tracker v2 — Scrapling Edition
Uses Scrapling's DynamicFetcher to render JavaScript and extract variant prices.

Install:  pip install "scrapling[all]"
          scrapling install --force
Run:      python price_drop_tracker_v2.py
"""

import json, os, re, smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

try:
    from scrapling.fetchers import Fetcher, DynamicFetcher
except ImportError:
    print("ERROR: Scrapling not installed. Run: pip install 'scrapling[all]'")
    sys.exit(1)

# ── Config ──────────────────────────────────────────
WATCHLIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "price_watchlist.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "price_history.json")

EMAIL_SENDER = "sediboi390@gmail.com"
EMAIL_PASSWORD = "zsdwrlbrvjqjlthe"
EMAIL_RECEIVER = "sediboi390@gmail.com"
PUSHBULLET_TOKEN = "o.agbesjAzlZdQFUVWmgS35YqPh9EHlotu"

MAX_PRODUCTS = 5
USE_BROWSER = True  # Set False to use fast HTTP (no JS rendering, less accurate)
# ────────────────────────────────────────────────────


def validate_product(product):
    """Validate a product entry."""
    name = product.get('name', '')
    url = product.get('url', '')
    store = product.get('store', '')
    enabled = product.get('enabled')

    if not name or not isinstance(name, str) or not name.strip():
        return False, "name is empty"
    if not url or not isinstance(url, str):
        return False, "url is empty"
    if 'shopee' not in url.lower() and 'lazada' not in url.lower():
        return False, "url must contain 'shopee' or 'lazada'"
    if store not in ('shopee', 'lazada'):
        return False, f"store must be 'shopee' or 'lazada'"
    if not isinstance(enabled, bool):
        return False, "enabled must be true or false"

    has_target = isinstance(product.get('target_price'), (int, float)) and product.get('target_price', 0) > 0
    has_variants = isinstance(product.get('variants'), list) and len(product.get('variants', [])) > 0
    if not has_target and not has_variants:
        return False, "must have target_price or variants"

    return True, ""


def load_watchlist():
    """Load and validate watchlist."""
    if not os.path.exists(WATCHLIST_FILE):
        default = {"products": [{"name": "Example", "url": "https://shopee.ph/product/123/456", "target_price": 5000, "store": "shopee", "enabled": False}]}
        with open(WATCHLIST_FILE, 'w') as f:
            json.dump(default, f, indent=2)
        print(f"Created watchlist at: {WATCHLIST_FILE}")
        return default

    with open(WATCHLIST_FILE) as f:
        data = json.load(f)

    products = data.get('products', [])
    valid = []
    for i, p in enumerate(products):
        ok, err = validate_product(p)
        if ok:
            valid.append(p)
        else:
            print(f"  Warning: Product #{i+1} '{p.get('name','?')}' skipped: {err}")

    if len(valid) > MAX_PRODUCTS:
        print(f"  Warning: {len(valid)} products, max {MAX_PRODUCTS}. Using first {MAX_PRODUCTS}.")
        valid = valid[:MAX_PRODUCTS]

    data['products'] = valid
    return data


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}


def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def fetch_shopee(url):
    """Fetch Shopee product page with Scrapling, extract prices and variants."""
    try:
        if USE_BROWSER:
            page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=30000)
        else:
            page = Fetcher.get(url)

        # Product name
        name = page.css('meta[property="og:title"]::attr(content)').get()
        if not name:
            name = page.css('title::text').get()
        if name:
            name = name.strip().split(' | ')[0]

        # Overall price
        price = None
        price_el = page.css('.pqTWkA::text').get()  # Shopee price class
        if not price_el:
            price_el = page.css('[class*="price"]::text').get()
        if price_el:
            price_clean = re.sub(r'[^\d.]', '', price_el.replace(',', ''))
            if price_clean:
                price = float(price_clean)

        # Fallback: extract from page source
        if price is None:
            body = page.body.decode('utf-8', errors='ignore') if isinstance(page.body, bytes) else str(page.body)
            m = re.search(r'"price_min"\s*:\s*(\d{6,})', body)
            if m:
                price = int(m.group(1)) / 100000

        # Discount
        discount = 0
        disc_el = page.css('[class*="discount"]::text').get()
        if disc_el:
            disc_m = re.search(r'(\d+)%', disc_el)
            if disc_m:
                discount = int(disc_m.group(1))

        # Variant prices
        variants = {}
        # Try extracting from variant buttons/options
        variant_els = page.css('[class*="variant"], [class*="model"], .product-variation')
        for el in variant_els:
            vname = el.css('::text').get()
            if vname:
                vname = vname.strip()
                if vname and len(vname) > 1:
                    variants[vname] = None  # Name found but price needs matching

        # Try extracting variant prices from JSON in page source
        body = page.body.decode('utf-8', errors='ignore') if isinstance(page.body, bytes) else str(page.body)
        models_match = re.search(r'"models"\s*:\s*\[([^\]]+)\]', body)
        if models_match:
            models_str = models_match.group(1)
            entries = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]*?"price"\s*:\s*(\d{6,})', models_str)
            for vn, vp in entries:
                variants[vn] = int(vp) / 100000
            if not entries:
                entries2 = re.findall(r'"price"\s*:\s*(\d{6,})[^}]*?"name"\s*:\s*"([^"]+)"', models_str)
                for vp, vn in entries2:
                    variants[vn] = int(vp) / 100000

        # Remove variants with no price
        variants = {k: v for k, v in variants.items() if v is not None}

        return {'name': name, 'price': price, 'discount': discount, 'variants': variants, 'status': 'ok'}

    except Exception as e:
        return {'name': None, 'price': None, 'discount': 0, 'variants': {}, 'status': f'error: {e}'}


def fetch_lazada(url):
    """Fetch Lazada product page with Scrapling, extract prices and variants."""
    try:
        if USE_BROWSER:
            page = DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=30000)
        else:
            page = Fetcher.get(url)

        # Product name
        name = page.css('meta[property="og:title"]::attr(content)').get()
        if not name:
            name = page.css('title::text').get()
        if name:
            name = name.strip()

        # Price
        price = None
        price_el = page.css('[class*="price"] span::text').get()
        if not price_el:
            price_el = page.css('[data-price]::attr(data-price)').get()
        if price_el:
            price_clean = re.sub(r'[^\d.]', '', price_el.replace(',', ''))
            if price_clean:
                price = float(price_clean)

        # Fallback from source
        if price is None:
            body = page.body.decode('utf-8', errors='ignore') if isinstance(page.body, bytes) else str(page.body)
            m = re.search(r'"price"\s*:\s*"?(\d+\.?\d*)"?', body)
            if m:
                price = float(m.group(1))

        # Discount
        discount = 0
        disc_el = page.css('[class*="discount"]::text').get()
        if disc_el:
            disc_m = re.search(r'(\d+)%', disc_el)
            if disc_m:
                discount = int(disc_m.group(1))

        # Variants from SKU selectors
        variants = {}
        body = page.body.decode('utf-8', errors='ignore') if isinstance(page.body, bytes) else str(page.body)
        sku_entries = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]*?"price"\s*:\s*"?(\d+\.?\d*)"?', body)
        for vn, vp in sku_entries:
            try:
                v_price = float(vp)
                if 100 < v_price < 1000000:
                    variants[vn] = v_price
            except ValueError:
                pass

        return {'name': name, 'price': price, 'discount': discount, 'variants': variants, 'status': 'ok'}

    except Exception as e:
        return {'name': None, 'price': None, 'discount': 0, 'variants': {}, 'status': f'error: {e}'}


def check_price(product):
    """Route to the correct store fetcher."""
    store = product.get('store', '')
    url = product['url']
    if store == 'shopee':
        return fetch_shopee(url)
    elif store == 'lazada':
        return fetch_lazada(url)
    return {'name': None, 'price': None, 'discount': 0, 'variants': {}, 'status': 'unknown store'}


def send_pushbullet(product_name, current_price, target_price, url, discount):
    """Send Pushbullet push."""
    try:
        import requests
        body = f"P{current_price:,.0f} (target P{target_price:,.0f})"
        if discount > 0:
            body += f" | {discount}% OFF!"
        body += "\nTap to buy!"

        resp = requests.post(
            'https://api.pushbullet.com/v2/pushes',
            headers={'Access-Token': PUSHBULLET_TOKEN, 'Content-Type': 'application/json'},
            json={"type": "link", "title": f"Price Drop! {product_name}", "body": body, "url": url},
            timeout=10
        )
        print(f"    Pushbullet: {'OK' if resp.status_code == 200 else f'Error {resp.status_code}'}")
    except Exception as e:
        print(f"    Pushbullet failed: {e}")


def send_email(product_name, current_price, target_price, url, discount, store):
    """Send email alert."""
    try:
        savings = target_price - current_price
        disc_text = f" ({discount}% OFF)" if discount > 0 else ""

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Price Drop! {product_name} - P{current_price:,.0f}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        text = f"PRICE DROP!\n\n{product_name}\nPrice: P{current_price:,.0f}{disc_text}\nTarget: P{target_price:,.0f}\nSave: P{savings:,.0f}\nStore: {store}\n\nBuy: {url}"
        html = f"""<html><body style="font-family:Arial;max-width:500px;margin:auto;padding:20px">
<div style="background:linear-gradient(135deg,#ff6b35,#f7c948);color:#fff;padding:20px;border-radius:12px;text-align:center"><h1>PRICE DROP!</h1></div>
<div style="padding:20px;border:1px solid #eee;border-radius:12px;margin-top:16px">
<h2>{product_name}</h2>
<div style="background:#f0fff0;border:2px solid #2a9d6b;border-radius:8px;padding:16px;margin:12px 0">
<p style="margin:0;font-size:1.5rem;font-weight:bold;color:#2a9d6b">&#8369;{current_price:,.0f}</p>
<p style="margin:4px 0 0;color:#666">Target: &#8369;{target_price:,.0f} &bull; Save &#8369;{savings:,.0f}{disc_text}</p></div>
<p>Store: <strong>{store.title()}</strong></p>
<a href="{url}" style="display:inline-block;background:#ff6b35;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:bold">Buy Now</a>
</div></body></html>"""

        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"    Email: sent!")
    except Exception as e:
        print(f"    Email failed: {e}")


def run_tracker():
    """Main tracker — fetches prices using Scrapling."""
    print("=" * 55)
    print("  Price Drop Tracker v2 (Scrapling)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: {'Browser (JS rendering)' if USE_BROWSER else 'HTTP only (fast)'}")
    print("=" * 55)

    watchlist = load_watchlist()
    history = load_history()
    enabled = [p for p in watchlist.get('products', []) if p.get('enabled', True)]

    if not enabled:
        print("\n  No enabled products. Edit price_watchlist.json")
        return

    print(f"\n  Checking {len(enabled)} product(s)...\n")
    alerts = 0

    for i, product in enumerate(enabled, 1):
        name = product.get('name', 'Unknown')
        url = product['url']
        store = product.get('store', 'unknown')
        variants_config = product.get('variants', [])
        has_variants = isinstance(variants_config, list) and len(variants_config) > 0

        print(f"  [{i}/{len(enabled)}] {name} ({store.title()})")

        result = check_price(product)

        if result['status'] != 'ok':
            print(f"    Error: {result['status']}")
            print()
            continue

        actual_name = result['name'] or name
        discount = result['discount']
        fetched_variants = result.get('variants', {})

        if fetched_variants:
            print(f"    Found {len(fetched_variants)} variant price(s) on page")

        if has_variants:
            for variant in variants_config:
                vname = variant['name']
                vtarget = variant['target_price']
                vprice = None

                # Match variant price
                if vname in fetched_variants:
                    vprice = fetched_variants[vname]
                else:
                    for fn, fp in fetched_variants.items():
                        if vname.lower() in fn.lower() or fn.lower() in vname.lower():
                            vprice = fp
                            break

                if vprice is None:
                    vprice = result.get('price')

                if vprice is None:
                    print(f"    [{vname}] price not found")
                    continue

                # History
                hkey = f"{url}##{vname}"
                if hkey not in history:
                    history[hkey] = []
                history[hkey].append({'price': vprice, 'discount': discount, 'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                if len(history[hkey]) > 200:
                    history[hkey] = history[hkey][-200:]

                if vprice <= vtarget:
                    print(f"    [{vname}] P{vprice:,.0f} <= P{vtarget:,.0f} ALERT!")
                    send_pushbullet(f"{actual_name} - {vname}", vprice, vtarget, url, discount)
                    send_email(f"{actual_name} - {vname}", vprice, vtarget, url, discount, store)
                    alerts += 1
                else:
                    print(f"    [{vname}] P{vprice:,.0f} (target P{vtarget:,.0f}, P{vprice - vtarget:,.0f} above)")

        else:
            target = product.get('target_price', 0)
            cprice = result.get('price')
            if cprice is None:
                print(f"    Price not found")
                print()
                continue

            hkey = url
            if hkey not in history:
                history[hkey] = []
            history[hkey].append({'price': cprice, 'discount': discount, 'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            if len(history[hkey]) > 200:
                history[hkey] = history[hkey][-200:]

            if cprice <= target:
                print(f"    P{cprice:,.0f} <= P{target:,.0f} ALERT!")
                send_pushbullet(actual_name, cprice, target, url, discount)
                send_email(actual_name, cprice, target, url, discount, store)
                alerts += 1
            else:
                print(f"    P{cprice:,.0f} (target P{target:,.0f}, P{cprice - target:,.0f} above)")

        print()

    save_history(history)
    print("-" * 55)
    print(f"  {'ALERTS SENT: ' + str(alerts) if alerts else 'No price drops. Checking again next run.'}")
    print(f"  History: {HISTORY_FILE}")
    print()


if __name__ == '__main__':
    try:
        run_tracker()
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
