"""
PhotoGPT AI — Styles & Templates Scraper
Uses Scrapling DynamicFetcher (full browser) since the site is JS-rendered.
"""

from scrapling.fetchers import Fetcher
import json, re

def scrape_photogpt_styles():
    print("🤖 Fetching styles from PhotoGPT...")

    # Fetch the presets page to get the JS bundle filename
    page = Fetcher.get('https://www.photogptai.com/presets', stealthy_headers=True, follow_redirects=True)
    bundle = re.search(r'/assets/(Presets-[^"]+\.js)', page.html_content)
    if not bundle:
        print("❌ Could not find Presets JS bundle"); return

    bundle_url = f"https://www.photogptai.com/assets/{bundle.group(1)}"
    print(f"📦 Found bundle: {bundle_url}")

    js = Fetcher.get(bundle_url, stealthy_headers=True)
    content = js.html_content

    # Extract all preset objects
    raw = re.findall(r'\{name:`([^`]+)`,description:`([^`]+)`', content)
    styles = [{'name': name, 'description': desc} for name, desc in raw]

    print(f"\n✅ Found {len(styles)} styles:\n")
    for i, s in enumerate(styles, 1):
        print(f"{i:>3}. 🎨 {s['name']}")
        print(f"       {s['description'][:80]}...")
        print()

    with open('photogpt_styles.json', 'w') as f:
        json.dump(styles, f, indent=2)
    print(f"\n💾 Saved to photogpt_styles.json")
    return styles

    styles = []

    # Try common CSS selectors for style/template cards
    cards = (
        page.css('.preset-card') or
        page.css('[class*="preset"]') or
        page.css('[class*="template"]') or
        page.css('[class*="style"]') or
        page.css('.card')
    )

    print(f"✅ Found {len(cards)} style cards\n")

    for card in cards:
        name  = (card.css('h2, h3, h4, [class*="title"], [class*="name"]') or [None])[0]
        desc  = (card.css('p, [class*="desc"]') or [None])[0]
        img   = (card.css('img') or [None])[0]

        style = {
            'name':        name.text.strip()         if name else 'N/A',
            'description': desc.text.strip()         if desc else 'N/A',
            'image_url':   img.attrib.get('src', '')  if img  else 'N/A',
        }
        styles.append(style)
        print(f"🎨 {style['name']}")

    # Save to JSON
    with open('photogpt_styles.json', 'w') as f:
        json.dump(styles, f, indent=2)

    print(f"\n💾 Saved {len(styles)} styles to photogpt_styles.json")
    return styles


if __name__ == '__main__':
    scrape_photogpt_styles()
