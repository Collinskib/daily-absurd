"""Agent 3 — Satirical Writer (staffed by Devin).

Each story idea becomes a writing brief; a bounded Devin session writes the
draft article JSON into the queue. The brief carries the house style, the
article schema and the safety rules, so downstream agents stay mechanical.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from .. import config, db
from ..devin import run_session, read_json_output
from .base import traced

REQUIRED_FIELDS = ("slug", "headline", "subheadline", "category", "author",
                   "publishedAt", "tags", "seoTitle", "seoDescription",
                   "sourceEvent", "art", "body")


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:70]


def _write_brief(idea: dict, slug_hint: str, out_path: Path) -> Path:
    ts = int(time.time())
    trend = db.one("SELECT * FROM trends WHERE id=?", (idea["trend_id"],)) or {}
    prompt = config.BRIEFS_DIR / f"writer-{ts}-{slug_hint[:30]}.md"
    prompt.write_text(f"""You are the staff satirical writer for THE DAILY ABSURD —
an international satirical news publication (think: professional newsroom,
absurd copy). The reader must be able to tell it's satire AND laugh anyway.

REAL EVENT YOU ARE SATIRISING (get the underlying facts right):
- Headline: {trend.get('title', idea['title'])}
- Source: {trend.get('source', 'wire')} — {trend.get('source_url', '')}
- Summary: {trend.get('summary', '')[:800]}

ASSIGNED ANGLE: {idea.get('angle', 'find the funniest escalation')}
SUGGESTED CATEGORY: {idea.get('category', 'world-absurdities')}
SUGGESTED SLUG: {slug_hint}

WRITE the article now, then save it as JSON to: {out_path}

JSON schema (all fields required):
{{
  "slug": "{slug_hint}",
  "headline": "funny, punchy, <90 chars",
  "subheadline": "one italic-style teaser line",
  "category": "<one of the 10 slugs>",
  "author": "<invented house byline + desk, e.g. 'Vera Okonkwo, Sports Desk'>",
  "publishedAt": "{db.now()}",
  "tags": ["3-6", "lowercase", "tags"],
  "seoTitle": "search-friendly, <=60 chars, keeps the joke",
  "seoDescription": "<=160 chars, says it's satire",
  "sourceEvent": "2-sentence factual description of the REAL event",
  "sourceUrl": "{trend.get('source_url', '')}",
  "featured": false,
  "art": "{slug_hint}.svg",
  "social": {{
    "x": "post text <=250 chars",
    "facebook": "post text",
    "linkedin": "post text (dry corporate voice) or empty string",
    "instagram": "caption + a few hashtags",
    "altHeadlines": ["2 alternative funny headlines"]
  }},
  "body": "MARKDOWN article, 350-550 words"
}}

ARTICLE CRAFT (follow this structure):
1. Headline that IS the joke's setup.
2. Deadpan news lede: state the absurd thing as fact.
3. Describe the fictional development in straight news style.
4. Escalate: increasingly absurd details, each topping the last.
5. Two or three quotes from clearly FICTIONAL or GENERIC characters
   (a spokesperson, 'local man', 'one analyst' — NEVER put invented words in
   the mouth of a real named person).
6. One more escalation beat.
7. End on the strongest line — the punchline goes LAST ("At press time, …").

SAFETY RULES (hard requirements):
- Clearly recognizable parody; the reader must never mistake it for real news.
- No invented quotes attributed to real identifiable people.
- No fabricated allegations (crimes, corruption, misconduct, illness) about
  real identifiable people. Institutions and generic characters are fine.
- No fake emergency alerts, safety announcements or official statements.
- No punching down at victims or vulnerable groups.
- International English; if a reference is regional, explain it in-line.

Write ONLY the JSON file. Do not reply with the article text.
""")
    return prompt


@traced("writer")
def run() -> dict:
    ideas = db.query(
        "SELECT * FROM story_ideas WHERE status='new' ORDER BY score DESC LIMIT ?",
        (config.MAX_ARTICLES_PER_RUN,),
    )
    written = 0
    for idea in ideas:
        slug = _slugify(idea["title"])
        if db.one("SELECT id FROM drafts WHERE slug=?", (slug,)) or db.one(
            "SELECT id FROM published WHERE slug=?", (slug,)
        ):
            db.run("UPDATE story_ideas SET status='exhausted', updated_at=? WHERE id=?",
                   (db.now(), idea["id"]))
            continue
        out = config.DRAFTS_DIR / f"{slug}.json"
        prompt = _write_brief(idea, slug, out)
        res = run_session(prompt, out)
        if not res.ok:
            db.run("UPDATE story_ideas SET updated_at=? WHERE id=?", (db.now(), idea["id"]))
            continue
        draft = read_json_output(out)
        if not draft or not all(k in draft for k in REQUIRED_FIELDS):
            out.unlink(missing_ok=True)
            continue
        # Force consistency fields.
        draft["slug"] = slug
        draft.setdefault("publishedAt", db.now())
        db.write_json(out, draft)
        db.run(
            """INSERT INTO drafts (id, idea_id, slug, path, status, created_at, updated_at)
               VALUES (?,?,?,?,'written',?,?)""",
            (db.uid(), idea["id"], slug, str(out), db.now(), db.now()),
        )
        db.run("UPDATE story_ideas SET status='drafted', updated_at=? WHERE id=?",
               (db.now(), idea["id"]))
        written += 1
    return {"detail": f"{written} drafts written", "written": written}
