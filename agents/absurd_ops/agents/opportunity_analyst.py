"""Agent 2 — Satire Opportunity Analyst.

Scores raw trends for comedic potential. Cheap heuristic pre-scoring keeps
Devin calls rare: one batched session picks angles for the strongest
candidates. Heuristic fallback keeps the pipeline alive if a session fails.
"""
from __future__ import annotations

import json
import re
import time

from .. import config, db
from ..devin import run_session, read_json_output
from .base import traced

ABSURD_SIGNALS = {
    "strong": [
        "bizarre", "weird", "unusual", "strange", "odd", "quirky", "coincidence",
        "accidentally", "mistaken", "error", "glitch", "outage", "recall",
        "apology", "apologise", "apologize", "coin", "toss", "record", "pumpkin",
        "goat", "dog", "cat", "emotional support", "ai ", "robot", "chatbot",
        "outrage", "backlash", "viral", "baffled", "confused", "ban ",
        "banned", "fine", "fined", "lawsuit", "sued", "rebrands", "rebrand",
    ],
    "risky": [
        "killed", "dead", "death", "dies", "murder", "crash victims", "rape",
        "suicide", "terror", "bombing", "massacre", "genocide", "torture",
        "child abuse", "school shooting", "hostage", "famine", "earthquake victims",
    ],
}

CATEGORY_HINTS: list[tuple[str, str]] = [
    (r"\b(ai|chatgpt|openai|robot|algorithm|app|software|tech|crypto|data|cyber)\b", "technology-ai"),
    (r"\b(election|minister|parliament|government|senate|congress|vote|policy|law)\b", "politics-government"),
    (r"\b(stock|market|ceo|company|business|billion|startup|funding|economy|inflation)\b", "business-money"),
    (r"\b(film|movie|celebrity|music|singer|actor|netflix|concert|star)\b", "entertainment-celebrity"),
    (r"\b(meme|viral|tiktok|reddit|internet|influencer|trend|hashtag)\b", "internet-culture"),
    (r"\b(scientist|study|research|space|nasa|climate|health|medical|vaccine)\b", "science-innovation"),
    (r"\b(football|soccer|cricket|tennis|olympic|match|player|league|fifa|rugby)\b", "sports"),
    (r"\b(wedding|dating|marriage|couple|relationship|divorce|family)\b", "relationships-society"),
]
DEFAULT_CATEGORY = "world-absurdities"


def _heuristic_score(title: str, summary: str, source: str) -> tuple[float, dict, bool]:
    text = f"{title} {summary}".lower()
    scores = {
        "humour": 4.0,
        "shareability": 4.0,
        "timeliness": 6.0,
        "international": 5.0,
        "originality": 5.0,
        "risk": 0.0,
    }
    for sig in ABSURD_SIGNALS["strong"]:
        if sig in text:
            scores["humour"] += 0.6
            scores["shareability"] += 0.4
    for sig in ABSURD_SIGNALS["risky"]:
        if sig in text:
            scores["risk"] += 3.0
    if source in ("Reddit NotTheOnion", "Reddit Offbeat"):
        scores["humour"] += 1.5
        scores["originality"] += 1.0
    total = (
        scores["humour"] * 0.3 + scores["shareability"] * 0.2
        + scores["timeliness"] * 0.15 + scores["international"] * 0.15
        + scores["originality"] * 0.2
    )
    risky = scores["risk"] >= 3.0
    return round(min(total, 10.0), 2), scores, risky


def _guess_category(text: str) -> str:
    for pattern, cat in CATEGORY_HINTS:
        if re.search(pattern, text, re.I):
            return cat
    return DEFAULT_CATEGORY


def _already_covered(title: str) -> bool:
    words = {w for w in re.findall(r"[a-z]{4,}", title.lower())}
    for row in db.query("SELECT title FROM story_ideas"):
        existing = {w for w in re.findall(r"[a-z]{4,}", row["title"].lower())}
        if words and len(words & existing) / len(words | existing) > 0.5:
            return True
    return False


def _devin_angle_pass(candidates: list[dict]) -> list[dict] | None:
    """One session scores + angles the whole batch. Returns parsed ideas."""
    ts = int(time.time())
    prompt = config.BRIEFS_DIR / f"analyst-{ts}.md"
    out = config.BRIEFS_DIR / f"ideas-{ts}.json"

    cand_lines = "\n".join(
        f"{i+1}. [{c['source']}] {c['title']} — {c['summary'][:200]} (url: {c['source_url']})"
        for i, c in enumerate(candidates)
    )
    prompt.write_text(f"""You are the Satire Opportunity Analyst for The Daily Absurd,
an international satirical news publication. Below are real trending stories.

{cand_lines}

Your job: choose AT MOST {config.MAX_IDEAS_PER_RUN} stories with the strongest
comedic potential for an international audience. For each, output:

- "trend_index": the 1-based index above
- "title": short working title
- "angle": the single central comedic idea (one sentence — premise + twist)
- "category": one of world-absurdities, politics-government, technology-ai,
  business-money, entertainment-celebrity, internet-culture,
  science-innovation, everyday-life, sports, relationships-society
- "scores": object with keys humour, shareability, timeliness,
  international, originality, risk — each 0-10
- "score": weighted total 0-10 (humour .3, shareability .2, timeliness .15,
  international .15, originality .2)

Rules: pick recognizable premises with unexpected punchlines. Skip duplicates
of the same joke. Skip tragedies and sensitive breaking news. Prefer stories
that work for readers outside the US.

Write ONLY a JSON array to {out}. Do not print explanations.
""")
    res = run_session(prompt, out, timeout=420)
    if not res.ok:
        return None
    data = read_json_output(out)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "ideas" in data:
        return data["ideas"]
    return None


@traced("opportunity_analyst")
def run() -> dict:
    rows = db.query(
        """SELECT * FROM trends WHERE id NOT IN
           (SELECT trend_id FROM story_ideas WHERE trend_id IS NOT NULL)
           ORDER BY fetched_at DESC LIMIT ?""",
        (config.MAX_CANDIDATES_PER_RUN * 3,),
    )
    scored = []
    for r in rows:
        score, breakdown, risky = _heuristic_score(r["title"], r["summary"] or "", r["source"])
        if risky:
            continue
        scored.append({**r, "hscore": score, "breakdown": breakdown})
    scored.sort(key=lambda x: -x["hscore"])
    candidates = [c for c in scored if not _already_covered(c["title"])][: config.MAX_CANDIDATES_PER_RUN]

    ideas = _devin_angle_pass(candidates) if candidates else None
    inserted = 0
    if ideas:
        for idea in ideas[: config.MAX_IDEAS_PER_RUN]:
            try:
                idx = int(idea["trend_index"]) - 1
                trend = candidates[idx]
            except (KeyError, IndexError, TypeError, ValueError):
                continue
            if float(idea.get("score", 0)) < config.MIN_IDEA_SCORE:
                continue
            db.run(
                """INSERT INTO story_ideas (id, trend_id, title, angle, category, scores_json, score, status, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,'new',?,?)""",
                (db.uid(), trend["id"], idea.get("title", trend["title"]),
                 idea.get("angle", ""), idea.get("category", DEFAULT_CATEGORY),
                 json.dumps(idea.get("scores", {})), float(idea.get("score", 0)),
                 db.now(), db.now()),
            )
            inserted += 1
    else:
        # Fallback: heuristic-only ideas, clearly marked for the writer.
        for c in candidates[: config.MAX_IDEAS_PER_RUN]:
            if c["hscore"] < config.MIN_IDEA_SCORE:
                continue
            db.run(
                """INSERT INTO story_ideas (id, trend_id, title, angle, category, scores_json, score, status, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,'new',?,?)""",
                (db.uid(), c["id"], c["title"],
                 f"Find the one absurd escalation inside this real story: {c['title']}",
                 _guess_category(f"{c['title']} {c['summary']}"),
                 json.dumps(c["breakdown"]), c["hscore"], db.now(), db.now()),
            )
            inserted += 1

    return {"detail": f"{inserted} story ideas from {len(candidates)} candidates", "ideas": inserted}
