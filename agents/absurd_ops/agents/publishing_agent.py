"""Agent 8 — Publishing Agent.

Moves approved drafts into the site content tree, generates art, commits and
pushes (which triggers the Vercel deployment), then verifies the article URL
is reachable. Dedupes on slug — an article is never published twice.
"""
from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from pathlib import Path

from .. import config, db
from ..art import ensure_art
from .base import traced


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=config.REPO_ROOT,
        capture_output=True, text=True, check=check,
    )


def _verify_url(url: str, attempts: int = 12, delay: int = 15) -> bool:
    for _ in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(delay)
    return False


@traced("publishing_agent")
def run() -> dict:
    drafts = db.query("SELECT * FROM drafts WHERE status='approved' ORDER BY created_at LIMIT ?",
                      (config.MAX_ARTICLES_PER_RUN,))
    published = []
    for d in drafts:
        slug = d["slug"]
        if db.one("SELECT id FROM published WHERE slug=?", (slug,)):
            db.run("UPDATE drafts SET status='published', updated_at=? WHERE id=?",
                   (db.now(), d["id"]))
            continue
        try:
            draft = json.loads(Path(d["path"]).read_text())
        except (OSError, json.JSONDecodeError):
            continue
        draft["art"] = ensure_art(slug, draft["category"], draft["headline"], draft.get("art"))
        target = config.ARTICLES_DIR / f"{slug}.json"
        db.write_json(target, draft)

        sha = ""
        if config.GIT_PUSH:
            _git("add", str(target.relative_to(config.REPO_ROOT)),
                 str(config.ART_DIR.relative_to(config.REPO_ROOT)), check=False)
            commit = _git(
                "-c", "user.name=Daily Absurd Bot",
                "-c", "user.email=bot@dailyabsurd.news",
                "commit", "-m", f"publish: {draft['headline'][:72]}", check=False)
            if commit.returncode == 0:
                push = _git("push", config.GIT_REMOTE, config.GIT_BRANCH, check=False)
                if push.returncode != 0:
                    db.run(
                        "UPDATE drafts SET updated_at=? WHERE id=?", (db.now(), d["id"]))
                    continue
                sha = _git("rev-parse", "HEAD", check=False).stdout.strip()

        url = f"{config.SITE_URL}/articles/{slug}"
        deployed = _verify_url(url) if config.GIT_PUSH else False
        db.run(
            """INSERT INTO published (id, draft_id, slug, url, commit_sha, deployed, published_at)
               VALUES (?,?,?,?,?,?,?)""",
            (db.uid(), d["id"], slug, url, sha, 1 if deployed else 0, db.now()),
        )
        db.run("UPDATE drafts SET status='published', updated_at=? WHERE id=?",
               (db.now(), d["id"]))
        published.append({"slug": slug, "url": url, "deployed": deployed})
    return {"detail": f"{len(published)} articles published", "published": published}
