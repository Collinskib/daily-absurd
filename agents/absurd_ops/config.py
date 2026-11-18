from __future__ import annotations

import os
from pathlib import Path

# Repo layout: <repo>/agents/absurd_ops/config.py -> repo root is parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = REPO_ROOT / "web"
ARTICLES_DIR = WEB_DIR / "content" / "articles"
ART_DIR = WEB_DIR / "public" / "art"
CATEGORIES_FILE = WEB_DIR / "content" / "categories.json"
QUEUE_DIR = REPO_ROOT / "agents" / "queue"
DRAFTS_DIR = QUEUE_DIR / "drafts"
REVIEWS_DIR = QUEUE_DIR / "reviews"
BRIEFS_DIR = QUEUE_DIR / "briefs"
SOCIAL_DIR = QUEUE_DIR / "social"
STATE_DIR = Path(os.environ.get("ABSURD_STATE_DIR", REPO_ROOT / "agents" / "state"))
DB_PATH = STATE_DIR / "absurd.db"

SITE_URL = os.environ.get("SITE_URL", "https://daily-absurd.vercel.app")
SITE_NAME = "The Daily Absurd"

# Devin is the editorial staff. Each call spawns a bounded non-interactive
# session; quality work (writer, editors) always goes through it.
DEVIN_BIN = os.environ.get("DEVIN_BIN", "devin")
DEVIN_TIMEOUT_SECONDS = int(os.environ.get("DEVIN_TIMEOUT_SECONDS", "900"))
DEVIN_PERMISSION_MODE = os.environ.get("DEVIN_PERMISSION_MODE", "accept-edits")
DEVIN_ENABLED = os.environ.get("ABSURD_DEVIN_ENABLED", "1") == "1"

# Daily targets — goals, not quotas. Quality overrides quantity.
MAX_CANDIDATES_PER_RUN = int(os.environ.get("ABSURD_MAX_CANDIDATES", "8"))
MAX_IDEAS_PER_RUN = int(os.environ.get("ABSURD_MAX_IDEAS", "5"))
MAX_ARTICLES_PER_RUN = int(os.environ.get("ABSURD_MAX_ARTICLES", "4"))
MIN_IDEA_SCORE = float(os.environ.get("ABSURD_MIN_IDEA_SCORE", "6.5"))
MIN_COMEDY_SCORE = float(os.environ.get("ABSURD_MIN_COMEDY_SCORE", "7.0"))
MAX_REWRITES = int(os.environ.get("ABSURD_MAX_REWRITES", "1"))

# Runs often fire seconds after boot (Persistent timer catch-up) before Wi-Fi
# is up. Wait this long for connectivity before giving up on the run.
NET_WAIT_SECONDS = int(os.environ.get("ABSURD_NET_WAIT_SECONDS", "300"))

GIT_REMOTE = os.environ.get("ABSURD_GIT_REMOTE", "origin")
GIT_BRANCH = os.environ.get("ABSURD_GIT_BRANCH", "main")
GIT_PUSH = os.environ.get("ABSURD_GIT_PUSH", "1") == "1"

# Traffic metrics — the growth analyst steers toward this many monthly
# readers. Vercel auth falls back to the local `vercel` CLI token.
MONTHLY_READER_TARGET = int(os.environ.get("ABSURD_READER_TARGET", "10000"))
VERCEL_TOKEN = os.environ.get("ABSURD_VERCEL_TOKEN") or os.environ.get("VERCEL_TOKEN", "")
VERCEL_PROJECT_ID = os.environ.get("ABSURD_VERCEL_PROJECT_ID", "")
VERCEL_TEAM_ID = os.environ.get("ABSURD_VERCEL_TEAM_ID", "")
# Google Search Console. Preferred auth: service-account JSON
# (ABSURD_GSC_SA_PATH — the shared claude-seo creds location is the
# default). Alternative: OAuth creds from `cli gsc-auth` (one-time flow).
GSC_SA_PATH = os.environ.get(
    "ABSURD_GSC_SA_PATH",
    str(Path.home() / ".config" / "claude-seo" / "service_account.json"),
)
GSC_SITE_URL = os.environ.get("ABSURD_GSC_SITE", "")
GSC_CLIENT_ID = os.environ.get("ABSURD_GSC_CLIENT_ID", "")
GSC_CLIENT_SECRET = os.environ.get("ABSURD_GSC_CLIENT_SECRET", "")
GSC_REFRESH_TOKEN = os.environ.get("ABSURD_GSC_REFRESH_TOKEN", "")

# Social posting (Agent 8 — social_poster). Opt-in: without ABSURD_SOCIAL_POST=1
# the agent dry-runs and posts nothing. Each channel activates when its pair
# of credentials is present. Posts go out as joke-text + link-in-self-reply.
SOCIAL_POST_ENABLED = os.environ.get("ABSURD_SOCIAL_POST", "0") == "1"
SOCIAL_MAX_PER_RUN = int(os.environ.get("ABSURD_SOCIAL_MAX_PER_RUN", "2"))
BSKY_PDS = os.environ.get("ABSURD_BSKY_PDS", "https://bsky.social")
BSKY_HANDLE = os.environ.get("ABSURD_BSKY_HANDLE", "")
BSKY_APP_PASSWORD = os.environ.get("ABSURD_BSKY_APP_PASSWORD", "")
MASTO_INSTANCE = os.environ.get("ABSURD_MASTO_INSTANCE", "")
MASTO_TOKEN = os.environ.get("ABSURD_MASTO_TOKEN", "")
THREADS_USER_ID = os.environ.get("ABSURD_THREADS_USER_ID", "")
THREADS_TOKEN = os.environ.get("ABSURD_THREADS_TOKEN", "")

DASHBOARD_HOST = os.environ.get("ABSURD_DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.environ.get("ABSURD_DASHBOARD_PORT", "8899"))

USER_AGENT = "DailyAbsurd/0.1 (+satirical publication research bot)"

for d in (STATE_DIR, DRAFTS_DIR, REVIEWS_DIR, BRIEFS_DIR, SOCIAL_DIR):
    d.mkdir(parents=True, exist_ok=True)
