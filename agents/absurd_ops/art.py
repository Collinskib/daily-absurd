"""Deterministic editorial art: duotone SVG cards per article."""
from __future__ import annotations

import hashlib
from pathlib import Path

PALETTES = [
    ("#16130e", "#faf6ec", "#e63b12"),
    ("#faf6ec", "#16130e", "#e63b12"),
    ("#16130e", "#faf6ec", "#d9a521"),
]

SHAPES = [
    "circles", "bars", "arc",
]


def _svg(slug: str, category: str, headline: str) -> str:
    h = int(hashlib.sha256(slug.encode()).hexdigest(), 16)
    bg, fg, accent = PALETTES[h % len(PALETTES)]
    kind = SHAPES[h % len(SHAPES)]
    seed = h % 997

    if kind == "circles":
        art = "".join(
            f'<circle cx="{200 + ((seed * (i + 3)) % 800)}" cy="{140 + ((seed * (i + 7)) % 320)}" '
            f'r="{40 + ((seed * (i + 11)) % 90)}" fill="{accent if i % 3 == 0 else fg}" '
            f'fill-opacity="{0.9 if i % 3 == 0 else 0.15}"/>'
            for i in range(5)
        )
    elif kind == "bars":
        art = "".join(
            f'<rect x="{150 + i * 180}" y="{420 - ((seed * (i + 5)) % 260)}" '
            f'width="120" height="{80 + ((seed * (i + 5)) % 260)}" '
            f'fill="{accent if i % 2 == 0 else fg}"/>'
            for i in range(5)
        )
    else:
        art = (
            f'<path d="M150 460 Q600 {60 + seed % 120} 1050 460" stroke="{fg}" '
            f'stroke-width="14" fill="none"/>'
            f'<circle cx="600" cy="{120 + seed % 100}" r="70" fill="{accent}"/>'
        )

    words = headline.split()
    line1 = " ".join(words[:4])
    line2 = " ".join(words[4:9])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600">
  <rect width="1200" height="600" fill="{bg}"/>
  {art}
  <rect x="60" y="60" width="1080" height="480" fill="none" stroke="{fg}" stroke-width="5"/>
  <rect x="90" y="90" width="150" height="46" fill="{accent}"/>
  <text x="165" y="122" font-family="Helvetica,sans-serif" font-size="24" font-weight="bold"
        fill="{bg}" text-anchor="middle" letter-spacing="3">SATIRE</text>
  <text x="600" y="500" font-family="Georgia,serif" font-style="italic" font-size="30"
        fill="{fg}" text-anchor="middle">{_esc(line1)}</text>
  <text x="600" y="538" font-family="Georgia,serif" font-style="italic" font-size="30"
        fill="{fg}" fill-opacity="0.7" text-anchor="middle">{_esc(line2)}</text>
</svg>'''


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def ensure_art(slug: str, category: str, headline: str, art_name: str | None = None) -> str:
    """Write a deterministic SVG for the article; returns the filename."""
    from . import config

    name = art_name or f"{slug}.svg"
    if not name.endswith(".svg"):
        name = f"{slug}.svg"
    path = config.ART_DIR / name
    if not path.exists():
        path.write_text(_svg(slug, category, headline))
    return name
