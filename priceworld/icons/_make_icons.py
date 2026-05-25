"""Generate PriceWorld PWA icons.

Creates three PNGs in the same directory:
  - icon-192.png            (any purpose, 192x192)
  - icon-512.png            (any purpose, 512x512)
  - icon-maskable-512.png   (maskable, 512x512, padded safe area)

Run once: `python3 _make_icons.py`
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

HERE = Path(__file__).parent

# Brand gradient endpoints (match app's --accent / purple gradient).
GRAD_TOP = (108, 99, 255)     # #6c63ff
GRAD_BOT = (168, 85, 247)     # #a855f7
EMOJI = "\U0001F30D"          # 🌍


def make_gradient(size, top, bottom, radius_ratio=0.22):
    """Square image with vertical gradient and rounded corners."""
    w = h = size
    base = Image.new("RGB", (w, h), top)
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        px_color = (
            int(top[0] + (bottom[0] - top[0]) * t),
            int(top[1] + (bottom[1] - top[1]) * t),
            int(top[2] + (bottom[2] - top[2]) * t),
        )
        for x in range(w):
            px[x, y] = px_color

    # Apply rounded corners via mask.
    radius = int(size * radius_ratio)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(base, (0, 0), mask)
    return out


def find_emoji_font(size):
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def draw_glyph(img, text, font_size_ratio=0.55):
    """Draw a centered white-ish glyph; falls back gracefully if no emoji font."""
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font = find_emoji_font(int(min(w, h) * font_size_ratio))

    try:
        bbox = draw.textbbox((0, 0), text, font=font, embedded_color=True)
    except TypeError:
        bbox = draw.textbbox((0, 0), text, font=font)

    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (w - tw) // 2 - bbox[0]
    y = (h - th) // 2 - bbox[1]

    try:
        # Color emoji rendering (Pillow >= 9.2 with libraqm).
        draw.text((x, y), text, font=font, embedded_color=True)
    except TypeError:
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))


def write_icon(size, path, maskable=False):
    radius_ratio = 0.5 if maskable else 0.22  # maskable = full circle safe area
    img = make_gradient(size, GRAD_TOP, GRAD_BOT, radius_ratio=radius_ratio)
    # Maskable icons need ~10% safe-zone padding on each side.
    glyph_ratio = 0.45 if maskable else 0.6
    draw_glyph(img, EMOJI, font_size_ratio=glyph_ratio)
    img.save(path, format="PNG", optimize=True)
    print(f"wrote {path} ({size}x{size})")


if __name__ == "__main__":
    write_icon(192, HERE / "icon-192.png")
    write_icon(512, HERE / "icon-512.png")
    write_icon(512, HERE / "icon-maskable-512.png", maskable=True)
