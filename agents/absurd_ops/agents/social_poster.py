"""Agent 8 — Social Poster.

Posts generated social packs to the configured channels (Bluesky, Mastodon,
Threads) once their article is deployed and verified live. The joke goes in
the post body; the article link goes in a self-reply so the main post isn't
throttled as an outbound-link post.

Every attempt is recorded in social_posts (unique per slug+channel), so runs
are idempotent and a failed channel retries next run. Channels with no
credentials are skipped. ABSURD_SOCIAL_POST=1 arms real posting; otherwise
the agent reports what it would have posted and touches nothing.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .. import config, db
from .base import traced

BSKY_CHAR_LIMIT = 280  # 300 graphemes; keep margin for the link reply
TEXT_LIMIT = 480       # Mastodon 500 / Threads 500, with margin


class PostError(RuntimeError):
    pass


def _api(url: str, payload: dict | None = None, form: dict | None = None,
         token: str | None = None, timeout: int = 20) -> dict:
    headers = {"User-Agent": config.USER_AGENT}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None:
        body = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode() or "{}"
            return json.loads(raw) if raw.strip().startswith(("{", "[")) else {"raw": raw}
    except urllib.error.HTTPError as e:
        raise PostError(f"HTTP {e.code} from {url}: {e.read().decode()[:300]}") from e
    except Exception as e:
        raise PostError(f"{url}: {e}") from e


# --- Bluesky ------------------------------------------------------------------

def _bsky_facets(text: str) -> list[dict]:
    """Link facets so URLs in the post render as real links."""
    return [
        {
            "index": {
                "byteStart": len(text[: m.start()].encode()),
                "byteEnd": len(text[: m.end()].encode()),
            },
            "features": [{"$type": "app.bsky.richtext.facet#link",
                          "uri": m.group(0)}],
        }
        for m in re.finditer(r"https?://\S+", text)
    ]


def _bsky_post(sess: dict, text: str, reply: dict | None = None) -> dict:
    record: dict = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": db.now(),
        "langs": ["en"],
        "facets": _bsky_facets(text),
    }
    if reply:
        record["reply"] = {"root": reply["root"], "parent": reply["parent"]}
    return _api(
        f"{config.BSKY_PDS}/xrpc/com.atproto.repo.createRecord",
        payload={"repo": sess["did"], "collection": "app.bsky.feed.post",
                 "record": record},
        token=sess["accessJwt"],
    )


def post_bluesky(text: str, url: str) -> tuple[str, str]:
    sess = _api(f"{config.BSKY_PDS}/xrpc/com.atproto.server.createSession",
                payload={"identifier": config.BSKY_HANDLE,
                         "password": config.BSKY_APP_PASSWORD})
    main = _bsky_post(sess, text[:BSKY_CHAR_LIMIT])
    ref = {"uri": main["uri"], "cid": main["cid"]}
    _bsky_post(sess, f"Full fabrication: {url}",
               reply={"root": ref, "parent": ref})
    return main["uri"], f"https://bsky.app/profile/{config.BSKY_HANDLE}/post/{main['uri'].rsplit('/', 1)[-1]}"


# --- Mastodon -----------------------------------------------------------------

def _masto(text: str, reply_to: str | None = None) -> dict:
    payload: dict = {"status": text, "visibility": "public"}
    if reply_to:
        payload["in_reply_to_id"] = reply_to
    return _api(f"{config.MASTO_INSTANCE.rstrip('/')}/api/v1/statuses",
                payload=payload, token=config.MASTO_TOKEN)


def post_mastodon(text: str, url: str) -> tuple[str, str]:
    main = _masto(text[:TEXT_LIMIT])
    _masto(f"Full fabrication: {url}", reply_to=main["id"])
    return str(main["id"]), main.get("url", "")


# --- Threads ------------------------------------------------------------------

def _threads_container(text: str, reply_to: str | None = None) -> str:
    form = {"media_type": "TEXT", "text": text,
            "access_token": config.THREADS_TOKEN}
    if reply_to:
        form["reply_to_id"] = reply_to
    res = _api(f"https://graph.threads.net/v1.0/{config.THREADS_USER_ID}/threads",
               form=form)
    return res["id"]


def _threads_publish(container_id: str) -> str:
    res = _api(
        f"https://graph.threads.net/v1.0/{config.THREADS_USER_ID}/threads_publish",
        form={"creation_id": container_id,
              "access_token": config.THREADS_TOKEN})
    return res["id"]


def post_threads(text: str, url: str) -> tuple[str, str]:
    post_id = _threads_publish(_threads_container(text[:TEXT_LIMIT]))
    time.sleep(3)  # the container needs a beat before it accepts replies
    _threads_publish(_threads_container(f"Full fabrication: {url}",
                                        reply_to=post_id))
    return post_id, f"https://www.threads.net/t/{post_id}"


# --- Orchestration ------------------------------------------------------------

def _channels() -> dict[str, tuple]:
    out = {}
    if config.BSKY_HANDLE and config.BSKY_APP_PASSWORD:
        out["bluesky"] = post_bluesky
    if config.MASTO_INSTANCE and config.MASTO_TOKEN:
        out["mastodon"] = post_mastodon
    if config.THREADS_USER_ID and config.THREADS_TOKEN:
        out["threads"] = post_threads
    return out


def _post_text(pack: dict) -> str:
    """Joke copy without the URL line the pack appends for manual posting."""
    text = (pack.get("x") or "").replace(pack.get("url", "\x00"), "").strip()
    return text


@traced("social_poster")
def run() -> dict:
    channels = _channels()
    rows = db.query(
        """SELECT slug, url FROM published
           WHERE deployed = 1
           ORDER BY published_at DESC LIMIT ?""",
        (config.SOCIAL_MAX_PER_RUN,),
    )
    posted = failed = skipped = 0
    for row in rows:
        pack_path = config.SOCIAL_DIR / f"{row['slug']}.json"
        if not pack_path.exists():
            continue
        try:
            pack = json.loads(Path(pack_path).read_text())
        except json.JSONDecodeError:
            continue
        text = _post_text(pack)
        url = pack.get("url") or row["url"]
        if not text or not url:
            continue
        for channel, fn in channels.items():
            if db.one(
                "SELECT id FROM social_posts WHERE slug=? AND channel=? AND status='posted'",
                (row["slug"], channel),
            ):
                continue
            if not config.SOCIAL_POST_ENABLED:
                skipped += 1
                continue
            try:
                remote_id, remote_url = fn(text, url)
                db.run(
                    "INSERT OR REPLACE INTO social_posts (id, slug, channel, status, remote_id, remote_url, error, created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (db.uid(), row["slug"], channel, "posted", remote_id, remote_url, None, db.now()),
                )
                posted += 1
            except Exception as e:
                db.run(
                    "INSERT OR REPLACE INTO social_posts (id, slug, channel, status, remote_id, remote_url, error, created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (db.uid(), row["slug"], channel, "failed", None, None, str(e)[:500], db.now()),
                )
                failed += 1
            time.sleep(2)  # stay polite; the pipeline runs on a timer anyway
    mode = "dry-run" if not config.SOCIAL_POST_ENABLED else "live"
    detail = (f"{posted} posts sent, {failed} failed, {skipped} pending "
              f"({mode}; channels: {', '.join(channels) or 'none configured'})")
    return {"detail": detail, "posted": posted, "failed": failed,
            "skipped": skipped, "channels": list(channels)}
