"""Agent 7 — Social Media Creative.

Turns each approved article into a per-platform asset pack (posts, captions,
alt headlines, short-video script scaffold, share-card SVG). Packs are
written to the queue; posting them is social_poster's job (opt-in via
ABSURD_SOCIAL_POST=1).
"""
from __future__ import annotations

import json
from pathlib import Path

from .. import config, db
from .base import traced

VIDEO_SCRIPT = """HOOK (0-2s): {hook}
BEAT (2-8s): {beat}
PAYOFF (8-20s): {payoff}
CTA (20-25s): Read the full fabrication at thedailyabsurd — link in bio.
ON-SCREEN TEXT: "SATIRE — not real news" (persistent, top-left)
"""


def _share_card(slug: str, headline: str) -> Path:
    out = config.SOCIAL_DIR / f"{slug}-card.svg"
    words = headline.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) > 38:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    text = "\n".join(
        f'<text x="600" y="{260 + i * 62}" font-family="Georgia,serif" font-size="52" '
        f'font-weight="bold" fill="#faf6ec" text-anchor="middle">{l}</text>'
        for i, l in enumerate(lines[:4])
    )
    out.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080">
  <rect width="1080" height="1080" fill="#16130e"/>
  <rect x="50" y="50" width="980" height="980" fill="none" stroke="#e63b12" stroke-width="6"/>
  <text x="540" y="160" font-family="Georgia,serif" font-size="64" font-weight="bold"
        fill="#faf6ec" text-anchor="middle">The Daily <tspan fill="#e63b12" font-style="italic">Absurd</tspan></text>
  {text}
  <text x="540" y="960" font-family="Helvetica,sans-serif" font-size="30" font-weight="bold"
        fill="#e63b12" text-anchor="middle" letter-spacing="8">SATIRE · NOT REAL NEWS</text>
</svg>''')
    return out


@traced("social_agent")
def run() -> dict:
    drafts = db.query(
        """SELECT d.*, p.slug IS NULL AS unpublished FROM drafts d
           LEFT JOIN published p ON p.slug = d.slug
           WHERE d.status IN ('approved','published')"""
    )
    made = 0
    for d in drafts:
        path = Path(d["path"])
        try:
            draft = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        slug = d["slug"]
        if db.one("SELECT id FROM social_assets WHERE slug=? AND platform='x'", (slug,)):
            continue
        social = draft.get("social", {})
        url = f"{config.SITE_URL}/articles/{slug}"
        pack = {
            "slug": slug,
            "url": url,
            "x": f"{social.get('x', draft['headline'])}\n{url}",
            "facebook": f"{social.get('facebook', draft['subheadline'])}\n{url}",
            "linkedin": (f"{social.get('linkedin', '')}\n{url}" if social.get("linkedin") else ""),
            "instagram": f"{social.get('instagram', draft['subheadline'])}\n🔗 {url}",
            "pinterest": f"{draft['headline']} — satirical take on {draft.get('sourceEvent','')[:80]}",
            "altHeadlines": social.get("altHeadlines", []),
            "shortVideoScript": VIDEO_SCRIPT.format(
                hook=draft["headline"],
                beat=draft["subheadline"],
                payoff="The punchline: " + draft["body"].rsplit("At press time", 1)[-1][:160]
                if "At press time" in draft["body"] else draft["body"][:160],
            ),
        }
        pack_path = config.SOCIAL_DIR / f"{slug}.json"
        db.write_json(pack_path, pack)
        card = _share_card(slug, draft["headline"])
        for platform, kind, content in (
            ("x", "post", pack["x"]), ("facebook", "post", pack["facebook"]),
            ("linkedin", "post", pack["linkedin"]), ("instagram", "caption", pack["instagram"]),
            ("pinterest", "concept", pack["pinterest"]),
            ("shorts", "script", pack["shortVideoScript"]),
        ):
            db.run(
                "INSERT INTO social_assets (id, slug, platform, kind, path, content, created_at) VALUES (?,?,?,?,?,?,?)",
                (db.uid(), slug, platform, kind, str(pack_path), content, db.now()),
            )
        db.run(
            "INSERT INTO social_assets (id, slug, platform, kind, path, created_at) VALUES (?,?,?,?,?,?)",
            (db.uid(), slug, "all", "graphic", str(card), db.now()),
        )
        made += 1
    return {"detail": f"{made} social packs generated", "packs": made}
