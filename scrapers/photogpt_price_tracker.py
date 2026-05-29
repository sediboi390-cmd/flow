"""
PhotoGPT AI — Price Tracker
Scrapes pricing plans from photogptai.com/pricing
Saves to JSON and compares with previous run to detect changes.
"""

from scrapling.fetchers import Fetcher
import json, re, os
from datetime import datetime

SAVE_FILE = 'photogpt_prices.json'
HISTORY_FILE = 'photogpt_prices_history.json'

def scrape_prices():
    print("🤖 Fetching PhotoGPT pricing page...")

    # Get the pricing page
    page = Fetcher.get(
        'https://www.photogptai.com/pricing',
        stealthy_headers=True,
        follow_redirects=True
    )
    print(f"✅ Status: {page.status}")

    # Find the JS bundle that contains pricing data
    bundles = re.findall(r'/assets/([^"]+\.js)', page.html_content)
    print(f"📦 Found {len(bundles)} JS bundles")

    prices = []

    # Search each bundle for pricing data
    for bundle in bundles:
        url = f"https://www.photogptai.com/assets/{bundle}"
        try:
            js = Fetcher.get(url, stealthy_headers=True)
            content = js.html_content

            # Look for price patterns like $9.99, $19, £9 etc.
            price_matches = re.findall(
                r'(?:price|amount|cost|plan)[^{]*?\{[^}]*?'
                r'(?:name|title)[:\s]*[`"\']([^`"\']+)[`"\'],[^}]*?'
                r'(?:price|amount|cost)[:\s]*[`"\']?\$?(\d+(?:\.\d+)?)',
                content, re.IGNORECASE
            )
            if price_matches:
                print(f"💰 Found pricing in: {bundle}")
                for name, price in price_matches:
                    prices.append({'plan': name, 'price': f'${price}'})
                break

            # Also try simpler pattern
            simple = re.findall(
                r'[`"\']([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)[`"\'][^}]{0,50}'
                r'\$(\d+(?:\.\d+)?)',
                content
            )
            if simple:
                for name, price in simple[:10]:
                    if any(k in name.lower() for k in ['free','basic','pro','starter','premium','enterprise','month','year']):
                        prices.append({'plan': name, 'price': f'${price}'})

        except Exception as e:
            continue

    # Scrape prices directly from HTML using known class names
    if not prices:
        print("🔍 Parsing pricing from HTML...")
        import re as _re
        # Extract all plan cards using regex on raw HTML
        card_pattern = _re.findall(
            r'PhotoGPT\s(\w+)\sPlan.*?'
            r'\$(\d+(?:\.\d+)?)</span>.*?'
            r'per month.*?'
            r'(?:was|<del[^>]*>)\$?(\d+(?:\.\d+)?).*?'
            r'Billed\s+\$(\d+(?:\.\d+)?)\s+every\s+([^<]+)',
            page.html_content, _re.DOTALL
        )
        for match in card_pattern:
            plan, current, was, billed_amt, period = match
            prices.append({
                'plan': f'PhotoGPT {plan} Plan',
                'price_per_month': f'${current}',
                'original_price': f'${was}',
                'billed': f'${billed_amt} every {period.strip()}'
            })

    # Fallback: simple dollar regex from HTML
    if not prices:
        import re as _re
        names = _re.findall(r'PhotoGPT\s(\w+)\sPlan', page.html_content)
        prices_found = _re.findall(r'text-4xl[^>]+>\$(\d+(?:\.\d+)?)', page.html_content)
        originals = _re.findall(r'<del[^>]*>\$(\d+(?:\.\d+)?)</del>', page.html_content)
        for i, name in enumerate(names):
            prices.append({
                'plan': f'PhotoGPT {name} Plan',
                'price_per_month': f'${prices_found[i]}' if i < len(prices_found) else 'N/A',
                'original_price': f'${originals[i]}' if i < len(originals) else 'N/A',
            })

    return prices


def save_and_compare(prices):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Load previous data
    old_prices = []
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            old_data = json.load(f)
            old_prices = old_data.get('prices', [])

    # Detect changes
    changes = []
    old_map = {p['plan']: p.get('price_per_month', p.get('price','N/A')) for p in old_prices}
    new_map = {p['plan']: p.get('price_per_month', p.get('price','N/A')) for p in prices}

    for plan, price in new_map.items():
        if plan not in old_map:
            changes.append(f"🆕 NEW plan: {plan} → {price}")
        elif old_map[plan] != price:
            changes.append(f"💸 PRICE CHANGE: {plan} — {old_map[plan]} → {price}")

    for plan in old_map:
        if plan not in new_map:
            changes.append(f"❌ REMOVED plan: {plan}")

    # Save current
    data = {'timestamp': timestamp, 'prices': prices}
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    # Append to history
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    history.append(data)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

    return changes


def main():
    prices = scrape_prices()

    print(f"\n{'='*50}")
    if prices:
        print(f"💰 Found {len(prices)} pricing plans:\n")
        for p in prices:
            print(f"  📦 {p['plan']}")
            print(f"     Current : {p.get('price_per_month', p.get('price','N/A'))}/month")
            if p.get('original_price'):
                print(f"     Was     : {p['original_price']}/month")
            if p.get('billed'):
                print(f"     Billed  : {p['billed']}")
            print()
    else:
        print("⚠️  No pricing data found directly.")
        print("💡 The site likely requires JavaScript to render prices.")
        print("    To get full pricing, run with a browser-based fetcher")
        print("    or visit: https://www.photogptai.com/pricing")

    changes = save_and_compare(prices)

    print(f"\n{'='*50}")
    if changes:
        print("🚨 CHANGES DETECTED:\n")
        for c in changes:
            print(f"  {c}")
    else:
        print("✅ No price changes detected since last run.")

    print(f"\n💾 Saved to {SAVE_FILE}")
    print(f"📜 History saved to {HISTORY_FILE}")
    print(f"🕐 Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
