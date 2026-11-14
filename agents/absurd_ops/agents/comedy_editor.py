"""Agent 4 — Comedy Editor (staffed by Devin).

Reviews each draft for jokes, structure and international readability.
Returns a verdict file; one rewrite is allowed per article.
"""
from __future__ import annotations

import time

from .. import config, db
from ..devin import run_session, read_json_output
from .base import traced


def _review(draft_path, draft: dict, review_out) -> None:
    prompt = config.BRIEFS_DIR / f"editor-{int(time.time())}-{draft['slug'][:30]}.md"
    prompt.write_text(f"""You are the COMEDY EDITOR of The Daily Absurd, an international
satirical news site. Review this draft article:

{draft['body']}

HEADLINE: {draft['headline']}
SUBHEADLINE: {draft['subheadline']}
ANGLE THE WRITER WAS GIVEN (see sourceEvent for the real event):
{draft['sourceEvent']}

Judge it against:
- Is the headline genuinely funny, not just descriptive?
- Does the opening create curiosity?
- Is the central comedic premise clear in one sentence?
- Does the humour escalate rather than repeat?
- Is there a real punchline at the end?
- Would an international reader (not just the US) get it?
- Would anyone share it?

Write a JSON object to {review_out}:
{{"verdict": "pass" | "rewrite" | "fail",
  "score": 0-10,
  "notes": "specific, actionable feedback",
  "rewrite_instructions": "what to change, or empty"}}

Be a hard editor. Below {config.MIN_COMEDY_SCORE} is rewrite or fail.
Write ONLY the JSON file.""")
    res = run_session(prompt, review_out, timeout=420)
    return read_json_output(review_out) if res.ok else None


def _rewrite(draft_path, draft: dict, instructions: str) -> dict | None:
    out = config.DRAFTS_DIR / f"{draft['slug']}.json"
    prompt = config.BRIEFS_DIR / f"rewrite-{int(time.time())}-{draft['slug'][:30]}.md"
    prompt.write_text(f"""You are the staff satirical writer for The Daily Absurd.
Your draft below was returned by the comedy editor with these notes:

{instructions}

CURRENT DRAFT:
{draft['body']}

Rewrite it funnier — keep the real event accurate, keep all safety rules
(fictional quotes only, no real-person quotes, no fake emergencies, no
punching down). Apply the editor's notes specifically.

Rewrite the ENTIRE JSON article file at {draft_path} in place — same schema,
same slug "{draft['slug']}", keep the social block but sharpen it too.
""")
    res = run_session(prompt, out, timeout=420)
    return read_json_output(out) if res.ok else None


@traced("comedy_editor")
def run() -> dict:
    drafts = db.query("SELECT * FROM drafts WHERE status='written'")
    reviewed = 0
    for d in drafts:
        draft = read_json_output(__import__("pathlib").Path(d["path"]))
        if not draft:
            continue
        review_out = config.REVIEWS_DIR / f"{d['slug']}-comedy.json"
        verdict = _review(d["path"], draft, review_out)
        if not verdict:
            db.run(
                "INSERT INTO reviews (id, draft_id, reviewer, verdict, notes, created_at) VALUES (?,?,?,?,?,?)",
                (db.uid(), d["id"], "comedy_editor", "error", "session failed", db.now()),
            )
            continue
        score = float(verdict.get("score", 0))
        v = verdict.get("verdict", "fail")
        db.run(
            "INSERT INTO reviews (id, draft_id, reviewer, verdict, score, notes, created_at) VALUES (?,?,?,?,?,?,?)",
            (db.uid(), d["id"], "comedy_editor", v, score,
             str(verdict.get("notes", ""))[:1500], db.now()),
        )
        db.run("UPDATE drafts SET comedy_score=?, updated_at=? WHERE id=?",
               (score, db.now(), d["id"]))
        if v == "pass" and score >= config.MIN_COMEDY_SCORE:
            db.run("UPDATE drafts SET status='comedy_ok', updated_at=? WHERE id=?",
                   (db.now(), d["id"]))
        elif v == "rewrite" and d["version"] <= config.MAX_REWRITES:
            new_draft = _rewrite(d["path"], draft, verdict.get("rewrite_instructions", ""))
            if new_draft:
                db.run("UPDATE drafts SET version=version+1, updated_at=? WHERE id=?",
                       (db.now(), d["id"]))
            else:
                db.run("UPDATE drafts SET status='rejected', updated_at=? WHERE id=?",
                       (db.now(), d["id"]))
        else:
            db.run("UPDATE drafts SET status='comedy_fail', updated_at=? WHERE id=?",
                   (db.now(), d["id"]))
        reviewed += 1
    return {"detail": f"{reviewed} drafts reviewed", "reviewed": reviewed}
